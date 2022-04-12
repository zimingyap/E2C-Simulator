"""
Author: Ali Mokhtari (ali.mokhtaary@gmail.com)
Created on Nov., 15, 2021


"""

from utils.base_task import TaskStatus
from utils.base_scheduler import BaseScheduler
import utils.config as config

class MM(BaseScheduler):
    

    def __init__(self, total_no_of_tasks):
        super().__init__()
        self.name = 'MM'
        self.total_no_of_tasks = total_no_of_tasks
        

    def choose(self, index=0):
        task = self.batch_queue.get(index)     
        self.unmapped_task.append(task)        
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
    
    def phase1(self):
        """Each task will be paired with a machine that offers minimum expected completion time

        Returns:
            list: attributes of task needed to map during phase 2
        """        
        provisional_map = []
        index = 0 
        for task in self.batch_queue.list:
            min_ct = float('inf')
            min_ct_machine = None
            for machine in config.machines:
                pct = machine.provisional_map(task)
                if pct < min_ct:
                    min_ct = pct
                    min_ct_machine = machine                
            provisional_map.append([task, min_ct, min_ct_machine, index])
            index += 1        
        
        return provisional_map
    

    def phase2(self, provisional_map):
        """There will be more than 1 task for a single machine, so the machines will select the pair in phase 1 that offers the minimum expected completion time


        Args:
            provisional_map (list): attributes of task from phase 1

        Returns:
            list: [task, machine, index]
        """        
        provisional_map_machines = []        
        for machine in config.machines:
            if not machine.queue.full():
                min_ct =float('inf')
                task = None
                index = None
                for pair in provisional_map:                    
                    if pair[2] != None and pair[2].id == machine.id and pair[1] < min_ct:
                        task = pair[0]
                        min_ct = pair[1]
                        index = pair[3]   
                provisional_map_machines.append([task,machine,index])

        return provisional_map_machines



    def schedule(self):
        
        provisional_map = self.phase1()
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
    