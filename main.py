import sys
import unithandler
import pandas as pd
import xlsxwriter
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget, QDialog, QFileDialog, QLineEdit, QLabel, QHBoxLayout

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set the window size and title
        self.setWindowTitle("Unit File Converter")
        self.setGeometry(100, 100, 300, 200)
        
        # Create a layout
        layout = QVBoxLayout()
        
        # Create buttons
        convert_unit_files_to_spreadsheet_button = QPushButton("Convert Unit Files to Spreadsheet")
        convert_spreadsheet_to_unit_files_button = QPushButton("Convert Spreadsheet to Unit Files")
        convert_command_to_spreadsheet_button = QPushButton("Convert Command to Spreadsheet")
        convert_spreadsheet_to_command_button = QPushButton("Convert Spreadsheet to Command")
        
        # Add buttons to the layout
        layout.addWidget(convert_unit_files_to_spreadsheet_button)
        layout.addWidget(convert_spreadsheet_to_unit_files_button)
        layout.addWidget(convert_command_to_spreadsheet_button)
        layout.addWidget(convert_spreadsheet_to_command_button)
        
        # Set the central widget
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        # Connect button clicks to functions (placeholder functions for now)
        convert_unit_files_to_spreadsheet_button.clicked.connect(lambda: self.convert_unit_files("from_unit"))
        convert_spreadsheet_to_unit_files_button.clicked.connect(lambda: self.convert_unit_files("to_unit"))
        convert_command_to_spreadsheet_button.clicked.connect(self.convert_command_to_spreadsheet)
        convert_spreadsheet_to_command_button.clicked.connect(self.convert_spreadsheet_to_command)

    def convert_unit_files(self, mode):
        self.conversionWindow = ConversionWindow(mode)
        self.conversionWindow.show()

    def convert_spreadsheet_to_unit_files(self):
        print("Converting Spreadsheet to Unit Files")

    def convert_command_to_spreadsheet(self):
        print("Converting Command to Spreadsheet")

    def convert_spreadsheet_to_command(self):
        print("Converting Spreadsheet to Command")


class ConversionWindow(QDialog):
    def __init__(self, mode):
        super(ConversionWindow, self).__init__()
        self.mode = mode
        self.setWindowTitle("Convert Unit Files to Spreadsheet")
        self.setFixedSize(600, 350)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20,20,20,20)
        self.initUI()
    
    def initUI(self):
        self.selectUnitbaseButton = QPushButton("Select")
        self.selectUnitstatButton = QPushButton("Select")
        self.selectUsearchButton = QPushButton("Select")
        self.convertButton = QPushButton("Convert")
        
        self.unitbaseLineEdit = QLineEdit()
        self.unitstatLineEdit = QLineEdit()
        self.usearchLineEdit = QLineEdit()
        
        self.unitbaseSubtitleLabel = QLabel("Select your unitbase.dat file.")
        self.unitstatSubtitleLabel = QLabel("Select your unitstat.dat file.")
        self.usearchSubtitleLabel = QLabel("Select your usearch.dat file.")

        self.unitbaseSection = QHBoxLayout()
        self.unitbaseSection.setContentsMargins(0,0,0,10)

        self.unitstatSection = QHBoxLayout()
        self.unitstatSection.setContentsMargins(0,0,0,10)

        self.usearchSection = QHBoxLayout()
        self.usearchSection.setContentsMargins(0,0,0,10)

        if self.mode == "to_unit":
            self.spreadsheetSubtitleLabel = QLabel("Select the spreadsheet (.xlsx) to convert.")
            self.spreadsheetLineEdit = QLineEdit()
            self.selectSpreadsheetButton = QPushButton("Select")
            self.selectSpreadsheetButton.clicked.connect(lambda: self.updateFilePath("spreadsheetLineEdit", "*.xlsx"))
            self.spreadsheetSection = QHBoxLayout()
            self.spreadsheetSection.setContentsMargins(0,0,0,30)
            self.layout.addWidget(self.spreadsheetSubtitleLabel)
            self.spreadsheetSection.addWidget(self.spreadsheetLineEdit)
            self.spreadsheetSection.addWidget(self.selectSpreadsheetButton)
            self.layout.addLayout(self.spreadsheetSection)
        
        self.unitbaseSection.addWidget(self.unitbaseLineEdit)
        self.unitbaseSection.addWidget(self.selectUnitbaseButton)

        self.unitstatSection.addWidget(self.unitstatLineEdit)
        self.unitstatSection.addWidget(self.selectUnitstatButton)

        self.usearchSection.addWidget(self.usearchLineEdit)
        self.usearchSection.addWidget(self.selectUsearchButton)

        self.layout.addWidget(self.unitbaseSubtitleLabel)
        self.layout.addLayout(self.unitbaseSection)

        self.layout.addWidget(self.unitstatSubtitleLabel)
        self.layout.addLayout(self.unitstatSection)

        self.layout.addWidget(self.usearchSubtitleLabel)
        self.layout.addLayout(self.usearchSection)

        self.layout.addWidget(self.convertButton)
        
        self.setLayout(self.layout)
        
        # Connect signals
        self.selectUnitbaseButton.clicked.connect(lambda: self.updateFilePath("unitbaseLineEdit", "*.dat"))
        self.selectUnitstatButton.clicked.connect(lambda: self.updateFilePath("unitstatLineEdit", "*.dat"))
        self.selectUsearchButton.clicked.connect(lambda: self.updateFilePath("usearchLineEdit", "*.dat"))
        if self.mode == "from_unit":
            self.convertButton.clicked.connect(self.convert_from_unit)
        elif self.mode == "to_unit":
            self.convertButton.clicked.connect(self.convert_to_unit)
    
    def updateFilePath(self, fileType, extension):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "", extension, options=options)
        if fileName:
            getattr(self, f'{fileType}').setText(fileName)

    def convert_from_unit(self):
        data = unithandler.get_unit_data(self.unitbaseLineEdit.text(), self.unitstatLineEdit.text(), self.usearchLineEdit.text())
        ordered_columns = list(data[0].keys())

        wb = xlsxwriter.Workbook("IE3 Unit Database.xlsx")
        ws = wb.add_worksheet()

        for col_num, header in enumerate(ordered_columns):
            ws.write(0, col_num, header)
        
        whole_number_format = wb.add_format({'num_format': '0'})
        for row_num, data in enumerate(data, start=1):
            for col_num, (key,value) in enumerate(data.items()):
                ws.write(row_num, col_num, value, whole_number_format)
        ws.autofit()
        wb.close()

    def convert_to_unit(self):
        file_path = self.spreadsheetLineEdit.text()
        df = pd.read_excel(file_path)

        data = df.to_dict(orient='records')
        success = unithandler.to_unit_data(data, self.unitbaseLineEdit.text(), self.unitstatLineEdit.text(), self.usearchLineEdit.text())

        


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
