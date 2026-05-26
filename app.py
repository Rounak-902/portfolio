from flask import Flask, request, render_template, redirect, url_for, flash

import smtplib
from email.message import EmailMessage

import os
import re  # For email format validation

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
secret_key = os.getenv("SECRET_KEY")
if not secret_key:
    secret_key = os.urandom(32)
app.secret_key = secret_key

# Email configuration
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
# EMAIL_FROM must match the authenticated Gmail account; fall back to EMAIL_USER
EMAIL_FROM = os.getenv("EMAIL_FROM") or EMAIL_USER
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")

try:
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
except (ValueError, TypeError):
    SMTP_PORT = 587


def send_notification(name, email, subject, message):
    """Send email notification"""
    try:
        if not all([EMAIL_USER, EMAIL_PASS, ADMIN_EMAIL]):
            print("Email configuration is incomplete!")
            return False

        # Sanitize subject to remove line breaks
        sanitized_subject = re.sub(r"[\r\n]+", " ", subject or "No subject")

        msg = EmailMessage()
        msg["Subject"] = f"New Contact Form Submission: {sanitized_subject}"
        msg["From"] = EMAIL_FROM
        msg["To"] = ADMIN_EMAIL
        msg["Reply-To"] = email

        body = (
            "You have received a new message from your portfolio website:\n\n"
            f"Name: {name}\n"
            f"Email: {email}\n"
            f"Subject: {subject}\n\n"
            "Message:\n"
            f"{message}\n"
        )

        msg.set_content(body)

        if SMTP_PORT == 465:
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
                smtp.login(EMAIL_USER, EMAIL_PASS)
                smtp.send_message(msg)
        else:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
                smtp.login(EMAIL_USER, EMAIL_PASS)
                smtp.send_message(msg)

        print(f"[SUCCESS] Email sent successfully to {ADMIN_EMAIL}")
        return True

    except smtplib.SMTPAuthenticationError:
        print("✗ Email authentication failed. Check EMAIL_USER / EMAIL_PASS.")
        return False
    except smtplib.SMTPException as e:
        print(f"✗ SMTP error: {e}")
        return False
    except OSError as e:
        print(f"✗ Network error sending email: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Email sending failed: {e}")
        return False


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():
    try:
        # Get form data
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()

        print("\n--- New Form Submission ---")
        print(f"Name: {name.encode('ascii', 'replace').decode('ascii')}")
        print(f"Email: {email.encode('ascii', 'replace').decode('ascii')}")
        print(f"Subject: {subject.encode('ascii', 'replace').decode('ascii')}")
        print(f"Message: {message[:50].encode('ascii', 'replace').decode('ascii')}...")

        # Validate required fields
        if not name or not email or not message:
            print("[ERROR] Validation failed: Missing required fields")
            flash("Please fill in all required fields.", "error")
            return redirect(url_for("home") + "#contact")

        # Validate email format
        email_pattern = r"^[\w\.\+\-]+@[\w\.-]+\.\w+$"
        if not re.match(email_pattern, email):
            print("[ERROR] Validation failed: Invalid email format")
            flash("Please enter a valid email address.", "error")
            return redirect(url_for("home") + "#contact")

        # Enforce reasonable length limits
        if len(name) > 200 or len(email) > 254 or len(subject) > 300 or len(message) > 5000:
            flash("One or more fields exceed the maximum allowed length.", "error")
            return redirect(url_for("home") + "#contact")

        email_success = send_notification(name, email, subject, message)

        if email_success:
            print("[SUCCESS] Form submission successful!")
            return redirect(url_for("thank_you"))
        else:
            print("[ERROR] Email sending failed")
            flash("There was an error sending your message. Please try again or contact me directly.", "error")
            return redirect(url_for("home") + "#contact")

    except Exception as e:
        print(f"[ERROR] Unexpected error in submit route: {e}")
        import traceback
        traceback.print_exc()
        flash("An unexpected error occurred. Please try again later.", "error")
        return redirect(url_for("home") + "#contact")


@app.route("/thankyou")
def thank_you():
    return render_template("thankyou.html")


if __name__ == "__main__":
    print("\n=== Flask App Starting ===")
    print(f"Email User: {EMAIL_USER}")
    print(f"Email From: {EMAIL_FROM}")
    print(f"Admin Email: {ADMIN_EMAIL}")
    print(f"SMTP Server: {SMTP_SERVER}")
    print(f"SMTP Port: {SMTP_PORT}")
    print("========================\n")
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
            host="0.0.0.0", port=int(os.getenv("PORT", "3000")))
