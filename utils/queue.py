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
        """
        The function qsize() returns the length of the list
        :return: The length of the list.
        """
              
        return len(self.list)

    def empty(self):
        """
        If the list is empty, return True, otherwise return False
        :return: The boolean value of the list.
        """
            
        return not bool(self.list)
    
    def full(self):
        """
        Returns True if the queue is full, False otherwise
        :return: The return value is a boolean value.
        """
        
        return self.qsize() == self.maxsize
    
    def put(self, item):
        """
        If the queue is full, raise a FullQueueError exception with the item as the argument, otherwise
        append the item to the list
        
        :param item: the item to be added to the queue
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
        """
        If the index is out of range, print the error message and exit the program
        
        :param index: The index of the item to be removed, defaults to 0 (optional)
        :return: The value of the item at the index specified.
        """
                           
        try:
            self.list[index]                   
        except IndexError as val_err:
            print(val_err)
            print(f'index {index} is out of range of list {self.list}')
            sys.exit()
        return self.list.pop(index)
        
        
    
    def remove(self, item):
        """
        The function removes an item from the list
        
        :param item: The item to be removed from the list
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
        
    
    


    