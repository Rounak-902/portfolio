from flask import Flask, request, render_template, redirect, url_for
import mysql.connector
from mysql.connector import Error
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Database configuration
db_config = {
    'host': os.getenv("DB_HOST"),
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASS"),
    'database': os.getenv("DB_NAME")
}

# Email configuration
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

def send_notification(name, email, subject, message):
    msg = EmailMessage()
    msg['Subject'] = f'New Contact Form Submission: {subject}'
    msg['From'] = EMAIL_USER
    msg['To'] = ADMIN_EMAIL

    body = f"""
    You have received a new message from your portfolio website:

    Name: {name}
    Email: {email}
    Subject: {subject}
    Message:
    {message}
    """

    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)
    except Exception as e:
        print(f"Email sending failed: {e}")

def insert_into_db(name, email, subject, message):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Create table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                email VARCHAR(100),
                subject VARCHAR(200),
                message TEXT,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Insert submission
        cursor.execute("""
            INSERT INTO contacts (name, email, subject, message)
            VALUES (%s, %s, %s, %s)
        """, (name, email, subject, message))

        connection.commit()
    except Error as e:
        print(f"Database error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route("/")
def home():
    return render_template("index.html")  # Ensure index.html is in the 'templates/' folder

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name")
    email = request.form.get("email")
    subject = request.form.get("subject")
    message = request.form.get("message")

    insert_into_db(name, email, subject, message)
    send_notification(name, email, subject, message)

    return redirect(url_for("thank_you"))  # Optionally redirect to a thank-you page

@app.route('/thankyou')
def thank_you():
    return render_template("thankyou.html")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=3000)