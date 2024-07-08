import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QTableView, QAbstractItemView
from PyQt5.QtCore import Qt, QAbstractTableModel, QMimeData
from PyQt5.QtGui import QFont, QColor
import pandas as pd
import numpy as np

class PandasTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def rowCount(self, parent):
        return len(self._data)

    def columnCount(self, parent):
        return len(self._data.columns)

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return str(self._data.iloc[index.row(), index.column()])
        return None

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
        
        # QTableView para mostrar o preview do CSV
        self.table_view = QTableView(self)
        self.table_view.setStyleSheet("""
            background-color: #E0FBFC;
            color: #000000;
        """)
        self.layout.addWidget(self.table_view)
        self.table_view.hide()  # Esconder a tabela inicialmente
        
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
        self.analyze_button.show()  # Mostrar o botão "Gerar Análise"
        
        # Mostrar os dados em QTableView
        model = PandasTableModel(self.csv_data)
        self.table_view.setModel(model)
        self.table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_view.resizeColumnsToContents()
        self.table_view.show()  # Mostrar a tabela após carregar os dados
    
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
