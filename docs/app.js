// ============================================================================
// app.js  —  shared logic for the static GitHub Pages version
// ----------------------------------------------------------------------------
// Uses Firebase Firestore (shared token store) and EmailJS (email sending).
// The Firebase compat SDK and EmailJS SDK are loaded from a CDN in each page.
// ============================================================================

// ---- Initialise Firebase ----
let db = null;
let firebaseReady = false;
try {
  firebase.initializeApp(FIREBASE_CONFIG);
  db = firebase.firestore();
  firebaseReady = true;
} catch (e) {
  console.error("Firebase init failed:", e);
}

// ---- Initialise EmailJS ----
let emailjsReady = false;
try {
  emailjs.init({ publicKey: EMAILJS_PUBLIC_KEY });
  emailjsReady = true;
} catch (e) {
  console.error("EmailJS init failed:", e);
}

const TOKENS = "tokens";

// ---- Helpers ----

// Generate a URL-safe random token.
function makeToken() {
  const bytes = new Uint8Array(18);
  crypto.getRandomValues(bytes);
  let s = btoa(String.fromCharCode.apply(null, bytes));
  return s.replace(/\+/g, "-").replace(/\//g, "_").replace(/=/g, "");
}

function nowISO() {
  return new Date().toISOString();
}

// Small UI helper: show a message box.
function showMessage(elId, kind, html) {
  const el = document.getElementById(elId);
  if (!el) return;
  el.className = "msg " + kind;
  el.innerHTML = html;
  el.style.display = "block";
}

function hide(elId) {
  const el = document.getElementById(elId);
  if (el) el.style.display = "none";
}

function configMissing() {
  return (
    !firebaseReady ||
    FIREBASE_CONFIG.projectId.indexOf("PASTE_") === 0 ||
    EMAILJS_SERVICE_ID.indexOf("PASTE_") === 0
  );
}

// ---- Issue a token (professor) ----
async function issueToken(studentName, studentEmail, professorEmail, quizId) {
  const token = makeToken();
  await db.collection(TOKENS).doc(token).set({
    student_name: studentName,
    student_email: studentEmail,
    professor_email: professorEmail,
    quiz_id: quizId,
    used: false,
    created_at: nowISO(),
    used_at: null
  });
  return token;
}

// ---- Check a token without spending it ----
async function checkToken(token) {
  const snap = await db.collection(TOKENS).doc(token).get();
  if (!snap.exists) return { valid: false, message: "Token not found.", data: null };
  const d = snap.data();
  if (d.used) {
    return { valid: false, message: "This token was already used on " + d.used_at + ".", data: d };
  }
  return { valid: true, message: "Token is valid and unused.", data: d };
}

// ---- Redeem a token (student): email FIRST, then mark used ----
async function redeemToken(token) {
  // 1. Read + verify (no spend yet).
  const snap = await db.collection(TOKENS).doc(token).get();
  if (!snap.exists) return { ok: false, message: "Token not found." };
  const d = snap.data();
  if (d.used) return { ok: false, message: "This token was already used on " + d.used_at + "." };

  // 2. Send the email FIRST. If it fails, the token stays valid.
  try {
    await emailjs.send(EMAILJS_SERVICE_ID, EMAILJS_TEMPLATE_ID, {
      to_email: d.professor_email,
      professor_email: d.professor_email,
      student_name: d.student_name,
      student_email: d.student_email,
      quiz_id: d.quiz_id,
      request_time: nowISO()
    });
  } catch (e) {
    console.error("EmailJS send failed:", e);
    return { ok: false, message: "Could not send the email. Your token was NOT used - please try again." };
  }

  // 3. Email sent. Now mark used in a transaction so it can only happen once.
  try {
    await db.runTransaction(async (tx) => {
      const ref = db.collection(TOKENS).doc(token);
      const s = await tx.get(ref);
      if (!s.exists) throw new Error("not found");
      if (s.data().used) throw new Error("already used");
      tx.update(ref, { used: true, used_at: nowISO() });
    });
  } catch (e) {
    // Extremely rare: someone redeemed it in the split second after our check.
    return { ok: false, message: "This token was already used." };
  }

  return { ok: true, professor_email: d.professor_email, quiz_id: d.quiz_id };
}
