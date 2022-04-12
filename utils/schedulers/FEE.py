"""
Author: Ali Mokhtari (ali.mokhtaary@gmail.com)
Created on Nov., 15, 2021


"""
import numpy as np

from utils.base_task import TaskStatus
from utils.base_scheduler import BaseScheduler
import utils.config as config


class FEE(BaseScheduler):
    
    def __init__(self, total_no_of_tasks):
        super().__init__()
        self.name = 'FEE'
        self.total_no_of_tasks = total_no_of_tasks
        self.priority_queue = []
        
        
            
    def choose(self, index=0):
        task = self.batch_queue.get(index)     
        self.unmapped_task.append(task)
        s =f'\nTask {task.id} is chosen:\n['
        for t in self.batch_queue.list:
            s += f'{t.id} , '
        s+=']'
        config.log.write(s)
        return task
    
    
    def defer(self, task):
        if config.time.gct() > task.deadline:
            self.drop(task)
            return 1
        self.unmapped_task.pop()
        task.status =  TaskStatus.DEFERRED
        task.no_of_deferring += 1
        self.batch_queue.put(task)
         
        self.stats['deferred'].append(task)
        s = '\n[ Task({:}),  _________ ]: Deferred       @time({:3.3f})'.format(
           task.id, config.time.gct())
        config.log.write(s)

    def drop(self, task):
        self.unmapped_task.pop()
        task.status = TaskStatus.CANCELLED
        task.drop_time = config.time.gct()
        self.stats['dropped'].append(task)        
        s = '\n[ Task({:}),  _________ ]: Cancelled      @time({:3.3f})'.format(
            task.id, config.time.gct()       )
        config.log.write(s)

    def map(self, machine):
        task = self.unmapped_task.pop()
        assignment = machine.admit(task)
        if assignment != 'notEmpty':
            task.assigned_machine = machine
            self.stats['mapped'].append(task)
        else:
            self.defer(task)

    
    def low_priority_queue(self):
        """Task that has high completion rate will be drop and make space for tasks that have low completion rate.

        Returns:
            list: tasks that has high completion rate or completed
        """        
        low_priority_tt = []        
        values = []
        
        for tt in config.task_types:
            arrived = self.stats[f'{tt.name}-arrived']
            completed = 0
            for machine in config.machines:                
                completed += machine.stats[f'{tt.name}-completed']
            if arrived > 0 :
                value = completed / arrived              
            else:
                value = 0.0
            self.stats[f'{tt.name}-overall'] = value
            values.append(value)
        values = np.array(values)
        mean = values.mean()
        std = values.std()

        for tt in config.task_types:
            value = self.stats[f'{tt.name}-overall']
            if mean > value :                
                low_priority_tt.append(tt)


        # low_priority_tt = []
        # for tt in Config.task_types:
        #     if tt.name == 'TT2':
        #         #print('TT2')
        #         low_priority_tt.append(tt)
                 
            
        return low_priority_tt
    
    def phase1(self):
        """Each task has a deadline, machines will be selected if the task can be completed before the deadline in the machines


        Returns:
            list: attributes of task needed to map during phase 2
        """        
        deadline_met = []
        provisional_map = []

        low_priority_tt = self.low_priority_queue()

        index = 0 
        for task in self.batch_queue.list:            
            machines_met_deadline = []  
            
            for machine in config.machines:                
                pct = machine.provisional_map(task)               
                
                if pct < task.deadline:                                                        
                    machines_met_deadline.append(machine)

            if not machines_met_deadline and task.type in low_priority_tt:
                    fastest_machine = min(task.estimated_time, key=task.estimated_time.get)                    
                    for machine in config.machines:
                        if machine.type.name == fastest_machine:
                            fastest_machine = machine                    
                    
                    for candid_for_drop in reversed(fastest_machine.queue):
                        if candid_for_drop.type not in low_priority_tt:
                            fastest_machine.cancel(candid_for_drop)
                        pct = fastest_machine.provisional_map(task)
                        if pct < task.deadline:                         
                            machines_met_deadline.append(machine)
                            break   

            deadline_met.append([task,index,machines_met_deadline])
            index += 1
        
        for item in deadline_met:
            task = item[0]
            index = item[1]
            machines = item[2]
            min_ec = float('inf')
            min_ec_machine = None 
            
            for machine in machines: 
                pec = machine.specs['power'] * task.estimated_time[machine.type.name]                           
                if pec < min_ec:
                    min_ec = pec
                    min_ec_machine = machine                
            provisional_map.append([task, min_ec, min_ec_machine, index])
            
        return provisional_map
    

    def phase2(self, provisional_map):
        """the machine that provides the minimum completion time will be selected if there are any

        Args:
            provisional_map (list): attributes of task from phase 1

        Returns:
            provisional_map (list): attributes of task from phase 1
        """        
        provisional_map_machines = []
        low_priority_tt = self.low_priority_queue()
        low_priority_map = []
        high_priority_map = []

        for pair in provisional_map:
            task = pair[0]
            if task.type in  low_priority_tt:
                low_priority_map.append(pair)
            else:
                high_priority_map.append(pair)
        rnd = np.random.random()
        if (rnd < config.fairness_factor) and (low_priority_map):
            provisional_map = low_priority_map
              
        for machine in config.machines:                   
            if not machine.queue.full():
                min_ec =float('inf')
                task = None
                index = None 
                for pair in provisional_map:                                                         
                    if pair[2] != None and machine.id == pair[2].id and pair[1] < min_ec:
                        task = pair[0]
                        min_ec = pair[1]
                        index = pair[3]
                provisional_map_machines.append([task,machine,min_ec,index ])        
        return provisional_map_machines


    def schedule(self): 
        """If there are no available machine, defers for a few times and dropped if still no available machines


        Returns:
        """               
        provisional_map = self.phase1()
        
        for item in provisional_map:
            #print(item[0].id, item[2].type.name)
            task = item[0]
            machine = item[2]
            
            if  machine == None:
                index = self.batch_queue.list.index(task)
                task = self.choose(index)                
                if task.no_of_deferring <= 2:
                    self.defer(task)                    

                else:                    
                    self.drop(task)   
                            
        provisional_map_machines = self.phase2(provisional_map)      
        
        for pair in provisional_map_machines:               
            task = pair[0]
            assigned_machine = pair[1]
            
            if task != None :                  
                index = self.batch_queue.list.index(task)                                               
                task = self.choose(index)
                self.map(assigned_machine)
                
                return assigned_machine
                
            
        return None
            
    #####
    