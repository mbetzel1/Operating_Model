import simpy
import random
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import pandas as pd
import matplotlib.patches
from entities import Machine, Buffer



def optimize(repititions=5, runs=5, starting_number_list=[2,6,11,20,5,4,26,5,3,20]):
    for i in range(repititions):
        buffer_lists = repeat_process(runs)
        average_production = sum([list[len(list) - 1].level for list in buffer_lists])/(len(buffer_lists)*2000)
        
    return(average_production)
    #pounds_produced = buffer_list[len(buffer_list)-1].level/2000, 

def repeat_process(n=3):
    total_produced = []
    for i in range(n):
        total_produced.append(run_process())
    return total_produced

def run_process(machine_number_list=[2,6,11,20,5,4,26,5,3,20]):
    # Load the specs using pandas
    SPEC_PATH = "./Machine_Specs.csv"
    specs = pd.read_csv(SPEC_PATH, index_col="Item",)
    machine_names = specs.index

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
    TWO_SHIFT_ANNUAL_HOURS = specs.loc['Jet-Mill', 'Two-Shift-Annual-Hours']
    ONE_SHIFT_ANNUAL_HOURS = specs.loc['Jet-Mill', 'One-Shift-Annual-Hours']

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
        number_required = machine_number_list[i]
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
            cycle_time = specs.loc[name, 'Cycle-Time'],
            cycle_time_sigma = specs.loc[name, 'Cycle-Time']/10,
            yield_rate = float(specs.loc[name, "Yield"][:2])/100,
            yield_sigma = float(specs.loc[name, "Yield"][:2])/100/20,
            batch_failure_rate = 0.05,
            mtbf = specs.loc[name, "MBTF-Days"] * WORK_HOURS_PER_DAY,
            mttr = specs.loc[name, "MMT-Days"] * WORK_HOURS_PER_DAY,
            repair_std_dev= 0.5,
            batch_size = specs.loc[name, "Lbs-Per-Cycle"],
            )
            
            machine_list.append(machine)
        machine_dict[name] = machine_list

    env.process(gen_arrivals(env, start_buffer))
    env.run(until=SIMULATION_HOURS)
    return buffer_list
# for name in machine_names:
#     machine_list = machine_dict[name]
#     for machine in machine_list:
#         print(f'{machine.name} finished {machine.number_finished} lbs')
# for buffer in buffer_list:
#     print(buffer.name + " has a level of " + str(buffer.level))
print(optimize(1,1))
