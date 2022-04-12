"""
Author: Ali Mokhtari (ali.mokhtaary@gmail.com)
Created on Nov., 15, 2021


"""

from utils.base_task import TaskStatus
from utils.base_scheduler import BaseScheduler
import utils.config as config


class EE(BaseScheduler):
    
    def __init__(self, total_no_of_tasks):
        super().__init__()
        self.name = 'EE'
        self.total_no_of_tasks = total_no_of_tasks
        
        
            
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
    
    def phase1(self):
        """Each task has a deadline, machines will be selected if the task can be completed before the deadline in the machines


        Returns:
            list: attributes of task needed to map during phase 2
        """        
        deadline_met = []
        provisional_map = []
        
        index = 0 
        for task in self.batch_queue.list:            
            machines_met_deadline = []  
            #check which machine offers the lowest completion time
            for machine in config.machines:                
                pct = machine.provisional_map(task) 
                # if completion time is before deadline, append to machines_met_deadline 
                if pct < task.deadline:                                                        
                    machines_met_deadline.append(machine)
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
                # pec = machine.specs['power'] * 2.02                           
                if pec < min_ec:
                    min_ec = pec
                    min_ec_machine = machine                
            provisional_map.append([task, min_ec, min_ec_machine, index])
            
        return provisional_map
    

    def phase2(self, provisional_map):
        """The machine that provides the minimum completion time will be selected if there are any


        Args:
            provisional_map (list): attributes of task from phase 1

        Returns:
            list: [task,machine,min_ec,index]
        """        
        provisional_map_machines = []        
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
            assigned_machine: the assigned machine for each task
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
    