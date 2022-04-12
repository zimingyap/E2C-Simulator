"""
Authors: Ali Mokhtari (ali.mokhtaary@gmail.com)
Created on Jan, 24, 2022

Description:


"""
import json
import sys
# added traceback by ziming
import traceback

from utils.time import Time
from utils.event_queue import EventQueue
from utils.task_type import TaskType, UrgencyLevel
from utils.machine_type import MachineType
# from . import event_queue
# import time as Time
# import task_type as TaskType
# import machine_type as MachineType
'''
Begin code changes by Ziming
if json file wrong format return error
'''


def load_config(path_to_config='./config.json'):
    """Load config.json data

    Args:
        path_to_config (str, optional): _description_. Defaults to './config.json'.

    Returns:
        json: dictionary of configurations
    """
    try:
        f = open(path_to_config)
    except FileNotFoundError as fnf_err:
        print(fnf_err)
        sys.exit()
    data = f.read()
    f.close()
    data = json.loads(data)
    return data


'''
Begin code changes by Ziming
- Adding input validation
- Check if there are duplicate ids (??)
'''


def create_task_types(task_types_info):
    """Create task types from config.json

    Args:
        task_types_info (list): Description of tasks

    Returns:
        list: TaskType
        list: task_type_names

    """

    task_types = []
    task_type_names = []
    # task_id = set()
    curr_task_id = 0
    for task_type in task_types_info:
        try:
            if ('id' in task_type):
                id = int(task_type['id'])
                curr_task_id = id
            else:
                id = curr_task_id+1
            # task_id.add(id)
            name = task_type['name']
            urgency = task_type['urgency']
            if urgency == 'best_effort':
                urgency = UrgencyLevel.BESTEFFORT
            elif urgency == 'urgent':
                urgency = UrgencyLevel.URGENT
            # Default value for urgency set to best effort if not defined or wrong value
            else:
                err = ValueError("Urgency level set to best effort if not provided or wrong value")
                urgency = UrgencyLevel.BESTEFFORT
                raise err
            deadline = float(task_type['deadline'])
            if deadline < 0:
                sys.exit('Deadline should be a positive number')
            task_types.append(TaskType(id, name, urgency, deadline))
            task_type_names.append(name)
        except ValueError:
            print(traceback.format_exc())
    return task_types, task_type_names


'''
Begin code changes by Ziming
Adding input validation
'''


def create_machine_types(machines_info):
    """Create machine types from config.json

    Args:
        machines_info (dict)): machine's info (type id, name, power, idle power, replicas)

    Returns:
        list: MachineType
        list: machine_type_names
        int: number of machines        
    """
    machine_types = []
    machine_type_names = []
    no_of_machines = 0
    type_id = 0
    for machine_type in machines_info:
        try:
            type_id += 1
            name = machine_type['name']
            power = float(machine_type['power'])
            if power < 0:
                sys.exit('Power should be a positive number')
            idle_power = float(machine_type['idle_power'])
            if idle_power < 0:
                sys.exit('Idle power should be a positive number')
            replicas = int(machine_type['replicas'])
            if replicas < 0:
                sys.exit('Replicas should be a positive number')
            type = MachineType(type_id, name, power, idle_power, replicas)
            no_of_machines += replicas
            machine_types.append(type)
            machine_type_names.append(name)
        except ValueError:
            print(traceback.format_exc())

    return machine_types, machine_type_names, no_of_machines


def find_task_type(task_type_id):
    """Find task type based on id

    Args:
        task_type_id (int): _description_

    Raises:
        Exception: _description_

    Returns:
        task_type: TaskType(id, name, urgency, deadline)
    """
    try:
        for task_type in task_types:
            if task_type.id == task_type_id:
                return task_type
        raise Exception(
            'ERROR:     The task type id does not exist in config.task_types')
    except ValueError as err:
        print(err)


def init():
    #add default value 
    global event_queue
    global time
    global machines, machine_types, machine_type_names
    global task_types, task_type_names
    global cloud

    global settings
    global scheduling_method
    global fairness_factor
    global total_energy, available_energy
    global machine_queue_size, batch_queue_size
    global no_of_machines
    global bandwidth, network_latency
    global gui_task
    global log

    global gui 
    
    data = load_config()

    time = Time()
    event_queue = EventQueue()
    gui_task = []
    task_types, task_type_names = create_task_types(data['task_types'])
    machine_types, machine_type_names, no_of_machines = create_machine_types(
        data['machines'])
    machines = []

    capacity = data['battery'][0]['capacity']
    total_energy = capacity * 3600
    available_energy = total_energy

    machine_queue_size = data['parameters'][0]["machine_queue_size"]
    batch_queue_size = data['parameters'][0]['batch_queue_size']
    scheduling_method = data['parameters'][0]['scheduling_method']
    fairness_factor = data['parameters'][0]['fairness_factor']
    bandwidth = data['cloud'][0]['bandwidth']
    network_latency = data['cloud'][0]['network_latency']

    settings = data['settings'][0]
    gui = settings['gui']
    try:
        log = open(f"{settings['path_to_output']}/log.txt", 'w')
    except OSError as err:
        print(err)
