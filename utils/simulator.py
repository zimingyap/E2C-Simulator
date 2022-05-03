"""
Author: Ali Mokhtari (ali.mokhtaary@gmail.com)
Created on Nov., 15, 2021


"""
import pandas as pd
import json
import time
import utils.config as config
from utils.event import Event, EventTypes
from utils.task import Task
from utils.schedulers.EE import EE
from utils.schedulers.MM import MM
from utils.schedulers.FEE import FEE
from utils.schedulers.FCFS import FCFS
from PyQt5.QtCore import QThread, pyqtSignal,QObject
class Simulator(QObject):
    progress = pyqtSignal(dict)
    def __init__(self, workload_id, epsiode_no, id = 0, verbosity = 0):         
        super(Simulator,self).__init__()      
        self.path_to_arrival = f"{config.settings['path_to_workload']}/workloads/workload-{workload_id}/workload-{epsiode_no}.csv"
        self.verbosity = verbosity
        self.id = id
        self.tasks = []
        self.total_no_of_tasks = []
        self.energy_statistics = []
        
        #for gui
        self.timer = 0 
        self.gui_statistic = {}
        self.check_sim = None
        self.total_tasks = None
        self.threadController = 1
    def create_event_queue(self):
        """In this function, csv file is convert into DataFrame. Tasks are created here with the 
        estimated time, execution time, arrival time from DataFrame. 
        Events are created here. The events are put inside event queue.
        """        

        #Read csv file into DataFrame
        df = pd.read_csv(self.path_to_arrival)
        est_clmns =[]
        ext_clmns = []

        for machine_type in config.machine_types:
            est_clmns.append(f'est_{machine_type.name}')
            for r in range(1,machine_type.replicas+1):
                ext_clmns.append(f'ext_{machine_type.name}-{r}')

        for idx in df.index:
            task_id = idx
            task_type_id = df.loc[idx,'task_type_id']
            arrival_time = df.loc[idx,'arrival_time']
            estimated_time = df.loc[idx, est_clmns]
            execution_time = df.loc[idx, ext_clmns]
            estimated_time = estimated_time.rename(lambda x: x.split('_')[1])
            execution_time = execution_time.rename(lambda x: x.split('_')[1])

            type = config.find_task_type(task_type_id)
            self.tasks.append(Task(task_id, type, estimated_time,
                                     execution_time, arrival_time))    
        self.total_no_of_tasks = len(self.tasks)
        self.total_tasks = len(self.tasks)
        
        for task in self.tasks:
            event = Event(task.arrival_time, EventTypes.ARRIVING, task)
            config.event_queue.add_event(event)
            
        

    def set_scheduling_method(self):
        """Set scheduling method based on the method defined in config.json
        - EE (energy-aware, energy-aware)
        - MM (min-completion, min-completion)
        - FEE (fair, energy-aware, energy-aware)
        - FCFS (first come first serve)
        """        
        if config.scheduling_method == 'EE':
            self.scheduler = EE(self.total_no_of_tasks)
        # elif self.scheduling_method == 'ME':
        #     self.scheduler = ME(self.total_no_of_tasks)
        elif config.scheduling_method == 'MM':
            self.scheduler = MM(self.total_no_of_tasks)
        elif config.scheduling_method == 'FEE':
            self.scheduler = FEE(self.total_no_of_tasks)
        # elif self.scheduling_method == 'RND':
        #     self.scheduler = RND(self.total_no_of_tasks)
        # elif self.scheduling_method == 'MSD':
        #     self.scheduler = MSD(self.total_no_of_tasks)
        # elif self.scheduling_method == 'MMU':
        #     self.scheduler = MMU(self.total_no_of_tasks)
        elif config.scheduling_method == 'FCFS':
            self.scheduler = FCFS(self.total_no_of_tasks)
        # elif self.scheduling_method == 'RLS':
        #     self.scheduler = RLS(self.total_no_of_tasks)
        # elif self.scheduling_method == 'TabRLS':
        #     self.scheduler = TabRLS(self.total_no_of_tasks)

        else:
            print('ERROR: Scheduler ' + config.scheduling_method + ' does not exist')
            self.scheduler = None
        
    def idle_energy_consumption(self):
        """Calculate energy consumption of idle machines
        """        
        for machine in config.machines:
                idle_time_interval = config.time.gct() - machine.idle_time
                if idle_time_interval >0:
                    idle_energy_consumption = machine.specs['idle_power'] * idle_time_interval                    
                    machine.idle_time = config.time.gct()
                else:
                    idle_energy_consumption = 0.0

                machine.stats['idle_energy_usage'] += idle_energy_consumption
                machine.stats['energy_usage'] += idle_energy_consumption
                config.available_energy -= idle_energy_consumption
                s = '\nmachine {} @{}\n\tidle_time:{}\n\tidle_time_interval:{}\n\tidle power consumption: {} '.format(
                    machine.id, config.time.gct(), machine.idle_time, idle_time_interval, idle_energy_consumption)
                #config.log.write(s)

    
    def run(self):       
        """Run the simulator after calling create_event_queue(),
        set_scheduling_method(), and idle_enerygy_consumption()
        """              
        # app = QApplication(sys.argv)
        # win = GUI()
        # win.show()
        # sys.exit(app.exec_())
        while config.event_queue.event_list and config.available_energy > 0.0:
            # use to pause the simulator
            # if config.gui == 1:
            #     print(self.threadController)
            #     while self.threadController == False:
            #         print("threadddd")  
            #         print("Simulation is paused")
            #         time.sleep(1)
            while self.threadController == 0:
                time.sleep(1)
            self.idle_energy_consumption()
            event = config.event_queue.get_first_event()
            task = event.event_details
            config.time.sct(event.time)
            s = '\nTask:{} \t\t {}  @time:{} '.format(
                task.id, event.event_type.name, event.time)
            config.log.write(s)
            if config.gui != 1:
                print(s)
            # print(s)
            row =[config.time.gct(),config.available_energy]

            for machine in config.machines:                
                row.append(machine.stats['energy_usage'])
            self.energy_statistics.append(row)
            
            # Task is added to the scheduler batch_queue and it is schedule to admit to the machine
            if event.event_type == EventTypes.ARRIVING:                
                self.scheduler.batch_queue.put(task)
                if config.gui == 1:
                    for i,v in enumerate(self.scheduler.batch_queue.list):
                        self.progress.emit({"Task id": v.id, "Event Type": 'INCOMING',"Type":'task'})
                # print(self.first_gui_task)
                ### add to gui batch_queue
                assigned_machine = self.scheduler.schedule() 
                if config.gui == 1 and assigned_machine != None:
                    time.sleep(self.timer)
                    self.progress.emit({"Task id":task.id,"Event Type":event.event_type.name,"Time":event.time, "Machine": assigned_machine.id, "Type":'task', "FROM":169})
                    time.sleep(self.timer)
                    self.progress.emit({"Task id":task.id,"Event Type":task.status.name, "Time":task.completion_time, "Machine": assigned_machine.id, "Type":'task', "FROM":171})
                    

            # Task is added to the scheduler batch_queue, if there are no available machines, 
            # the task will be drop
            elif event.event_type == EventTypes.DEFERRED:
                self.scheduler.batch_queue.put(task)   
                if config.gui == 1:
                    for i,v in enumerate(self.scheduler.batch_queue.list):
                        self.first_gui_task = {"Task id": v.id, "Event Type": 'DEFFERED',"Type":'task'}
                        self.progress.emit(self.first_gui_task) 
                ### add to gui batch_queue
                assigned_machine = self.scheduler.schedule()
                if assigned_machine == None:
                    break
                if config.gui == 1 :
                    time.sleep(self.timer)
                    self.progress.emit({"Task id":task.id,"Event Type":event.event_type.name,"Time":event.time, "Machine": assigned_machine.id, "Type":'task', "FROM":184})
                    time.sleep(self.timer)
                    self.progress.emit({"Task id":task.id,"Event Type":task.status.name, "Time":task.completion_time, "Machine": assigned_machine.id, "Type":'task', "FROM":186})
                    

            # Task will be terminated upon completion
            elif event.event_type == EventTypes.COMPLETION:                
                machine = task.assigned_machine
                if config.gui == 1:
                    time.sleep(self.timer)
                    self.progress.emit({"Task id":task.id,"Event Type":event.event_type.name, "Time":task.completion_time, "Machine": machine.id, "Type":'task', "FROM":197})
                ### add to gui batch_queue
                machine.terminate(task)      
                self.scheduler.schedule()

            # elif event.event_type == EventTypes.OFFLOADED:
            #     if self.verbosity >= 1:
            #         pbar.update(1)
            #     Config.cloud.terminate(task)
            #     self.scheduler.feed()
            #     num = 4
            #     assigned_machine = self.scheduler.schedule()

            # Drop current running task 
            elif event.event_type == EventTypes.DROPPED_RUNNING_TASK:
                machine = task.assigned_machine
                if config.gui == 1 :
                    time.sleep(self.timer)
                    self.progress.emit({"Task id":task.id,"Event Type":event.event_type.name,"Time":event.time, "Type":'task', "FROM":214})
                machine.drop()
                self.scheduler.schedule() 
                    # time.sleep(self.timer)
                    # self.progress.emit({"Task id":task.id,"Event Type":task.status.name,"Time":event.time, "Machine": machine.id, "Type":'task'})
            if assigned_machine == None:
                continue
            # if config.gui == 1 :
            #     time.sleep(self.timer)
            #     self.progress.emit({"Task id":task.id,"Event Type":event.event_type.name,"Time":event.time, "Machine": assigned_machine.id, "Type":'task'})
            #     if (assigned_machine.machine_log != self.check_sim):
            #         time.sleep(self.timer)
            #         self.progress.emit(assigned_machine.machine_log)
            #     self.check_sim = assigned_machine.machine_log
        
            
                          
    
   

    def report(self, path_to_report):        
        """Generate a report to the path

        Args:
            path_to_report (Path): Path where you want to report to store

        Returns:
            row,
            task report

        """ 
        df_detailed = pd.DataFrame()
        for task in self.tasks:
            if task.assigned_machine == None:
                assigned_machine = None
            else:
                assigned_machine = f'{task.assigned_machine.type.name}-{task.assigned_machine.replica_id}'
            detailed_dict = {
                'id':task.id,
                'type':task.type.name,
                'urgency':task.urgency.name,
                'status':task.status.name,
                'assigned_machine': assigned_machine, 
                'arrival_time':task.arrival_time,
                'execution_time':task.execution_time.to_dict(),
                'energy_usage': task.energy_usage,
                'start_time':task.start_time,
                'completion_time': task.completion_time,
                'missed_time':task.missed_time,
                'deadline': task.deadline - task.devaluation_window,
                'extended_deadline': task.deadline
            }            
            df_detailed = df_detailed.append(detailed_dict, ignore_index=True)
        df_detailed.to_csv(f'{path_to_report}/detailed-{self.id}.csv', index = False)

        total_assigned_tasks = 0
        total_completion = 0
        total_xcompletion = 0
        missed_urg = 0
        missed_be = 0
        

        for machine in config.machines:
            total_assigned_tasks += machine.stats['assigned_tasks']
            total_completion += machine.stats['completed_tasks']
            total_xcompletion += machine.stats['xcompleted_tasks']
            missed_urg += machine.stats['missed_URG_tasks']
            missed_be += machine.stats['missed_BE_tasks']
            completed_percent = 0
            xcompleted_percent = 0
            energy_percent = 0
            wasted_energy = 0
            if machine.stats['assigned_tasks'] != 0:
                completed_percent = machine.stats['completed_tasks'] / machine.stats['assigned_tasks']
                xcompleted_percent = machine.stats['xcompleted_tasks'] / machine.stats['assigned_tasks']
                energy_percent = machine.stats['energy_usage'] / config.total_energy
                wasted_energy = machine.stats['wasted_energy']

            s = '\nMachine: {:} (id#{:})  \n\t%Completion: {:2.1f} #: {:}\n\t%XCompletion:{:2.1f} #: {:}\n\t#Missed URG:{:1.2f}\n\tMissed BE:{:}\n\t%Energy: {:2.1f}\n\t%Wasted Energy: {:2.1f} '.format(
                machine.type.name,machine.id,
                100*completed_percent, machine.stats['completed_tasks'],
                100*xcompleted_percent, machine.stats['xcompleted_tasks'],
                machine.stats['missed_URG_tasks'],
                machine.stats['missed_BE_tasks'],
                100*energy_percent,
                100 * wasted_energy) 
            if config.gui == 1:
                d = {"Machine":machine.type.name, "Machine id": machine.id,
                    "%Completion": 100*completed_percent, "# of %Completion":machine.stats['completed_tasks'],
                    "%XCompletion":100*xcompleted_percent,"# of %XCompletion":machine.stats['xcompleted_tasks'],
                    "#Missed URG": machine.stats['missed_URG_tasks'],
                    "Missed BE":machine.stats['missed_BE_tasks'],
                    "%Energy":100*energy_percent,"%Wasted Energy":100 * wasted_energy}
                self.progress.emit(d)
            else:
                if self.verbosity <= 3 :
                    print(s)
                config.log.write(s)

        # total_completion_percent = 100 * (total_completion / self.total_no_of_tasks)
        # total_xcompletion_percent = 100 * (total_xcompletion / self.total_no_of_tasks)
        total_completion_percent = 100 * (total_completion / self.total_tasks)
        total_xcompletion_percent = 100 * (total_xcompletion / self.total_tasks)
        s = '\n%Total Completion: {:2.1f}'.format(total_completion_percent)
        s += '\n%Total xCompletion: {:2.1f}'.format(total_xcompletion_percent)
        s += '\n%deferred: {:2.1f}'.format(len(self.scheduler.stats['deferred']))
        s += '\n%dropped: {:2.1f}'.format(len(self.scheduler.stats['dropped']))
        
    
        if self.verbosity <= 3:
            print(s)
        config.log.write(s)

        
        d = {}
        for task_type in config.task_types:            
            for machine in config.machines:
                d [f'{task_type.name}_assigned_to_{machine.type.name}_{machine.replica_id}'] = 0
                d[f'{task_type.name}_completed_{machine.type.name}_{machine.replica_id}']=0
                d[f'{task_type.name}_xcompleted_{machine.type.name}_{machine.replica_id}'] = 0
                d[f'{task_type.name}_missed_{machine.type.name}_{machine.replica_id}']=0
                d[f'{task_type.name}_energy_{machine.type.name}_{machine.replica_id}']=0
                d[f'{task_type.name}_wasted-energy_{machine.type.name}_{machine.replica_id}']=0
        #print(d.keys())
        
        for task in self.tasks:            
            if task.assigned_machine != None:
                machine = task.assigned_machine
                d[f'{task_type.name}_assigned_to_{machine.type.name}_{machine.replica_id}'] +=1
                d[f'{task_type.name}_energy_{machine.type.name}_{machine.replica_id}'] += task.energy_usage
                d[f'{task_type.name}_wasted-energy_{machine.type.name}_{machine.replica_id}'] += task.wasted_energy
                if task.status.name == 'COMPLETED':
                    d[f'{task_type.name}_completed_{machine.type.name}_{machine.replica_id}'] +=1
                elif task.status.name == 'XCOMPLETED':
                    d[f'{task_type.name}_xcompleted_{machine.type.name}_{machine.replica_id}'] +=1
                elif task.status.name == 'MISSED':
                    d[f'{task_type.name}_missed_{machine.type.name}_{machine.replica_id}'] +=1
        task_report = pd.DataFrame(d, index= [self.id])
        task_report.iloc[:,:-2] /= (0.01*self.total_no_of_tasks)
        task_report.iloc[:,-2:] /= (0.01*config.total_energy)
        task_report = task_report.round(3)
    
        row = []
        consumed_energy = config.total_energy - config.available_energy
        no_of_completed_task = self.total_no_of_tasks*(total_completion_percent+total_xcompletion_percent)
        if no_of_completed_task != 0:
            energy_per_completion = consumed_energy / no_of_completed_task
        elif consumed_energy != 0 and no_of_completed_task == 0:
            energy_per_completion = float('inf')
        else:
            energy_per_completion = 0.0

        row.append(
            [self.id,self.total_no_of_tasks ,
            total_assigned_tasks, len(self.scheduler.stats['dropped']),
            missed_urg,
            missed_be,
            total_completion_percent, total_xcompletion_percent,
            total_completion_percent+total_xcompletion_percent,
            100*(consumed_energy/config.total_energy),            
            energy_per_completion ])
        
        self.gui_statistic["%Total Completion"] = total_completion_percent
        self.gui_statistic["%Total xCompletion"] = total_xcompletion_percent
        self.gui_statistic["%Deferred"] = len(self.scheduler.stats['deferred'])
        self.gui_statistic["%Dropped"] = len(self.scheduler.stats['dropped'])
        self.gui_statistic["totalCompletion%"] = total_completion_percent+total_xcompletion_percent
        self.gui_statistic["consumed_energy%"] = 100*(consumed_energy/config.total_energy)
        self.gui_statistic["energy_per_completion"] = energy_per_completion
        self.monitor()
        return row, task_report

    def setTimer(self,time=1):
        #for gui
        self.timer = time
        
    def simPause(self,value):
        self.threadController = value
        
     # This function is used to pass necessary information for GUI. 
    # Create a json file to store the data and pass it to GUI like API
    def monitor(self):
        """
        It writes the current state of the system to a json file
        """
        data = {}
        data['no_of_machine'] = config.no_of_machines
        data['scheduler'] = config.scheduling_method
        data['batch_queue_size'] = config.batch_queue_size
        data['machine_queue_size'] = config.machine_queue_size
        data['statistics'] = self.gui_statistic
        with open('api.json','w') as outfile:
            json.dump(data, outfile)

class WorkerThread(QThread):
    update_progress = pyqtSignal(dict)
    def run(self):
        for x in range(1,10):
            self.update_progress.emit({x:x*10})