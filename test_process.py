import simpy
import random
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import pandas as pd
import matplotlib.patches
from entities import Machine, Buffer

# Load the specs using pandas
SPEC_PATH = "./Machine_Specs.csv"
specs = pd.read_csv(SPEC_PATH, index_col="Item",)

NUMBER_PROCESSES = 1
machine_names = []
for i in range(NUMBER_PROCESSES):
# indirect way for setting how many processes there will be
    machine_names.append(str(i) + " machine")
# how many machines are in each process, length must match machine_names
NUMBER_OF_MACHINES_PER_PROCESS = [1]

# Define constants
HOURS_PER_DAY = 24
WORK_HOURS_PER_DAY = 16
DAYS_PER_YEAR = 365
TWO_SHIFT_HOURS_WORKED_PER_DAY = 16
ONE_SHIFT_HOURS_WORKED_PER_DAY = 8
DELIVERY_SIZE = 10000
DELIVERY_SIZE_SIGMA = 0
DELIVERY_TIME = 1
DELIVERY_TIME_SIGMA = 0

# Number of hours annually in a one or two shift shop
TWO_SHIFT_ANNUAL_HOURS = 100

SIMULATION_HOURS = TWO_SHIFT_ANNUAL_HOURS



def gen_arrivals(env, start_buffer):
    """
    start the process for each part by putting part in starting buffer
    """
    while True:
        yield env.timeout(random.normalvariate(DELIVERY_TIME, DELIVERY_TIME_SIGMA))
        #print(f'{env.now:.2f} part has arrived')
        yield start_buffer.put(random.normalvariate(DELIVERY_SIZE, DELIVERY_SIZE_SIGMA))


env = simpy.Environment()
start_buffer = Buffer(env, "Buffer 0")
buffer_list = [start_buffer,]
machine_dict = {}
for i in range(len(machine_names)):
    name = machine_names[i]
    # print(name)
    number_required = NUMBER_OF_MACHINES_PER_PROCESS[i]
    buffer_list.append(Buffer(env, "Buffer " + str(i + 1)))
    # print(buffer_list[i].name)
    # print(buffer_list[i + 1].name)
    machine_list = []
    for j in range(number_required):
        machine = Machine(
        env,
        name = name + " " + str(j),
        item_type = name,
        in_buffer = buffer_list[i],
        out_buffer = buffer_list[i + 1],
        cycle_time = 1,
        cycle_time_sigma = 0,
        yield_rate = 1,
        yield_sigma = 0,
        batch_failure_rate = 0.0,
        mtbf = 10,
        mttr = 10,
        repair_std_dev= 0.0,
        batch_size = 1,
        )
        
        machine_list.append(machine)
    machine_dict[name] = machine_list

env.process(gen_arrivals(env, start_buffer))
env.run(until=SIMULATION_HOURS)
for name in machine_names:
    machine_list = machine_dict[name]
    for machine in machine_list:
        print(f'{machine.name} finished {machine.number_finished} lbs')
for buffer in buffer_list:
    print(buffer.name + " has a level of " + str(buffer.level))
