"""
Authors: Ali Mokhtari, Chavit Denninnart
Created on Dec. 18, 2020.

In simulation mode, all events (e.g arriving a task or completing the
task) are queued in EventQueue.In this way, the processing of a task
in real-world can be imitated.
The EventQueue is firstly empty. By arriving the first task, an event
which is "arriving a new task" is added to the head of queue. In the
same way, other events are added to the queue. 
Moreover, the queue is always sorted based on the event's time.
Heap sort technique is used to sort the queue.

"""
import heapq
#Begin code changes by Ziming
from utils.event import Event
# import event as Event
#End 
class EventQueue:
    # All events are queued in EventQueue.
    #
    # event_list: It is the list of events in the queue. event_list has
    # Min-heap data structure. It can help sorting the queue based on the
    # event.time with reasonable time complexity.

    event_list = []

    def add_event(self, event):
        """
        **add_event** takes an event object and inserts it into the event_list
        
        :param event: The event to be added to the event list
        """
               
        # Insert an event into the event_list.
        if isinstance(event, Event):
            heapq.heappush(self.event_list, event)
        else:
            raise TypeError

    def get_first_event(self):
        """
        It returns the event with the smallest time
        :return: The event with the smallest time.
        """
        if self.event_list:  # it checks that event_list is non-empty
            return heapq.heappop(self.event_list)
        else:
            return Event(None, None, None)

    def remove(self, event):
        """
        It removes the event from the event_list. Then, the resulted
        event_list is heapified again.
        
        :param event: The event to be removed
        """
        print(self.event_list)
        print('\n\n\n')
        self.event_list.remove(event)
        heapq.heapify(self.event_list)
    
    def reset(self):
        """
        It resets the event list to an empty list.
        """
        self.event_list = []
