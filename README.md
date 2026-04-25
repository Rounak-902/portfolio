# Raunak's Portfolio

A personal portfolio website built with **Flask** and deployed via **Gunicorn**.

---

## Features

- Responsive single-page design
- Contact form that delivers messages via Gmail SMTP
- Thank-you page on successful submission
- Flash messages for validation / error feedback

---

## Local development

### 1 – Prerequisites

- Python 3.8+
- `pip`

### 2 – Install dependencies

```bash
pip install -r requirements.txt
```

### 3 – Configure environment variables

Copy the example file and fill in your own values:

```bash
cp .env.example .env
# then edit .env
```

Required variables:

| Variable     | Description |
|--------------|-------------|
| `SECRET_KEY` | Flask session secret key – use a long random string in production |
| `EMAIL_USER` | Gmail address used to authenticate with the SMTP server |
| `EMAIL_PASS` | Gmail **App Password** (see note below) |
| `ADMIN_EMAIL`| Address that receives contact-form submissions |

Optional variables:

| Variable      | Default            | Description |
|---------------|--------------------|-------------|
| `EMAIL_FROM`  | same as `EMAIL_USER` | From address shown in outgoing email. **Must match `EMAIL_USER`** when using Gmail SMTP unless the address is a verified Gmail alias. |
| `SMTP_SERVER` | `smtp.gmail.com`   | SMTP host |
| `SMTP_PORT`   | `587`              | SMTP port (587 = STARTTLS, 465 = SSL) |

> **Gmail App Password**  
> Gmail no longer allows sign-in with your regular password for SMTP.  
> 1. Enable **2-Step Verification** on your Google Account.  
> 2. Go to <https://myaccount.google.com/apppasswords> and create an App Password.  
> 3. Use that 16-character password as `EMAIL_PASS`.

### 4 – Run

```bash
python app.py
# or with gunicorn:
gunicorn app:app --bind 0.0.0.0:3000
```

The site is available at <http://localhost:3000>.

---

## Deployment notes

- Set all environment variables (from the table above) in your hosting platform's dashboard rather than committing a `.env` file.
- Use a strong, unique `SECRET_KEY` in production.
- Make sure outbound SMTP port **587** (or **465**) is not blocked by your hosting provider. Some free-tier platforms block outbound SMTP; in that case use a transactional email API (e.g. SendGrid, Mailgun) instead.

---

## Project structure

```
portfolio/
├── app.py              # Flask application
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
├── templates/
│   ├── index.html      # Main single-page portfolio
│   └── thankyou.html   # Post-submission confirmation page
└── static/
    ├── style.css       # Global stylesheet
    ├── profile.jpg     # Profile photo
    └── resume.pdf      # Downloadable résumé
```
