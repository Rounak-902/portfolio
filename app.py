from flask import Flask, request, render_template, redirect, url_for, flash
import mysql.connector
# from mysql.connector import Error
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

# Database configuration
# db_config = {
#     'host': os.getenv("DB_HOST", "localhost"),
#     'user': os.getenv("DB_USER", "root"),
#     'password': os.getenv("DB_PASS", ""),
#     'database': os.getenv("DB_NAME", "portfolio_db")
# }

# Email configuration
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_FROM = os.getenv("EMAIL_FROM", EMAIL_USER)  # Use EMAIL_FROM if provided, else EMAIL_USER
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

def send_notification(name, email, subject, message):
    """Send email notification"""
    try:
        if not all([EMAIL_USER, EMAIL_PASS, ADMIN_EMAIL]):
            print("Email configuration is incomplete!")
            return False

        msg = EmailMessage()
        msg['Subject'] = f'New Contact Form Submission: {subject}'
        msg['From'] = EMAIL_FROM  # Will show as raunakportfolio@outlook.com
        msg['To'] = ADMIN_EMAIL
        msg['Reply-To'] = email

        body = f"""
You have received a new message from your portfolio website:

Name: {name}
Email: {email}
Subject: {subject}

Message:
{message}
        """

        msg.set_content(body)

        # Use SMTP_SSL for port 465 (Gmail), SMTP with STARTTLS for port 587 (Gmail/Outlook)
        if SMTP_PORT == 465:
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
                smtp.login(EMAIL_USER, EMAIL_PASS)
                smtp.send_message(msg)
        else:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
                smtp.starttls()
                smtp.login(EMAIL_USER, EMAIL_PASS)
                smtp.send_message(msg)
        
        print(f"✓ Email sent successfully to {ADMIN_EMAIL}")
        return True
    except Exception as e:
        print(f"✗ Email sending failed: {e}")
        return False

# def insert_into_db(name, email, subject, message):
    """Insert contact form data into database"""
    connection = None
    cursor = None
    try:
        print(f"Connecting to database: {db_config['database']} at {db_config['host']}")
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Create table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cont (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL,
                subject VARCHAR(200),
                message TEXT,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Insert submission
        cursor.execute("""
            INSERT INTO cont (name, email, subject, message)
            VALUES (%s, %s, %s, %s)
        """, (name, email, subject, message))

        connection.commit()
        print(f"✓ Data inserted successfully for {name}")
        return True
    except Error as e:
        print(f"✗ Database error: {e}")
        if connection:
            connection.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

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

        print(f"\n--- New Form Submission ---")
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Subject: {subject}")
        print(f"Message: {message[:50]}...")

        # Validate required fields
        if not name or not email or not message:
            print("✗ Validation failed: Missing required fields")
            flash("Please fill in all required fields.", "error")
            return redirect(url_for("home"))

        # Try to insert into database
        # db_success = insert_into_db(name, email, subject, message)
        
        # Try to send email notification
        email_success = send_notification(name, email, subject, message)

        # Check results
        if email_success:
            print("✓ Form submission successful!")
            return redirect(url_for("thank_you"))
        # elif db_success or email_success:
        #     print("⚠ Partial success (check logs above)")
        #     return redirect(url_for("thank_you"))
        else:
            print("✗ email failed")
            flash("There was an error submitting your form. Please try again.", "error")
            return redirect(url_for("home"))

    except Exception as e:
        print(f"✗ Unexpected error in submit route: {e}")
        import traceback
        traceback.print_exc()
        flash("An unexpected error occurred. Please try again later.", "error")
        return redirect(url_for("home"))

@app.route('/thankyou')
def thank_you():
    return render_template("thankyou.html")

if __name__ == "__main__":
    print("\n=== Flask App Starting ===")
    # print(f"Database Host: {db_config['host']}")
    # print(f"Database Name: {db_config['database']}")
    # print(f"Database User: {db_config['user']}")
    print(f"Email User: {EMAIL_USER}")
    print(f"Email From: {EMAIL_FROM}")
    print(f"Admin Email: {ADMIN_EMAIL}")
    print(f"SMTP Server: {SMTP_SERVER}")
    print(f"SMTP Port: {SMTP_PORT}")
    print("========================\n")
    app.run(debug=True, host='0.0.0.0', port=3000)