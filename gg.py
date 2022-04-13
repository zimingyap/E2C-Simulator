import sys
from PyQt5.QtWidgets import * 
                    
   
#Main Window
class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 - QTableWidget'
        self.left = 0
        self.top = 0
        self.width = 300
        self.height = 200
        self.machine_stats = [{'Machine': 'cpu', 'Machine id': 0, '%Completion': 22.22222222222222, '# of %Completion': 4, '%XCompletion': 11.11111111111111, '# of %XCompletion': 2, '#Missed URG': 0, 'Missed BE': 12, '%Energy': 1.5592722222222215, '%Wasted Energy': 170928.0},
{'Machine': 'cpu', 'Machine id': 1, '%Completion': 12.5, '# of %Completion': 1, '%XCompletion': 25.0, '# of %XCompletion': 2, '#Missed URG': 0, 'Missed BE': 5, '%Energy': 1.0621194444444442, '%Wasted Energy': 83627.99999999999},
{'Machine': 'gpu', 'Machine id': 2, '%Completion': 40.909090909090914, '# of %Completion': 27, '%XCompletion': 36.36363636363637, '# of %XCompletion': 24, '#Missed URG': 0, 'Missed BE': 15, '%Energy': 4.75279111111111, '%Wasted Energy': 205693.99999999983}]
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        # self.btn = QPushButton(self)
        # self.btn.setGeometry(100,100,50,50)
        # self.btn.clicked.connect(lambda: self.createTable())
        self.createTable()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget)
        self.setLayout(self.layout)
   
        #Show window
        self.show()
   
    #Create table
    def createTable(self):
        self.tableWidget = QTableWidget()
        print("button")
        #Row count
        self.tableWidget.setRowCount(len(self.machine_stats)+1) 
  
        #Column count
        self.tableWidget.setColumnCount(8) 
        self.tableWidget.setFixedSize(700,700)
        self.tableWidget.move(900,900) 
        self.tableWidget.setHorizontalHeaderLabels(['Machine id', '%Completion', '# of %Completion'])
        # self.tableWidget.horizontalHeaderItem().setTextAlignment(Qt.AlignHCenter)
        for i,v in enumerate(self.machine_stats):
            machineID = QTableWidgetItem(str(v['Machine id']))
            completion = QTableWidgetItem(str(v['%Completion']))
            no_completion = QTableWidgetItem(str(v['# of %Completion']))
            
            self.tableWidget.setItem(i,0,machineID)           
            self.tableWidget.setItem(i,1,completion)
            self.tableWidget.setItem(i,2,no_completion)
            
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())