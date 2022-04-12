"""
Authors: Ali Mokhtari (ali.mokhtaary@gmail.com)
Created on Jan, 24, 2022
"""

class Time:


    def __init__(self):
        self.current_time = 0.0

    

    def gct(self):
        """Get completion time

        Returns:
            float: current time
        """        
        return self.current_time
    
    def sct(self,time):
        """Set completion time

        Args:
            time (float): time
        """        
        self.current_time = time
    
    def reset(self):
        """Reset time
        """        
        self.current_time = 0.0
    