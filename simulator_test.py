from asyncio import Task
from distutils.command import config
import unittest
import utils.config as Config
from utils.event import Event
from utils.simulator import Simulator
from utils.task import Task
from utils.schedulers.FEE import FEE

class TestConfig(unittest.TestCase):
    Config.init()
    def test_create_event_queue(self):
        sim = Simulator('0-0',0)
        sim.create_event_queue()
        print()
        self.assertIsInstance(sim.tasks[0], Task)
        self.assertIsInstance(Config.event_queue.event_list[0], Event)

    def test_set_scheduling_method(self):
        sim = Simulator('0-0',0)
        sim.set_scheduling_method()
        self.assertIsInstance(sim.scheduler, FEE)      

    def test_run(self):
        sim = Simulator('0-0',0)
        sim.set_scheduling_method()
        # sim.run()


if __name__ == '__main__':
    unittest.main() 