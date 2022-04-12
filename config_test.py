from dataclasses import dataclass
import string
import unittest
from venv import create
import utils.config as config
from utils.machine import Machine
from utils.task_type import TaskType
from utils.machine_type import MachineType

class TestConfig(unittest.TestCase):

    def test_create_task_types(self):
        data = config.load_config()
        print(data['task_types'])
        task_types, task_type_names = config.create_task_types(data['task_types'])
        for i in range(len((task_types))):
            self.assertIsInstance(task_types[i],TaskType)
            self.assertTrue(type(task_type_names[i]),string)
        self.assertEqual(len(task_types),2)

    def test_create_machine_types(self):
        data = config.load_config()

        machine_types, machine_type_names, no_of_machines = config.create_machine_types(data['machines'])
        for i, v in enumerate(data['machines']):
            self.assertIsInstance(machine_types[i], MachineType)
            self.assertTrue(type(machine_type_names[i]), string)
            
        self.assertEqual(no_of_machines, 6)
        self.assertEqual(machine_types[1].id,2)

    def find_task_type(self):
        pass



if __name__ == '__main__':
    unittest.main()