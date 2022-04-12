import unittest
# import sys
# sys.path.insert(0, '/Users/zimingyap/Documents/HPCC/V1/')
from utils.machine import Machine
from utils.machine_type import MachineType
from utils.task import Task
from utils.task_type import TaskType

from utils.base_machine import BaseMachine, MachineStatus
import utils.config as config
from utils.task_type import UrgencyLevel

class TestConfig(unittest.TestCase):
    config.init()
    
    def is_working(self):
        """Check if there are any running tasks in the machine

        Returns:
            bool: True if there are any tasks in running_task, else False
        """
        return True
    def test_reset(self):
        specs = {'power':45.0,'idle_power':10.0}
        machine = Machine(0,1,2,specs)
        machine.status = MachineStatus.WORKING
        machine.running_task.append("task1")
        machine.completed_tasks.append("task2")
        machine.xcompleted_tasks.append("task3")
        machine.missed.append("task3")
        # machine.stats.append(10)
        # machine.stats.append(120)
        # machine.stats.append(102)
        machine.reset()
        self.assertEqual(machine.status, MachineStatus.IDLE)

    def test_get_completion_time(self):
        specs = {'power':45.0,'idle_power':10.0}
        self.type= MachineType(1,"cpu",45.0,10.0,4)
        machine = Machine(1,1,self.type,specs)
        self.tasktype = TaskType(1,"name", UrgencyLevel.BESTEFFORT,1.0)
        self.idle_time = 0.0
        self.task = Task(1,self.tasktype,5.335,2.421,0.701)
        self.type = self.task.type
        self.replica_id = 2
        completion_time, running_time, _ = machine.get_completion_time(self.task)
        self.assertGreater(completion_time, 0)
        self.assertGreater(running_time, 0)

    def test_provisional_map(self):
        tasks = []
        specs = {'power':45.0,'idle_power':10.0}
        machine = Machine(1,1,config.machine_types[0],specs)
        config.machines.append(machine)
        
        tasks.append(Task(1,config.task_types[0],5.335,2.421,0.701))
        tasks.append(Task(2,config.task_types[1],1.335,0.421,1.701))
        tasks.append(Task(3,config.task_types[0],2.335,1.421,2.701))
        for i in tasks:
            self.assertGreater(machine.provisional_map(i),0)

    # def test_execute(self):
    #     tasks = []
    #     specs = {'power':45.0,'idle_power':10.0}
    #     machine = Machine(1,1,config.machine_types[0],specs)
    #     config.machines.append(machine)
        
    #     tasks.append(Task(1,config.task_types[0],5.335,2.421,0.701))
    #     tasks.append(Task(2,config.task_types[1],1.335,0.421,1.701))
    #     tasks.append(Task(3,config.task_types[0],2.335,1.421,2.701))
    #     for i in tasks:
    #         machine.execute(i)

    def test_drop(self):
        tasks = []
        specs = {'power':45.0,'idle_power':10.0}
        machine = Machine(1,1,config.machine_types[0],specs)
        config.machines.append(machine)
        
        tasks.append(Task(1,config.task_types[0],5.335,2.421,0.701))
        # tasks.append(Task(2,config.task_types[1],1.335,0.421,1.701))
        # tasks.append(Task(3,config.task_types[0],2.335,1.421,2.701))
        machine.running_task.append(Task(1,config.task_types[0],5.335,2.421,0.701))
        print(machine.drop())

if __name__ == '__main__':
    unittest.main()
