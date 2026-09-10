import argparse
from dotenv import load_dotenv

import token_manager
import emailer

load_dotenv()


def cmd_issue(args):
    token = token_manager.issue(
        student_name=args.student_name,
        student_email=args.student_email,
        professor_email=args.professor_email,
        quiz_id=args.quiz_id,
    )
    print("\nToken issued successfully.")
    print("Give this token to the student. It can be used only once:\n")
    print(f"    {token}\n")


def cmd_verify(args):
    is_valid, message, row = token_manager.verify(args.token)
    print(f"\nValid : {is_valid}")
    print(f"Status: {message}")
    if row:
        print(f"Student : {row['student_name']} <{row['student_email']}>")
        print(f"Quiz    : {row['quiz_id']}")
    print()


def cmd_redeem(args):
    is_valid, message, row = token_manager.verify(args.token)
    if not is_valid:
        print(f"\nRedeem failed: {message}\n")
        return

    sent, email_message = emailer.send_makeup_request(row)
    if not sent:
        print(f"\nEmail failed: {email_message}")
        print(
            "\nThe token was NOT used — it is still valid. "
            "Fix your .env settings and run redeem again.\n"
        )
        return

    success, spend_message, row = token_manager.redeem(args.token)
    if not success:
        print(f"\n{email_message}")
        print(f"\nNote: {spend_message}\n")
        return

    print(f"\n{email_message}")
    print("Token redeemed successfully.")
    print("\nDone. The professor has been notified.\n")


def build_parser():
    parser = argparse.ArgumentParser(
        description="One-time quiz make-up token system."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_issue = subparsers.add_parser("issue", help="Create a new one-time token.")
    p_issue.add_argument("--student-name", required=True)
    p_issue.add_argument("--student-email", required=True)
    p_issue.add_argument("--professor-email", required=True)
    p_issue.add_argument("--quiz-id", required=True)
    p_issue.set_defaults(func=cmd_issue)

    p_verify = subparsers.add_parser("verify", help="Check a token without spending it.")
    p_verify.add_argument("--token", required=True)
    p_verify.set_defaults(func=cmd_verify)

    p_redeem = subparsers.add_parser("redeem", help="Spend a token and email the professor.")
    p_redeem.add_argument("--token", required=True)
    p_redeem.set_defaults(func=cmd_redeem)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()