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
from statistics_algorithm import generate_statistics, plot_graphics, analyze_normality_stationarity, smoothing_and_modeling, train_neural_network

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
            statistics = generate_statistics(df, data_column)
            stats_text = '\n'.join([f'{stat}: {value:.2f}' for stat, value in statistics.items()])
            plt.gcf().text(0.15, 0.6, stats_text, fontsize=10, bbox=dict(facecolor='white', alpha=0.5))
            pdf.savefig()

            plot_graphics(df, data_column, pdf)

            normality_stationarity = analyze_normality_stationarity(df, data_column)
            ns_text = f"Shapiro-Wilk: {normality_stationarity['shapiro_stat']:.2f}, {normality_stationarity['shapiro_p_value']:.2f}\n"
            ns_text += f"KPSS: {normality_stationarity['kpss_stat']:.2f}, {normality_stationarity['kpss_p_value']:.2f}"
            plt.gcf().text(0.15, 0.6, ns_text, fontsize=10, bbox=dict(facecolor='white', alpha=0.5))
            pdf.savefig()

            smoothing_and_modeling(df, data_column, pdf)

            train_neural_network(df, data_column, pdf)

        return jsonify({'pdf_file': pdf_filename})
    else:
        return jsonify({'error': 'Por favor, envie um arquivo CSV válido.'}), 400

@app.route('/send_email', methods=['POST'])
def send_email():
    email_to = request.form.get('to_email')
    pdf_filename = request.form.get('pdf_file')
    email_subject = request.form.get('email_subject')
    email_body = request.form.get('email_body')

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
    msg['Subject'] = email_subject  # Use o assunto enviado pelo usuário
    msg.attach(MIMEText(email_body, 'plain'))  # Use o corpo do e-mail enviado pelo usuário

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
