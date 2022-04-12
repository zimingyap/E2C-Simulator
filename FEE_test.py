import unittest
from utils.schedulers.FEE import FEE
import utils.config as Config
from utils.task import Task
from utils.task_type import TaskType, UrgencyLevel
from utils.machine import Machine

class TestConfig(unittest.TestCase):
    Config.init()
    def test_low_priority_queue(self):
        tasks = []
        self.tasktype = TaskType(1,"name", UrgencyLevel.BESTEFFORT,1.0)
        tasks.append(Task(1,self.tasktype,5.335,2.421,0.701))
        tasks.append(Task(1,self.tasktype,5.335,2.421,0.701))
        tasks.append(Task(1,self.tasktype,5.335,2.421,0.701))

        scheduler = FEE(len(tasks))
        lpq = scheduler.low_priority_queue()
        self.assertGreater(len(lpq),0)
        
    def test_phase1(self):
        tasks = []
        specs = {'power':45.0,'idle_power':10.0}
        specs1 = {'power':90.0,'idle_power':15.0}

        Config.machines.append(Machine(1,1,Config.machine_types[0],specs))
        Config.machines.append(Machine(2,2,Config.machine_types[1],specs1))
        
        tasks.append(Task(1,Config.task_types[0],5.335,2.421,0.701))
        tasks.append(Task(2,Config.task_types[1],1.335,0.421,1.701))
        tasks.append(Task(3,Config.task_types[0],2.335,1.421,2.701))

        scheduler = FEE(len(tasks))
        scheduler.batch_queue.put(Task(1,Config.task_types[0],5.335,2.421,0.701))
        scheduler.batch_queue.put(Task(2,Config.task_types[1],1.335,0.421,1.701))
        scheduler.batch_queue.put(Task(3,Config.task_types[0],2.335,1.421,2.701))

        self.assertGreater(len(scheduler.phase1()),0)

    def test_phase_2(self):
        tasks = []
        self.tasktype = TaskType(1,"name", UrgencyLevel.BESTEFFORT,1.0)
        tasks.append(Task(1,self.tasktype,5.335,2.421,0.701))
        tasks.append(Task(1,self.tasktype,5.335,2.421,0.701))
        tasks.append(Task(1,self.tasktype,5.335,2.421,0.701))

        scheduler = FEE(len(tasks))
        pm = scheduler.phase1()
        print(scheduler.phase2(pm))

if __name__ == '__main__':
    unittest.main() 