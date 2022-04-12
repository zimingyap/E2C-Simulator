import sys
sys.path.insert(0, '/Users/zimingyap/Documents/HPCC/V1/')
from utils.queue import Queue
import unittest

class TestConfig(unittest.TestCase):

    def test_qsize_0(self):
        queue = Queue(maxsize=10)
        self.assertEqual(queue.qsize(), 0)

    def test_put(self):
        queue = Queue(maxsize=10)
        queue.put("task1")
        self.assertIn("task1", queue.list)

    def test_get(self):
        queue = Queue(maxsize=10)
        queue.put("task1")
        queue.put("task3")
        queue.put("task2")
        queue.put("task4")
        self.assertEqual(queue.get(),"task1")

    def test_remove(self):
        queue = Queue(maxsize=10)
        queue.put("task1")
        queue.put("task3")
        queue.put("task2")
        queue.put("task4")
        queue.remove("task1")
        self.assertNotIn("task1", queue.list)