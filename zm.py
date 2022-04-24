import sys
import os
import json
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
    QSlider,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAction,
    QScrollArea,
    QComboBox
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

import csv
from os import makedirs
import pandas as pd

import utils.config as config
from utils.simulator import Simulator
from utils.machine import Machine
import utils.config as config


class Statistic(QFrame):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.width = 400
        self.TotalCompletion = QLabel(self)
        self.TotalCompletion.setText("%Total Completion: {}".format(0))
        self.TotalCompletion.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.TotalCompletion.setMaximumWidth(self.width)
        self.TotalCompletion.setStyleSheet("border:1px solid;")
        self.layout.addWidget(self.TotalCompletion)

        self.TotalxCompletion = QLabel(self)
        self.TotalxCompletion.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.TotalxCompletion.setText("%Total xCompletion: {}".format(0))
        self.TotalxCompletion.setMaximumWidth(self.width)
        self.TotalxCompletion.setStyleSheet("border:1px solid;")
        self.layout.addWidget(self.TotalxCompletion)

        self.deffered = QLabel(self)
        self.deffered.setText("%Deffered: {}".format(0))
        self.deffered.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.deffered.setMaximumWidth(self.width)
        self.deffered.setStyleSheet("border:1px solid;")
        self.layout.addWidget(self.deffered)

        self.dropped = QLabel(self)
        self.dropped.setText("%Dropped: {}".format(0))
        self.dropped.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.dropped.setMaximumWidth(self.width)
        self.dropped.setStyleSheet("border:1px solid;")
        self.layout.addWidget(self.dropped)

        self.totalCompletion = QLabel(self)
        self.totalCompletion.setText("totalCompletion%: {}".format(0))
        self.totalCompletion.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.totalCompletion.setMaximumWidth(self.width)
        self.totalCompletion.setStyleSheet("border:1px solid;")
        self.layout.addWidget(self.totalCompletion)

        self.consumedEnergy = QLabel(self)
        self.consumedEnergy.setText("ConsumedEnergy%: {}".format(0))
        self.consumedEnergy.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.consumedEnergy.setMaximumWidth(self.width)
        self.consumedEnergy.setStyleSheet("border:1px solid;")
        self.layout.addWidget(self.consumedEnergy)

        self.energyPerCompletion = QLabel(self)
        self.energyPerCompletion.setText("energy_per_completion: {}".format(0))
        self.energyPerCompletion.setTextInteractionFlags(
            Qt.TextSelectableByMouse)
        self.energyPerCompletion.setMaximumWidth(self.width)
        self.energyPerCompletion.setStyleSheet("border:1px solid;")
        self.layout.addWidget(self.energyPerCompletion)

        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)


class GUI_SIM(QFrame):
    def __init__(self):
        super().__init__()
        # self.setStyleSheet("border:1px solid;")
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)


class ScrollMessageBox(QMessageBox):
    def __init__(self, l, title, *args, **kwargs):
        QMessageBox.__init__(self, *args, **kwargs)
        self.task = l
        self.comboBox = QComboBox(self)
        self.comboBox.addItem("All")
        self.comboBox.addItem("Completed tasks")
        self.comboBox.addItem("Not completed tasks")
        self.comboBox.addItem("Missed tasks")
        self.comboBox.addItem("Dropped tasks")
        self.comboBox.addItem("Machine logs")
        self.comboBox.activated.connect(self.activated)
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        self.content = QWidget()
        scroll.setWidget(self.content)
        self.lay = QVBoxLayout(self.content)
        for item in self.task:
            self.lay.addWidget(QLabel("{}".format(item), self))
        self.layout().addWidget(self.comboBox)
        self.layout().addWidget(scroll, 0, 0, 1, self.layout().columnCount())
        self.setStyleSheet("QScrollArea{min-width:900 px; min-height: 400px}")
        self.setWindowTitle(title)

    def activated(self, index):
        self.clearLayout()
        if index == 0:
            for item in self.task:
                self.lay.addWidget(QLabel("{}".format(item), self))
        elif index == 1:
            for item in self.task:
                if 'Type' in item and item['Event Type'] == "COMPLETED":
                    self.lay.addWidget(QLabel("{}".format(item), self))
        elif index == 2:
            for item in self.task:
                if 'Type' in item and item['Event Type'] == "XCOMPLETED":
                    self.lay.addWidget(QLabel("{}".format(item), self))

        elif index == 3:
            for item in self.task:
                if 'Type' in item and item['Event Type'] == 'MISSED':
                    self.lay.addWidget(QLabel("{}".format(item), self))
        elif index == 4:
            for item in self.task:
                if 'Type' in item and item['Event Type'] == 'DROPPED_RUNNING_TASK':
                    self.lay.addWidget(QLabel("{}".format(item), self))
        elif index == 5:
            for item in self.task:
                if 'Machine id' in item:
                    self.lay.addWidget(QLabel("{}".format(item), self))

    def clearLayout(self):
        if self.lay is not None:
            while self.lay.count():
                item = self.lay.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())


