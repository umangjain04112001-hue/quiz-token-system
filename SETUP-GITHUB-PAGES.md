# Setup Guide - GitHub Pages version

This version runs entirely on GitHub Pages (no Render). It uses two free
services for the parts a static site can't do on its own:

- **Firebase (Firestore)** - the shared database that stores tokens and enforces one-time use.
- **EmailJS** - sends the make-up request email to the professor.

You set up both once, paste their values into `docs/config.js`, and enable
GitHub Pages. ~20 minutes.

---

## Part 1 - Firebase (the token database)

1. Go to https://console.firebase.google.com and sign in with your Google account.
2. Click **Add project**. Give it a name (e.g. `quiz-token-system`). You can skip
   Google Analytics. Click through until the project is created.
3. On the project home, click the **web icon** `</>` ("Add app to get started").
   - App nickname: `quiz-token-web`. Do NOT check "Firebase Hosting".
   - Click **Register app**.
4. Firebase shows a `firebaseConfig` block with values like `apiKey`, `projectId`,
   etc. **Keep this screen open** - these go into `config.js`.
5. In the left menu, click **Build -> Firestore Database -> Create database**.
   - Choose a location (any), and start in **production mode**. Click Enable.
6. Open the **Rules** tab in Firestore and replace everything with this, then
   click **Publish**:

   ```
   rules_version = '2';
   service cloud.firestore {
     match /databases/{database}/documents {
       match /tokens/{token} {
         allow read, create, update: if true;
         allow delete: if false;
       }
     }
   }
   ```

   (This lets the site read/create/update tokens. It's open, which matches this
   tool's purpose - a convenience tracker, not a security system.)

---

## Part 2 - EmailJS (sends the email)

1. Go to https://www.emailjs.com and create a free account.
2. **Add an email service:** dashboard -> **Email Services -> Add New Service ->
   Gmail -> Connect Account** (sign in with the Gmail that will send the mail).
   After connecting, note the **Service ID** (looks like `service_xxxxxxx`).
3. **Create a template:** **Email Templates -> Create New Template**.
   - In the template settings, set **To Email** to:  `{{to_email}}`
   - Set the **Subject** to:  `Quiz Make-Up Request - Quiz {{quiz_id}}`
   - Set the **Content** to:

     ```
     A student who missed a quiz has submitted a make-up request.

     Student name : {{student_name}}
     Student email: {{student_email}}
     Quiz ID      : {{quiz_id}}
     Request time : {{request_time}}

     Please reply to the student at {{student_email}} to arrange the make-up.
     ```
   - Save it, and note the **Template ID** (looks like `template_xxxxxxx`).
4. Get your **Public Key:** dashboard -> **Account -> General -> Public Key**.

---

## Part 3 - Put the values into config.js

Open `docs/config.js` and replace every `PASTE_...` placeholder:

- From Firebase (step 1.4): `apiKey`, `authDomain`, `projectId`, `storageBucket`,
  `messagingSenderId`, `appId`.
- From EmailJS: `EMAILJS_PUBLIC_KEY`, `EMAILJS_SERVICE_ID`, `EMAILJS_TEMPLATE_ID`.

(If you give these values to Claude, it can paste them in for you.)

---

## Part 4 - Enable GitHub Pages

1. Push the project to GitHub (the `docs/` folder must be included).
2. On GitHub, open your repo -> **Settings -> Pages**.
3. Under **Build and deployment -> Source**, choose **Deploy from a branch**.
4. Branch: **main**, folder: **/docs**. Click **Save**.
5. Wait 1-2 minutes. GitHub shows your live URL, like:
   `https://YOUR_USERNAME.github.io/quiz-token-system/`

That URL is the website to send your professor.

---

## Notes

- Firebase config values are **not** passwords - they're public client keys, which
  is normal for a website. Access is controlled by the Firestore rules above.
- Both free tiers are far more than a class project needs.
- The one-time-use guarantee is enforced by a Firestore transaction when a token
  is redeemed, so a token can never be used twice.
