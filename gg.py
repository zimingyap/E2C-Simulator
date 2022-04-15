from PyQt5.QtWidgets import (
    QWidget,
    QApplication,
    QLabel,
    QFrame,
    QMainWindow,
    QMenu,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QSlider,
    QGridLayout,
    QSlider,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAction,
    QScrollArea
)
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import (
    QPropertyAnimation,
    Qt,
    QPoint,
    QThread,
    QSequentialAnimationGroup,
    QCoreApplication,
    QProcess,
    
)
import sys
class ScrollMessageBox(QMessageBox):
   def __init__(self, l, *args, **kwargs):
      QMessageBox.__init__(self, *args, **kwargs)
      scroll = QScrollArea(self)
      scroll.setWidgetResizable(True)
      self.content = QWidget()
      scroll.setWidget(self.content)
      lay = QVBoxLayout(self.content)
      for item in l:
         lay.addWidget(QLabel(item, self))
      self.layout().addWidget(scroll, 0, 0, 1, self.layout().columnCount())
      self.setStyleSheet("QScrollArea{min-width:300 px; min-height: 400px}")

class W(QWidget):
   def __init__(self):
      super().__init__()
      self.btn = QPushButton('Show Message', self)
      self.btn.setGeometry(10, 10, 100, 100)
      self.btn.clicked.connect(self.buttonClicked)
      self.lst = [str(i) for i in range(2000)]
      self.show()


   def buttonClicked(self):
      result = ScrollMessageBox(self.lst, None)
      result.exec_()

if __name__ == "__main__":
   app = QApplication(sys.argv)
   gui = W()
   sys.exit(app.exec_())