class ScrollMessageBox1(QMessageBox):
    def __init__(self, l, title, *args, **kwargs):
        QMessageBox.__init__(self, *args, **kwargs)
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        self.content = QWidget()
        scroll.setWidget(self.content)
        lay = QVBoxLayout(self.content)
        for k, v in l.items():
            lay.addWidget(QLabel("{} : {}".format(k, v), self))
        self.layout().addWidget(scroll, 0, 0, 1, self.layout().columnCount())
        self.setStyleSheet("QScrollArea{min-width:900 px; min-height: 400px}")
        self.setWindowTitle(title)


class ScrollMessageBox2(QMessageBox):
    def __init__(self, l, title, *args, **kwargs):
        QMessageBox.__init__(self, *args, **kwargs)
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        self.content = QWidget()
        scroll.setWidget(self.content)
        lay = QVBoxLayout(self.content)
        for k in l:
            lay.addWidget(QLabel("{}".format(k), self))
        self.layout().addWidget(scroll, 0, 0, 1, self.layout().columnCount())
        self.setStyleSheet("QScrollArea{min-width:900 px; min-height: 400px}")
        self.setWindowTitle(title)


class GUI(QMainWindow):
    def __init__(self):
        super(GUI, self).__init__()
        self.color = ["background-color:lightgreen", "background-color:lightblue",
                      "background-color:lightsalmon", "background-color:lightpink", "background-color:lightgoldenrodyellow"]
        self.no_of_task = 150  # need to read from somewhere
        self.tasks = []
        self.machine_stats = []
        self.machine_stats_btn = []
        self.m_coords = {}
        self.mq_coords = {}  # machine queue coordinates
        self.bq_coords = {}
        self.mq_availability = {}
        self.machine_availability = {}
        self.batch_queue_availability = {}
        self.finishedLog = []
        self.finishedTasks = []
        self.finishedTasksLabel = []
        # self.completedTask = []
        # self.missedTask = []
        # self.droppedTask = []
        self.deletedTask = []
        self.machine_queue_size = config.machine_queue_size
        self.initUI()

    def initUI(self):
        # self.setGeometry(0, 0, 2560, 1440)
        # self.showFullScreen()
        self.move(0, 0)
        self.setMinimumSize(2500, 1200)
        self.setWindowTitle("Simulator")
        self.group = QSequentialAnimationGroup(self)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        self.statistic = Statistic()
        self.gui_sim = GUI_SIM()
        self.layout.addWidget(self.statistic, 1)
        self.layout.addWidget(self.gui_sim, 6)
        # self.create_menu_bar()
        self.draw_batch_queue()
        self.scheduling()
        self.draw_machine()
        for i in range(len(self.m_coords)):
            b = QPushButton(self)
            b.setGeometry(self.m_coords[i][0]+400,
                          self.m_coords[i][1]+20, 70, 40)
            b.setText("Details")
            b.setEnabled(False)
            self.machine_stats_btn.append(b)
            self.machine_stats_btn[i].clicked.connect(
                lambda checked, a=i: self.create_machine_stat(a))
        for _ in range(self.no_of_task):
            a = QLabel(self)
            self.tasks.append(a)
            
        self.main()

    def main(self):
        config.init()
        scheduling_method = config.scheduling_method
        workload = '0-0'
        low = 0
        high = 1
        self.path_to_result = f'{config.settings["path_to_output"]}/data/{workload}/{scheduling_method}'
        makedirs(self.path_to_result, exist_ok=True)
        self.report_summary = open(
            f'{self.path_to_result}/results-summary.csv', 'w')
        self.summary_header = ['Episode', 'total_no_of_tasks', 'mapped', 'cancelled', 'URG_missed', 'BE_missed',
                               'Completion%', 'xCompletion%', 'totalCompletion%', 'consumed_energy%', 'energy_per_completion']
        self.writer = csv.writer(self.report_summary)
        self.writer.writerow(self.summary_header)
        self.df_task_based_report = pd.DataFrame()

        for i in range(low, high):
            s = '\n\n' + 15 * '='+' EPISODE#'+str(i)+' ' + 15 * '='
            config.log.write(s)
            print(s)
            config.init()

            id = 0
            for machine_type in config.machine_types:
                for r in range(1, machine_type.replicas+1):
                    specs = {'power': machine_type.power,
                             'idle_power': machine_type.idle_power}
                    machine = Machine(id, r, machine_type, specs)
                    config.machines.append(machine)

                    id += 1

            self.simulation = Simulator(
                workload_id=workload, epsiode_no=i, id=i, verbosity=0)
            self.thread = QThread(parent=self)
            self.simulation.progress.connect(self.handle_signal)
            self.simulation.moveToThread(self.thread)
            self.thread.started.connect(self.simulation.create_event_queue)
            self.thread.started.connect(self.simulation.set_scheduling_method)
            self.thread.started.connect(self.simulation.setTimer)
            self.thread.started.connect(self.simulation.run)

            self.timer = 1000

            self.startBtn = QPushButton("Start", self)
            self.startBtn.setGeometry(30, 750, 100, 50)
            self.startBtn.clicked.connect(lambda: self.thread.start())
            self.pauseBtn = QPushButton(self)
            self.pauseBtn.setGeometry(30, 800, 100, 50)
            self.pauseBtn.setText("Pause")
            self.pause = True
            self.pauseBtn.clicked.connect(lambda: self.pauseResumeBtn())

            self.endBtn = QPushButton("End", self)
            self.endBtn.setGeometry(30, 850, 100, 50)
            self.endBtn.clicked.connect(lambda: self.endThread())

            self.slider = QSlider(self)
            self.slider.setGeometry(200, 760, 200, 40)
            self.slider.setOrientation(Qt.Horizontal)
            self.slider.setMinimum(50)
            self.slider.setMaximum(2000)
            self.slider.setInvertedAppearance(True)
            self.slider.setSliderPosition(self.timer)
            self.slider.valueChanged.connect(self.updateSlider)
            self.slider.valueChanged.connect(self.speed)

            self.sliderLabel = QLabel(self)
            self.sliderLabel.setGeometry(400, 760, 200, 40)
            self.sliderLabel.setText("{:.1f}x".format(self.timer/1000))

            self.finishSimBtn = QPushButton("Finish Simulation", self)
            self.finishSimBtn.setGeometry(200, 850, 100, 50)
            self.finishSimBtn.adjustSize()
            self.finishSimBtn.clicked.connect(
                lambda: self.simulation.setTimer(0))

            self.restartBtn = QPushButton("Restart", self)
            self.restartBtn.setGeometry(30, 900, 100, 50)
            self.restartBtn.setEnabled(False)
            self.restartBtn.clicked.connect(lambda: self.restart())

            self.mDetails = QPushButton("Machine Details", self)
            self.mDetails.setGeometry(30, 950, 100, 50)
            self.mDetails.setEnabled(False)
            self.mDetails.adjustSize()
            self.mDetails.clicked.connect(lambda: self.createTable())

            self.getLogBtn = QPushButton("Full log", self)
            self.getLogBtn.setGeometry(30, 1000, 100, 50)
            self.getLogBtn.setEnabled(False)
            self.getLogBtn.adjustSize()
            self.getLogBtn.clicked.connect(lambda: self.getLog())

            self.thread.finished.connect(
                lambda: self.simulation.report(self.path_to_result))
            self.thread.finished.connect(self.load_config)
            self.thread.finished.connect(self.statistics_info)
            self.thread.finished.connect(self.setEnabledEnd)
            self.thread.finished.connect(self.deleteTask)
            self.thread.finished.connect(self.getReport)

    def getReport(self):
        row, task_report = self.simulation.report(self.path_to_result)
        self.writer.writerows(row)
        self.df_task_based_report = self.df_task_based_report.append(
            task_report, ignore_index=True)
        self.report_summary.close()
        self.df_task_based_report.to_csv(
            f'{self.path_to_result}/task_based_report.csv', index=False)
        df_summary = pd.read_csv(f'{self.path_to_result}/results-summary.csv',
                                 usecols=['Completion%', 'xCompletion%', 'totalCompletion%',
                                          'consumed_energy%', 'energy_per_completion'])
        print('\n\n' + 10*'*'+'  Average Results of Executing Episodes  '+10*'*')
        print(df_summary.mean())

    # Generate logs and display in a pop up window
    def getLog(self):
        result = ScrollMessageBox(self.finishedLog, "Full logs", None)
        result.exec_()

    # Enable buttons
    def setEnabledEnd(self):
        self.mDetails.setEnabled(True)
        self.restartBtn.setEnabled(True)
        self.getLogBtn.setEnabled(True)

        for i in range(len(self.machine_stats_btn)):
            self.machine_stats_btn[i].setEnabled(True)

    # End the thread/simulation
    def endThread(self):
        self.simulation.threadController = False
        self.thread.terminate()
        self.thread.wait()
        # self.thread.exit()

    # Control the speed of the simulation, this function calls a function in simulator.py
    def speed(self, value):
        self.timer = value
        self.simulation.setTimer(value/1000)

    # Update the slider speed text
    def updateSlider(self, value):
        if value != 0:
            self.sliderLabel.setText("{:.1f}x".format(1000/value, "2f"))

    # Puase the simulation
    def pauseResumeBtn(self):
        if self.pause:
            self.pause = False
            self.pauseBtn.setText("Resume")
            self.simulation.simPause(0)

        else:
            self.pause = True
            self.pauseBtn.setText("Pause")
            self.simulation.simPause(1)

    def deleteTask(self):
        for i in range(len(self.tasks)):
            if i not in self.deletedTask:
                self.deletedTask.append(i)
                self.tasks[i].deleteLater()

    # Handling
    def handle_signal(self, d):
        print(d)
        self.finishedLog.append(d)
        if 'Type' in d:
            self.taskAnimation(120, 520, d)
        elif '%Completion' in d:
            if len(self.machine_stats) < len(config.machines):
                self.machine_stats.append(d)

    # Pop up message box to show statistics of each machine
    def create_machine_stat(self, i):
        msgBox = ScrollMessageBox1(self.machine_stats[i], "Machine log", None)
        msgBox.exec_()

    # Create machine stat table
    def createTable(self):
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(len(self.machine_stats)+1)
        self.tableWidget.setColumnCount(len(self.machine_stats[0]))
        self.tableWidget.setHorizontalHeaderLabels(['Machine name', '%Completion', '# of %Completion',
                                                   '%XCompletion', '# of %XCompletion', '#Missed URG', 'Missed BE', '%Energy', '%Wasted Energy'])
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()
        for i, v in enumerate(self.machine_stats):
            machineName = QTableWidgetItem(str(v['Machine']))
            completion = QTableWidgetItem(str(round(v['%Completion'], 2)))
            no_completion = QTableWidgetItem(
                str(round(v['# of %Completion'], 2)))
            XCompletion = QTableWidgetItem(str(round(v['%XCompletion'], 2)))
            no_XCompletion = QTableWidgetItem(
                str(round(v['# of %XCompletion'], 2)))
            missed_URG = QTableWidgetItem(str(round(v['#Missed URG'], 2)))
            missed_BE = QTableWidgetItem(str(round(v['Missed BE'], 2)))
            energy = QTableWidgetItem(str(round(v['%Energy'], 2)))
            wasted_energy = QTableWidgetItem(
                str(round(v['%Wasted Energy'], 2)))

            self.tableWidget.setItem(i, 0, machineName)
            self.tableWidget.setItem(i, 1, completion)
            self.tableWidget.setItem(i, 2, no_completion)
            self.tableWidget.setItem(i, 3, XCompletion)
            self.tableWidget.setItem(i, 4, no_XCompletion)
            self.tableWidget.setItem(i, 5, missed_URG)
            self.tableWidget.setItem(i, 6, missed_BE)
            self.tableWidget.setItem(i, 7, energy)
            self.tableWidget.setItem(i, 8, wasted_energy)

        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()

        self.tableWidget.setFixedSize(self.tableWidget.horizontalHeader().length() +
                                      self.tableWidget.verticalHeader().width(),
                                      self.tableWidget.verticalHeader().length() +
                                      self.tableWidget.horizontalHeader().height())

        self.tableWidget.verticalHeader().setStretchLastSection(True)
        self.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents)
        # self.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tableWidget.show()
    # Create menu bar on top

    def create_menu_bar(self):
        menuBar = self.menuBar()
        # Creating menus using a QMenu object
        fileMenu = QMenu("&File", self)
        editMenu = QMenu("&Edit", self)
        helpMenu = QMenu("&Help", self)
        menuBar.addMenu(fileMenu)
        menuBar.addMenu(editMenu)
        menuBar.addMenu(helpMenu)

        quitAction = QAction("Quit", self)
        fileMenu.addAction(quitAction)
    # Set the stats of machines after simulation ends

    def statistics_info(self):
        self.statistic.TotalCompletion.setText("%Total Completion: {:.3f}".format(
            self.data['statistics']['%Total Completion']))
        self.statistic.TotalxCompletion.setText("%Total xCompletion: {:.3f}".format(
            self.data['statistics']['%Total xCompletion']))
        self.statistic.deffered.setText(
            "%Deferred: {:.3f}".format(self.data['statistics']['%Deferred']))
        self.statistic.dropped.setText(
            "%Dropped: {:.3f}".format(self.data['statistics']['%Dropped']))
        self.statistic.totalCompletion.setText(
            "totalCompletion%: {:.3f}".format(self.data['statistics']['totalCompletion%']))
        self.statistic.consumedEnergy.setText("ConsumedEnergy%: {:.3f}".format(
            self.data['statistics']['consumed_energy%']))
        self.statistic.energyPerCompletion.setText("energy_per_completion: {:.3f}".format(
            self.data['statistics']['energy_per_completion']))

    # draws batch queue on the left side
    def draw_batch_queue(self):
        overload = None
        if (config.batch_queue_size <= 4):
            batch_queue_size = config.batch_queue_size
        else:
            batch_queue_size = 4
            overload = True
        x = 220
        y = 600
        for i in range(batch_queue_size):
            self.batch_queue_availability[i] = True
            self.bq_coords[i] = [x, y]
            box = QLabel(self)
            box.setGeometry(x, y, 41, 41)
            box.setFrameShape(QFrame.Box)
            x -= 40
        if (overload):
            overload_dot = QLabel(self)
            overload_dot.setGeometry(100, y, 41, 41)
            overload_dot.setText("...")
            overload_dot.setAlignment(Qt.AlignCenter)

    # Controls the animation of the tasks
    def taskAnimation(self, x, y, d):
        # # if d['Event Type'] != 'COMPLETION':
        #     self.tasks[d["Task id"]].resize(35, 35)
        #     self.tasks[d["Task id"]].setStyleSheet(
        #         self.color[d["Task id"] % 5])
        #     self.tasks[d["Task id"]].setText("{}".format(d["Task id"]))
        #     self.tasks[d["Task id"]].setAlignment(Qt.AlignCenter)
        #     self.anim = QPropertyAnimation(self.tasks[d["Task id"]], b"pos")
        
        # task arriving into batch queue, ready to go into scheduler
        if d['Event Type'] == 'INCOMING':
            self.tasks[d["Task id"]].resize(35, 35)
            self.tasks[d["Task id"]].setStyleSheet(
                self.color[d["Task id"] % 5])
            self.tasks[d["Task id"]].setText("{}".format(d["Task id"]))
            self.tasks[d["Task id"]].setAlignment(Qt.AlignCenter)
            self.anim = QPropertyAnimation(self.tasks[d["Task id"]], b"pos")
            for i, v in enumerate(self.batch_queue_availability):
                if v == True:
                    self.anim.setDuration(self.timer/4)
                    self.anim.setStartValue(QPoint(x, 600))
                    self.anim.setEndValue(
                        QPoint(self.bq_coords[i][0], self.bq_coords[i][1]+1))
                    self.anim.setStartValue(
                        QPoint(self.bq_coords[i][0], self.bq_coords[i][1]+1))
                    self.anim.setEndValue(QPoint(y, 600))

                    v == False

        elif d['Event Type'] == "ARRIVING":
            for i, v in enumerate(self.mq_availability[d['Machine']]):
                if v == True:
                    coord_x = self.mq_coords[d['Machine']][len(
                        self.mq_availability[d['Machine']])-i-1][0]
                    coord_y = self.mq_coords[d['Machine']][len(
                        self.mq_availability[d['Machine']])-i-1][1]
                    self.anim.setStartValue(QPoint(y, 600))
                    self.anim.setEndValue(QPoint(coord_x+3, coord_y+3))
                    self.anim.setDuration(100)
                    self.mq_availability[d['Machine']] == False
                else:
                    continue
        elif d['Event Type'] == "RUNNING":
            mq_coord_x = self.mq_coords[d['Machine']][0][0]
            mq_coord_y = self.mq_coords[d['Machine']][0][1]
            coord_x = self.m_coords[d['Machine']][0]
            coord_y = self.m_coords[d['Machine']][1]
            self.anim.setStartValue(QPoint(mq_coord_x + 3, mq_coord_y + 3))
            self.anim.setEndValue(QPoint(coord_x+20, coord_y+15))
            self.anim.setDuration(self.timer/8)
        elif d['Event Type'] == "COMPLETION":
            coord_x = self.m_coords[d['Machine']][0]
            coord_y = self.m_coords[d['Machine']][1]
            self.anim.setStartValue(QPoint(coord_x, coord_y))
            self.anim.setEndValue(
                QPoint(self.m_coords[d['Machine']][0]+100, self.m_coords[d['Machine']][1]))
            self.anim.setDuration(self.timer/4)
            self.finishedTasks[d['Machine']].append(d['Task id'])
            self.finishedTasksLabel[d['Machine']].setText("Finished tasks: {}".format(
                self.finishedTasks[d['Machine']][:-4:-1]))  # show last 3 element of finished tasks and reverse it
            self.anim.stop()
            self.tasks[d["Task id"]].deleteLater()
            self.deletedTask.append(d["Task id"])
        # elif d['Event Type'] == "XCOMPLETED":
        #     coord_x = self.m_coords[d['Machine']][0]
        #     coord_y = self.m_coords[d['Machine']][1]
        #     self.anim.setStartValue(QPoint(coord_x, coord_y))
        #     self.anim.setEndValue(
        #         QPoint(self.m_coords[d['Machine']][0]+100, self.m_coords[d['Machine']][1]))
        #     self.anim.setDuration(self.timer/4)
        #     self.finishedTasks[d['Machine']].append(d['Task id'])
        #     self.finishedTasksLabel[d['Machine']].setText("Finished tasks: {}".format(
        #     self.finishedTasks[d['Machine']][:-4:-1]))  # show last 3 element of finished tasks and reverse it
        #     self.anim.stop()
        #     self.tasks[d["Task id"]].deleteLater()
        #     self.deletedTask.append(d["Task id"])
        elif d['Event Type'] == "DROPPED_RUNNING_TASK":
            self.tasks[d["Task id"]].deleteLater()
            self.deletedTask.append(d["Task id"])

        elif d['Event Type'] == 'FINISH':
            self.thread.requestInterruption()
            self.thread.wait()  
            self.thread.quit()
        self.anim.start()

    # Draw the scheduler in the middle
    def scheduling(self):
        scheduling_method = config.scheduling_method
        round_scheduler = QLabel(self)
        round_scheduler.move(500, 580)
        round_scheduler.resize(80, 80)
        round_scheduler.setStyleSheet(
            """
        QLabel {
            border: 3px solid blue;
            border-radius: 40px;
            }
        """
        )
        round_scheduler.setText("{}".format(scheduling_method))
        round_scheduler.setAlignment(Qt.AlignCenter)

    # Draw the machines on the right side
    def draw_machine(self):
        machine_name = []
        config.init()
        self.machineBtn = []
        for i in config.machine_types:
            for _ in range(i.replicas):
                machine_name.append(i.name)
        y_axis = 200
        y_axis_size = 800
        y_axis_diff = int(y_axis_size/(len(machine_name)+1))
        machine_queue_overload = None
        if (config.machine_queue_size <= 4):
            machine_queue_size = config.machine_queue_size
        else:
            machine_queue_size = 4
            machine_queue_overload = True
        for i in range(len(machine_name)):
            self.machine_availability[i] = True
            x_axis = 1100
            y_axis += y_axis_diff
            m = QPushButton(self)
            mname = QLabel(self)
            mname.move(x_axis+120, y_axis-60)
            mname.resize(80, 40)
            m.move(x_axis+100, y_axis-20)
            m.resize(80, 80)
            mname.setText("{}".format(machine_name[i]))
            self.m_coords[i] = [x_axis+100, y_axis-20]
            if machine_name[i] == 'cpu':
                m.setStyleSheet("""
               QPushButton {
                  border: 3px solid black;
                  border-radius: 40px;
                  background-color:lightgreen;
                  }
               """)
            else:
                m.setStyleSheet("""
               QPushButton {
                  border: 3px solid black;
                  border-radius: 40px;
                  background-color:lightblue;
                  }
               """)
            self.machineBtn.append(m)
            self.machineBtn[i].clicked.connect(
                lambda checked, a=i: self.getMachineDetail(a))

            mq_c = []
            mq_a = []
            for _ in range(machine_queue_size):
                x_axis -= 40
                self.draw_machine_queue(x_axis, y_axis)
                mq_c.append([x_axis, y_axis])
                mq_a.append(True)
            self.mq_coords[i] = mq_c
            self.mq_availability[i] = mq_a
            if (machine_queue_overload):
                overload_dot = QLabel(self)
                overload_dot.setGeometry(940, y_axis, 41, 41)
                overload_dot.setText("...")
                overload_dot.setAlignment(Qt.AlignCenter)

        for i in range(len(self.m_coords)):
            t = QLabel(self)
            t.move(self.m_coords[i][0]+100, self.m_coords[i][1])
            t.resize(400, 80)
            t.setText("Finished tasks: ")
            self.finishedTasksLabel.append(t)
            self.finishedTasks.append([])

    def getMachineDetail(self, i):
        machineId = "id: {}".format(config.machines[i].id)
        machineType = "type: {}".format(config.machines[i].type.name)
        machineSpecs = "specs: {}".format(config.machines[i].specs)
        machineQSize = "Queue size: {}".format(config.machines[i].queue_size)
        machineDetail = [machineId, machineType, machineSpecs, machineQSize]
        msgBox = ScrollMessageBox2(machineDetail, "Machine detail", None)
        msgBox.exec_()

    # Draw machine queue
    def draw_machine_queue(self, x, y):
        mq = QLabel(self)
        mq.setFrameShape(QFrame.Box)
        mq.setGeometry(x, y, 41, 41)

    # Initialize QPainter for drawing line
    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.bq_sch_Lines(qp)
        self.sch_mq_Lines(qp)
        self.mq_m_Lines(qp)

        qp.end()

    # draw line from batch queue to scheduler
    def sch_mq_Lines(self, qp):
        pen = QPen(Qt.black, 2, Qt.DashLine)
        sch_x = 500+85
        sch_y = 580+41
        for i in range(len(self.mq_coords)):
            # first machine queue coordinates
            m_x = self.mq_coords[i][self.machine_queue_size-1][0]
            # first machine queue coordinates
            m_y = self.mq_coords[i][self.machine_queue_size-1][1] + 21
            qp.setPen(pen)
            qp.drawLine(sch_x, sch_y, m_x, m_y)

    # draw lines from scheduler to machine queue
    def bq_sch_Lines(self, qp):
        pen = QPen(Qt.black, 2, Qt.DashLine)
        bq_x = self.bq_coords[0][0] + 41  # first batch queue coordinates
        bq_y = self.bq_coords[0][1] + 21  # first batch queue coordinates
        sch_x = 500
        sch_y = 580+41.25
        qp.setPen(pen)
        qp.drawLine(bq_x, bq_y, sch_x, sch_y)

    # draw lines from machine queue to machine
    def mq_m_Lines(self, qp):
        pen = QPen(Qt.black, 2, Qt.DashLine)

        for i in range(len(self.mq_coords)):
            # first machine queue coordinates
            mq_x = self.mq_coords[i][0][0]+41
            # first machine queue coordinates
            mq_y = self.mq_coords[i][0][1] + 21
            m_x = self.m_coords[i][0] + 21
            m_y = self.m_coords[i][1] + 41

            qp.setPen(pen)
            qp.drawLine(mq_x, mq_y, m_x, m_y)

    # Used to restart the simulator
    def restart(self):
        QCoreApplication.quit()
        QProcess.startDetached(sys.executable, sys.argv)

    def load_config(self, path_to_config='./api.json'):
        try:
            f = open(path_to_config)
        except FileNotFoundError as fnf_err:
            print(fnf_err)
            sys.exit()
        data = f.read()
        f.close()
        data = json.loads(data)
        self.data = data


def window():
    app = QApplication(sys.argv)
    win = GUI()
    win.show()
    app.exec_()


if __name__ == '__main__':
    window()
