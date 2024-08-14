import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_pdf import PdfPages
import smtplib
import getpass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)

class CSVDragDropWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        # Configurações da janela
        self.setWindowTitle('Selecione o Arquivo CSV')
        self.setGeometry(100, 100, 900, 600)
        self.setStyleSheet("background-color: #C2DFE3;")  # Cor de fundo

        # Layout principal
        self.layout = QVBoxLayout()
        
        # Label para instruções
        self.label = QLabel('ARRASTE E ENVIE', self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont('Arial', 20, QFont.Bold))
        self.label.setStyleSheet("""
            color: #253237;                   
            margin-bottom: 20px;     
        """)
        self.layout.addWidget(self.label)
        
        # Label para área de arrastar e soltar
        self.drop_label = QLabel(self)
        self.drop_label.setAlignment(Qt.AlignCenter)
        self.drop_label.setFont(QFont('Arial', 14))
        self.drop_label.setText("ARRASTE SEU ARQUIVO")
        self.drop_label.setStyleSheet("""
            border: 2px dashed #9db4c0;
            color: #333333;                     
            min-width: 400px;                                      
            min-height: 400px;                          
            background-color: #E0FBFC;
            border-radius: 10px;
        """)
        self.layout.addWidget(self.drop_label)
        
        # Layout para os botões
        button_layout = QHBoxLayout()
        
        # Botão para abrir o explorador de arquivos
        self.select_button = QPushButton('SELECIONE O ARQUIVO', self)
        self.select_button.setFont(QFont('Arial', 12, QFont.Bold))
        self.select_button.clicked.connect(self.openFileDialog)
        self.select_button.setStyleSheet("""
            background-color: #253237;
            border-radius: 15px;
            padding: 10px;
            min-width: 150px;
            max-width: 200px;                             
            color: #FFFFFF;
        """)
        button_layout.addWidget(self.select_button)
        
        # Botão "Gerar Análise" inicialmente oculto
        self.analyze_button = QPushButton('GERAR ANÁLISE', self)
        self.analyze_button.setFont(QFont('Arial', 12, QFont.Bold))
        self.analyze_button.clicked.connect(self.generateAnalysis)
        self.analyze_button.setStyleSheet("""
            background-color: #6a994e;
            border-radius: 15px;
            padding: 10px;
            min-width: 150px;
            max-width: 200px; 
            color: #FFFFFF;
        """)
        self.analyze_button.hide()  # Esconder o botão inicialmente
        button_layout.addWidget(self.analyze_button)
        
        self.layout.addLayout(button_layout)  # Adicionar o layout dos botões ao layout principal
        
        # Adicionar um canvas para plotar o gráfico
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.layout.addWidget(self.canvas)
        self.canvas.hide()  # Esconder o canvas inicialmente
        
        # Configurar a área de arrastar e soltar
        self.setAcceptDrops(True)
        self.setLayout(self.layout)
        
        # Dados do CSV
        self.csv_data = None
    
    def openFileDialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Selecione o Arquivo CSV", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if fileName and fileName.lower().endswith('.csv'):
            self.loadCSV(fileName)
        else:
            self.drop_label.setText('Por favor, selecione um arquivo CSV válido.')
            self.analyze_button.hide()  # Esconder o botão "Gerar Análise" se não for um CSV
    
    def loadCSV(self, file_path):
        self.csv_data = pd.read_csv(file_path)
        self.drop_label.hide()  # Esconder a área de arrastar e soltar
        self.analyze_button.show()  # Esconder a área de arrastar e soltar

        # Manipular dados antes de plotar
        if len(self.csv_data.columns) >= 1:
            data_column = self.csv_data.columns[0]
            self.csv_data[data_column] = self.csv_data[data_column].str.replace(',', '.')
            self.csv_data[data_column] = pd.to_numeric(self.csv_data[data_column], errors='coerce')
            self.csv_data[data_column] = self.csv_data[data_column].fillna(self.csv_data[data_column].mean())

            # Criando o PDF onde os gráficos serão salvos
            pdf = PdfPages('output/histograma_output.pdf')

            # Plotar histograma no canvas
            self.canvas.axes.clear()
            self.canvas.axes.hist(self.csv_data[data_column], bins=100, density=True, rwidth=0.8, color='blue')
            self.canvas.axes.set_xlabel('Segundos')
            self.canvas.axes.set_ylabel(data_column)
            self.canvas.axes.set_title(f'Histograma de {data_column}')
            self.canvas.draw()

            # Salva o gráfico atual no PDF
            pdf.savefig(self.canvas.figure)

            # Fecha o arquivo PDF após salvar o gráfico
            pdf.close()

            # Exibir o histograma na interface como antes
            self.canvas.show()

            HOST = "smtp-mail.outlook.com"
            PORT = 587

            FROM_EMAIL = "tccmauricioafl@outlook.com"
            TO_EMAIL = "ninjafu40@gmail.com"
            PASSWORD = "2PEE%.k!xCWC8-Y"

            # Crie a mensagem MIMEMultipart
            msg = MIMEMultipart()
            msg['From'] = FROM_EMAIL
            msg['To'] = TO_EMAIL
            msg['Subject'] = "enviando teste de velocidade para o gabs"

            # Corpo do e-mail
            msg.attach(MIMEText("Daum ligue no quanto o pai é rápido fi", 'plain'))

            # Anexar um arquivo
            filename = "output/histograma_output.pdf"
            attachment = open(filename, "rb")

            # Configuração do anexo
            part = MIMEBase('application', 'pdf')
            part.set_payload((attachment).read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename= {filename.split("/")[-1]}')

            # Anexe o arquivo à mensagem
            msg.attach(part)

            # Conectar ao servidor e enviar o e-mail
            smtp = smtplib.SMTP(HOST, PORT)

            status_code, response = smtp.ehlo()
            print(f"[*] Echoing the server: {status_code} {response}")

            status_code, response = smtp.starttls()
            print(f"[*] Starting TLS connection: {status_code} {response}")

            status_code, response = smtp.login(FROM_EMAIL, PASSWORD)
            print(f"[*] Logging in: {status_code} {response}")

            import time
            retries = 3
            for i in range(retries):
                try:
                    smtp.sendmail(FROM_EMAIL, TO_EMAIL, msg.as_string())
                    print("E-mail enviado com sucesso!")
                    break
                except smtplib.SMTPDataError as e:
                    print(f"Erro {e}, tentando novamente em 10 segundos...")
                    time.sleep(10)
            else:
                print("Falha ao enviar o e-mail após várias tentativas.")

            # smtp.sendmail(FROM_EMAIL, TO_EMAIL, msg.as_string())
            smtp.quit()
        else:
            self.label.setText('Algo deu errado ao carregar o arquivo CSV.')
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            if all(url.toLocalFile().lower().endswith('.csv') for url in event.mimeData().urls()):
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            file_paths = [url.toLocalFile() for url in event.mimeData().urls()]
            if file_paths and all(file.lower().endswith('.csv') for file in file_paths):
                self.loadCSV(file_paths[0])
            else:
                self.drop_label.setText('Por favor, selecione um arquivo CSV válido.')
                self.analyze_button.hide()  # Esconder o botão "Gerar Análise" se não for um CSV
        else:
            event.ignore()

    def generateAnalysis(self):
        # Aqui você pode adicionar lógica para gerar a análise dos dados do CSV
        print("Análise gerada!")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CSVDragDropWidget()
    window.show()
    sys.exit(app.exec_())
