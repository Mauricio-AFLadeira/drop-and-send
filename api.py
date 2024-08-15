import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from flask import Flask, request, jsonify, send_file, send_from_directory
import re
import random

app = Flask(__name__)
output_dir = 'output'
os.makedirs(output_dir, exist_ok=True)

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'csv_file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado.'}), 400

    file = request.files['csv_file']
    if file and file.filename.endswith('.csv'):
        df = pd.read_csv(file)
        data_column = df.columns[0]
        df[data_column] = df[data_column].str.replace(',', '.')
        df[data_column] = pd.to_numeric(df[data_column], errors='coerce')
        df[data_column] = df[data_column].fillna(df[data_column].mean())

        # Gerando um número aleatório de 4 dígitos
        random_number = random.randint(1000, 9999)
        pdf_filename = f"analise_{data_column}_{random_number}.pdf"
        pdf_path = os.path.join(output_dir, pdf_filename)

        with PdfPages(pdf_path) as pdf:
            plt.figure()
            plt.hist(df[data_column], bins=100, density=True, rwidth=0.8, color='blue')
            plt.xlabel('Segundos')
            plt.ylabel(data_column)
            plt.title(f'Histograma de {data_column}')
            pdf.savefig()

        return jsonify({'pdf_file': pdf_filename})
    else:
        return jsonify({'error': 'Por favor, envie um arquivo CSV válido.'}), 400

@app.route('/send_email', methods=['POST'])
def send_email():
    email_to = request.form.get('to_email')
    pdf_filename = request.form.get('pdf_file')

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email_to):
        return jsonify({'error': 'Endereço de e-mail inválido.'}), 400

    FROM_EMAIL = "tccmauricioafl@outlook.com"
    PASSWORD = "2PEE%.k!xCWC8-Y"
    HOST = "smtp-mail.outlook.com"
    PORT = 587
    TO_EMAIL = email_to
    pdf_path = os.path.join(output_dir, pdf_filename)

    msg = MIMEMultipart()
    msg['From'] = FROM_EMAIL
    msg['To'] = TO_EMAIL
    msg['Subject'] = "Histograma gerado"
    msg.attach(MIMEText("Segue em anexo o histograma gerado.", 'plain'))

    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as attachment:
            part = MIMEBase('application', 'pdf')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(pdf_path)}')
            msg.attach(part)
    else:
        return jsonify({'error': 'Arquivo PDF não encontrado.'}), 400

    try:
        smtp = smtplib.SMTP(HOST, PORT)
        smtp.ehlo()
        smtp.starttls()
        smtp.login(FROM_EMAIL, PASSWORD)
        smtp.sendmail(FROM_EMAIL, TO_EMAIL, msg.as_string())
        smtp.quit()
        return jsonify({'success': 'E-mail enviado com sucesso!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/output/<path:filename>')
def download_file(filename):
    return send_from_directory(output_dir, filename)

if __name__ == '__main__':
    app.run(debug=True)
