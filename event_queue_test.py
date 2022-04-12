import unittest
import sys
sys.path.insert(0, '/Users/zimingyap/Documents/HPCC/V1/')

from utils.event_queue import EventQueue
from utils.event import Event


class TestConfig(unittest.TestCase):
    def test_add_event(self):
        e = Event(0,1,2)
        e1 = Event(1,2,3)
        e2 = "not Event"
        eq = EventQueue()
        eq.add_event(e)
        eq.add_event(e1)
        self.assertEqual(eq.event_list[0], e)
        self.assertRaises(TypeError,lambda: eq.add_event(e2))

    def test_get_first_event(self):
        e = Event(0,1,2)
        e1 = Event(1,2,3)
        eq = EventQueue()
        eq.add_event(e)
        eq.add_event(e1)
        first_event = eq.get_first_event()
        self.assertEqual(first_event, e)

    #not working
    def test_remove(self):
        e = Event(0,1,2)
        e1 = Event(1,2,3)
        eq = EventQueue()
        eq.add_event(e)
        eq.add_event(e1)
        eq.remove(Event(0,1,2))
        self.assertNotIn(e, eq.event_list)

    def test_reset(self):
        e = Event(0,1,2)
        e1 = Event(1,2,3)
        eq = EventQueue()
        eq.add_event(e)
        eq.add_event(e1)
        eq.reset()
        self.assertEqual(len(eq.event_list),0)
if __name__ == '__main__':
    unittest.main()