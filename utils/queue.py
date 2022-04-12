"""
Authors: Ali Mokhtari (ali.mokhtaary@gmail.com)
Created on Jan, 26, 2022

Description:


"""
"""
Authors: Ali Mokhtari (ali.mokhtaary@gmail.com)
Created on Jan, 26, 2022

Description:


"""
import sys 

class Queue:

    def __init__(self, maxsize):
        self.maxsize = maxsize
        self.list = []
        
    def qsize(self):
        """Return the size of the queue

        Returns:
            int: size of the queue
        """        
        return len(self.list)

    def empty(self):
        """Check if queue is empty or not

        Returns:
            bool
        """        
        return not bool(self.list)
    
    def full(self):
        """Check if queue is full or not

        Returns:
            _type_: _description_
        """        
        return self.qsize() == self.maxsize
    
    def put(self, item):
        """Append an item inside the queue

        Args:
            item (Any): Any

        Raises:
            FullQueueError: _description_
        """        
        try:
            if self.full():
                raise FullQueueError(item)
            else:
                self.list.append(item)
        except FullQueueError as err:
            print(err)
            sys.exit()
    
    def get(self, index = 0):    
        """Get an item from queue based on index

        Args:
            index (int, optional): _description_. Defaults to 0.

        Returns:
            Any: item in the queue
        """                    
        try:
            self.list[index]                   
        except IndexError as val_err:
            print(val_err)
            print(f'index {index} is out of range of list {self.list}')
            sys.exit()
        return self.list.pop(index)
        
        
    
    def remove(self, item):
        """Remove an item in the queue

        Args:
            item (Any): Any
        """        
        try:
            index = self.list.index(item)            
        except ValueError as err:
            print(err)
            sys.exit()        
        self.list.pop(index)
        


class FullQueueError(Exception):
    def __init__(self, item):
        self.item = item

    def __str__(self):
        return f'FullQueueError: Try to put {self.item} to the full queue'

class EmptyQueueError(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return f'EmptyQueueError: Try to get item from an empty queue'
        
    
    


    