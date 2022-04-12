"""
Authors: Ali Mokhtari
Created on Jan. 07, 2021.

Description:

"""
import random
import pandas as pd
import numpy as np


class ExecutionTime:
    # Here, the execution time of task type on a specific machine type
    # is read from the dataset. Then, an execution time is sampled and
    # return as estimated or real execution time. 

    def __init__(self):        
        self.execution_times = None

    def sample(self, task_type_id, machine_type, size):
        # Here, the execution time of task type on a specific machine type
        # is read from the dataset. This function returns a list that 
        # contains the execution times.
        # the file name of the dataset must be in the format of 
        # <task_type_id>-<machine_type>.csv (e.g. 1-CPU.csv)
                
        path_to_file =f"./workload/execution_times/{task_type_id}-{machine_type.name}.csv"
        data = pd.read_csv(path_to_file)
        self.execution_times = np.random.choice(data['execution_time'].values, size)
        self.execution_times = [round(x, 3) for x in self.execution_times]    
       
        return self.execution_times
    
    def synthesize(self, low, high, size):
        self.execution_times = np.random.uniform(low, high, size)        
        self.execution_times = [round(x, 3) for x in self.execution_times]

        return self.execution_times

        