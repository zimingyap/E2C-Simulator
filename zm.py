import sys
import json
import utils.config as config
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

)
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import (
    QPropertyAnimation,
    Qt,
    QPoint,
    QThread,
    QSequentialAnimationGroup,
)

import csv
from os import makedirs

from utils.simulator import Simulator
from utils.machine import Machine
import utils.config as config


class Statistic(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("border:1px solid;")
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        
        self.TotalCompletion = QLabel(self)
        self.TotalCompletion.setText("%Total Completion: {}".format(0))
        self.TotalCompletion.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.layout.addWidget(self.TotalCompletion, 0, 0)
        
        self.TotalxCompletion = QLabel(self)
        self.TotalxCompletion.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.TotalxCompletion.setText("%Total xCompletion: {}".format(0))
        self.layout.addWidget(self.TotalxCompletion, 0, 1)
        
        self.deffered = QLabel(self)
        self.deffered.setText("%Deffered: {}".format(0))
        self.deffered.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.layout.addWidget(self.deffered, 0, 2)

        self.dropped = QLabel(self)
        self.dropped.setText("%Dropped: {}".format(0))
        self.dropped.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.layout.addWidget(self.dropped, 1, 0)
        
        self.totalCompletion = QLabel(self)
        self.totalCompletion.setText("totalCompletion%: {}".format(0))
        self.totalCompletion.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.layout.addWidget(self.totalCompletion, 1, 1)

        self.consumedEnergy = QLabel(self)
        self.consumedEnergy.setText("ConsumedEnergy%: {}".format(0))
        self.consumedEnergy.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.layout.addWidget(self.consumedEnergy, 1, 2)
        
        self.energyPerCompletion = QLabel(self)
        self.energyPerCompletion.setText("energy_per_completion: {}".format(0))
        self.energyPerCompletion.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.layout.addWidget(self.energyPerCompletion, 2, 1)



class GUI_SIM(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("border:1px solid;")
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)



class GUI(QMainWindow):
    def __init__(self):
        super(GUI, self).__init__()
        # 5 colors, each color represent a task. Illustrate that a task is moving forward when the first task is pop to scheduler
        # config.init()
        self.color = ["background-color:lightgreen", "background-color:lightblue",
                      "background-color:lightsalmon", "background-color:lightpink", "background-color:lightgoldenrodyellow"]
        self.no_of_task = 100  # need to read from somewhere
        self.tasks = []
        self.machine_stats = []
        self.machine_stats_btn = []
        self.m_coords = {}
        self.mq_coords = {}  # machine queue coordinates
        self.bq_coords = {}
        self.mq_availability = {}
        self.machine_availability = {}
        self.batch_queue_availability = {}
        self.data = load_config()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 2200, 1000)
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
        self.create_menu_bar()
        self.draw_batch_queue()
        self.scheduling()
        self.draw_machine()
        self.conLine = QPainter(self)
        self.conLine.begin(self)
        self.conLine.setPen(Qt.red)
        self.conLine.drawLine(10,10,100,140)
        for i in range(len(self.m_coords)):
            b = QPushButton(self)
            b.setGeometry(self.m_coords[i][0]+200,self.m_coords[i][1],70,40)
            b.setText("Details")
            b.setVisible(False)
            self.machine_stats_btn.append(b)
            self.machine_stats_btn[i].clicked.connect(lambda: self.create_machine_stat(i))
        # self.create_machine_btn
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
        path_to_result = f'{config.settings["path_to_output"]}/data/{workload}/{scheduling_method}'
        makedirs(path_to_result, exist_ok=True)
        report_summary = open(f'{path_to_result}/results-summary.csv', 'w')
        summary_header = ['Episode', 'total_no_of_tasks', 'mapped', 'cancelled', 'URG_missed', 'BE_missed',
                          'Completion%', 'xCompletion%', 'totalCompletion%', 'consumed_energy%', 'energy_per_completion']
        writer = csv.writer(report_summary)
        writer.writerow(summary_header)
        count = 0

        for i in range(low, high):
            s = '\n\n' + 15 * '='+' EPISODE#'+str(i)+' ' + 15 * '='
            config.log.write(s)
            print(s)
            count += 1
            Tasks = []
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
            self.pauseBtn = QPushButton("Pause", self)
            self.pauseBtn.setGeometry(30, 800, 100, 50)
            self.pauseBtn.clicked.connect(lambda: self.simulation.setTimer(10000))
            self.endBtn = QPushButton("End", self)
            self.endBtn.setGeometry(30, 850, 100, 50)
            self.endBtn.clicked.connect(lambda: self.endThread())
            self.slider = QSlider(self)
            self.slider.setGeometry(200, 760, 200, 40)
            self.slider.setOrientation(Qt.Horizontal)
            self.slider.setMinimum(0)
            self.slider.setMaximum(3000)
            self.slider.setSliderPosition(self.timer)
            self.slider.valueChanged.connect(self.updateSlider)
            self.slider.valueChanged.connect(self.speed)
            
            self.sliderLabel = QLabel(self)
            self.sliderLabel.setGeometry(400, 760, 200, 40)
            self.sliderLabel.setText("{:.1f}x".format(self.timer/1000))
            self.thread.finished.connect(lambda: self.simulation.report(path_to_result))
            self.thread.finished.connect(self.statistics_info)
            self.thread.finished.connect(self.set_Vis)
            
                

    def set_Vis(self):
        for i in range(len(self.machine_stats_btn)):
            self.machine_stats_btn[i].setVisible(True)
    
    def endThread(self):
        # if self.simulation.threadController == True:
        #     self.simulation.simPause(False)
        #     self.pauseBtn.setText("Resume")
        # else:
        #     self.simulation.simPause(True)
        #     self.pauseBtn.setText("Pause")s
        self.simulation.threadController = False
        self.thread.terminate()
        self.thread.wait()
        # self.thread.exit()
        

    def speed(self, value):
        self.simulation.setTimer(value/1000)
    
    def updateSlider(self,value):
        self.sliderLabel.setText("{:.1f}x".format(value/1000,"2f"))
    
    def handle_signal(self, d):
        print(d)
        if 'Type' in d:
            self.taskAnimation(120, 520, d)
        elif '%Completion' in d:
            self.machine_stats.append(d)
            
    # def create_machine_btn(self):
        
    #     # b.clicked.connect(lambda: self.create_machine_stat(self.machine_stats[i]))
    #     # self.machine_stats_btn.append(b)
                
    
    def create_machine_stat(self,i):
        a = QMessageBox(self)
        a.setText("{}".format(self.machine_stats[i]))
        a.setWindowTitle("Machine {}".format(self.machine_stats[i]['Machine id']))
        a.setStandardButtons(QMessageBox.Ok)
        a.setIcon(QMessageBox.Information)
        a.exec()
        
            
    def create_menu_bar(self):
        menuBar = self.menuBar()
        # Creating menus using a QMenu object
        fileMenu = QMenu("&File", self)
        editMenu = QMenu("&Edit", self)
        helpMenu = QMenu("&Help", self)
        menuBar.addMenu(fileMenu)
        menuBar.addMenu(editMenu)
        menuBar.addMenu(helpMenu)

    def statistics_info(self):
        self.statistic.TotalCompletion.setText("%Total Completion: {:.3f}".format(self.data['statistics']['%Total Completion']))
        self.statistic.TotalxCompletion.setText("%Total xCompletion: {:.3f}".format(self.data['statistics']['%Total xCompletion']))
        self.statistic.deffered.setText("%Deferred: {:.3f}".format(self.data['statistics']['%Deferred']))
        self.statistic.dropped.setText("%Dropped: {:.3f}".format(self.data['statistics']['%Dropped']))
        self.statistic.totalCompletion.setText("totalCompletion%: {:.3f}".format(self.data['statistics']['totalCompletion%']))
        self.statistic.consumedEnergy.setText("ConsumedEnergy%: {:.3f}".format(self.data['statistics']['consumed_energy%']))
        self.statistic.energyPerCompletion.setText("energy_per_completion: {:.3f}".format(self.data['statistics']['energy_per_completion']))

    def draw_batch_queue(self):
        overload = None
        if (self.data['batch_queue_size'] <= 4):
            batch_queue_size = self.data['batch_queue_size']
        else:
            batch_queue_size = 4
            overload = True
        x = 220
        y = 600
        for i in range(batch_queue_size):
            self.batch_queue_availability[i] = True
            self.bq_coords[i] = [x,y]
            box = QLabel(self)
            box.setGeometry(x, y, 41, 41)
            box.setFrameShape(QFrame.Box)
            x -= 40
        if (overload):
            overload_dot = QLabel(self)
            overload_dot.setGeometry(100, y, 41, 41)
            overload_dot.setText("...")
            overload_dot.setAlignment(Qt.AlignCenter)

    def taskAnimation(self, x, y, d):
       
        self.tasks[d["Task id"]].resize(35, 35)
        self.tasks[d["Task id"]].setStyleSheet(self.color[d["Task id"] % 5])
        self.tasks[d["Task id"]].setText("{}".format(d["Task id"]))
        self.tasks[d["Task id"]].setAlignment(Qt.AlignCenter)
        self.anim = QPropertyAnimation(self.tasks[d["Task id"]], b"pos")
        

        # task arriving into batch queue, ready to go into scheduler
        if d['Event Type'] == 'INCOMING':
            for i,v in enumerate(self.batch_queue_availability):
                if v == True:
                    self.anim.setDuration(1000)
                    self.anim.setStartValue(QPoint(x, 600))
                    self.anim.setEndValue(QPoint(self.bq_coords[i][0], self.bq_coords[i][1]+1))
                    self.anim.setStartValue(QPoint(self.bq_coords[i][0], self.bq_coords[i][1]+1))
                    self.anim.setEndValue(QPoint(y, 600))
                    
                    v == False
            
        elif d['Event Type'] == "ARRIVING":
            for i,v in enumerate(self.mq_availability[d['Machine']]):
                if v == True:
                    coord_x = self.mq_coords[d['Machine']][len(self.mq_availability[d['Machine']])-i-1][0]
                    coord_y = self.mq_coords[d['Machine']][len(self.mq_availability[d['Machine']])-i-1][1]
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
            self.anim.setStartValue(QPoint( mq_coord_x + 3, mq_coord_y + 3))
            self.anim.setEndValue(QPoint(coord_x+20, coord_y+15))
            self.anim.setDuration(100)
        elif d['Event Type'] == "COMPLETION":
            coord_x = self.m_coords[d['Machine']][0]
            coord_y = self.m_coords[d['Machine']][1]
            self.anim.setStartValue(QPoint(coord_x, coord_y))
            self.anim.setEndValue(QPoint(self.m_coords[d['Machine']][0]+100, self.m_coords[d['Machine']][1]))
            self.anim.setDuration(100)
            self.anim.stop()
        elif d['Event Type'] == "DROPPED_RUNNING_TASK":
            mq_coord_x = self.mq_coords[d['Machine']][0][0]
            mq_coord_y = self.mq_coords[d['Machine']][0][1]
            coord_x = self.m_coords[d['Machine']][0]
            coord_y = self.m_coords[d['Machine']][1]
            self.anim.setStartValue(QPoint(coord_x+20, coord_y+15))
            self.anim.setEndValue(QPoint( mq_coord_x + 3, mq_coord_y + 3))
            self.anim.setDuration(100)
            
            # self.tasks[d["Task id"]].deleteLater()
        elif d['Event Type'] == "MISSED":
            # self.tasks[d["Task id"]].deleteLater()
            pass
        
        elif d['Event Type'] == 'FINISH':
            self.thread.requestInterruption()
            self.thread.wait()
            self.thread.quit()            
        self.anim.start()
        
    def scheduling(self):
        scheduling_method = self.data['scheduler']
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

    def draw_machine(self):
        machine_name = []
        config.init()

        for i in config.machine_types:
            for _ in range(i.replicas):
                machine_name.append(i.name)
        y_axis = 200
        y_axis_size = 800
        y_axis_diff = int(y_axis_size/(len(machine_name)+1))
        machine_queue_overload = None
        if (self.data['machine_queue_size'] <= 4):
            machine_queue_size = self.data['machine_queue_size']
        else:
            machine_queue_size = 4
            machine_queue_overload = True
        for i in range(len(machine_name)):
            self.machine_availability[i] = True
            x_axis = 1100
            y_axis += y_axis_diff
            m = QLabel(self)
            m.move(x_axis+100, y_axis-20)
            self.m_coords[i] = [x_axis+100,y_axis-20]
            m.resize(80, 80)
            if machine_name[i] == 'cpu':
                m.setStyleSheet("""
               QLabel {
                  border: 3px solid black;
                  border-radius: 40px;
                  background-color:lightgreen;
                  }
               """)
            else:
                m.setStyleSheet("""
               QLabel {
                  border: 3px solid black;
                  border-radius: 40px;
                  background-color:lightblue;
                  }
               """)
            m.setText("{}".format(machine_name[i]))
            m.setAlignment(Qt.AlignCenter)
            mq_c = []
            mq_a = []
            for _ in range(machine_queue_size):
                x_axis -= 40
                self.draw_machine_queue(x_axis, y_axis)
                # self.mq_coords.append({i:[x_axis,y_axis]})
                mq_c.append([x_axis, y_axis])
                mq_a.append(True)
            self.mq_coords[i] = mq_c
            self.mq_availability[i] = mq_a
            if (machine_queue_overload):
                overload_dot = QLabel(self)
                overload_dot.setGeometry(940, y_axis, 41, 41)
                overload_dot.setText("...")
                overload_dot.setAlignment(Qt.AlignCenter)
  
            
            # Collect all the task that are completed    
            
                
            for i in range(len(self.m_coords)):
                t = QLabel(self)
                t.move(self.m_coords[i][0]+100, self.m_coords[i][1])
                t.resize(80, 80)
                t.setStyleSheet("""
               QLabel {
                  border: 3px solid black;
                  background-color: #737d84;
                  }
               """)
                

    def draw_machine_queue(self, x, y): 
        mq = QLabel(self)
        mq.setFrameShape(QFrame.Box)
        mq.setGeometry(x, y, 41, 41)

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.bq_sch_Lines(qp)
        self.sch_m_Lines(qp)
        qp.end()

    # draw line from batch queue to scheduler
    def bq_sch_Lines(self, qp):
        pen = QPen(Qt.black, 2, Qt.DashLine)
        sch_x = 500+85
        sch_y = 580+41
        for i in range(len(self.mq_coords)):
            m_x = self.mq_coords[i][len(self.mq_coords)-1][0]#first machine queue coordinates
            m_y = self.mq_coords[i][len(self.mq_coords)-1][1] +21#first machine queue coordinates
            qp.setPen(pen)
            qp.drawLine(sch_x, sch_y, m_x, m_y)
    #draw lines from scheduler to machine queue
    def sch_m_Lines(self, qp):
        pen = QPen(Qt.black, 2, Qt.DashLine)
        bq_x = self.bq_coords[0][0] +41#first batch queue coordinates
        bq_y = self.bq_coords[0][1] +21#first batch queue coordinates
        sch_x = 500
        sch_y = 580+41.25
        qp.setPen(pen)
        qp.drawLine(bq_x, bq_y, sch_x, sch_y)
        
def load_config(path_to_config='./api.json'):
    try:
        f = open(path_to_config)
    except FileNotFoundError as fnf_err:
        print(fnf_err)
        sys.exit()
    data = f.read()
    f.close()
    data = json.loads(data)
    return data


def window():
    app = QApplication(sys.argv)
    win = GUI()
    win.show()
    app.exec_()
    # sys.exit(app.exec_())


if __name__ == '__main__':
    window()
