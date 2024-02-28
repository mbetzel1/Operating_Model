import simpy
import random
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import pandas as pd
import matplotlib.patches
from entities import Machine, Buffer



def optimize(repititions=5, runs=5, numbers_of_each_machine=[2,6,11,20,5,4,26,5,3,20], target=1000):
    SPEC_PATH = "./Machine_Specs.csv"
    specs = pd.read_csv(SPEC_PATH, index_col="Item",)
    machine_names = specs.index
    reversed_names = machine_names[::-1]
    finished_by_type = {}
    yield_ratios = {}
    yield_ratio = 1
    # use the expected yield of each step to know how many pounds you need to get the target
    for name in reversed_names:
        yield_ratio *= float(specs.loc[name, "Yield"][:2])/100
        yield_ratios[name] = yield_ratio
    # go through reps changing the number of each machine
    for i in range(repititions):
        # set the dict back to zero
        for name in machine_names:
            finished_by_type[name] = 0.0
        # run the process
        list_of_dicts = repeat_process(runs, numbers_of_each_machine)
        # see how much each machine finished
        for j in range(runs):
            machine_dict = list_of_dicts[j]
            for name in machine_names:
                finished_by_type[name] += yield_ratios[name] * sum([machine.number_finished for machine in machine_dict[name]]) /(2000 * runs)
            
        # for the first machine which didn't finish the target on average, add one more
        for number, name in enumerate(machine_names):
            print(f'Run {i}, {numbers_of_each_machine[number]} {name} machines total finished: {finished_by_type[name]}')
            if finished_by_type[name] < target:
                numbers_of_each_machine[number] += 1
                print(f'added one {name} to have {numbers_of_each_machine[number]}')
                break
    return(numbers_of_each_machine)
    #pounds_produced = buffer_list[len(buffer_list)-1].level/2000, 

def repeat_process(n=3, numbers_of_each_machine=[2,6,11,20,5,4,26,5,3,20]):
    list_of_dicts = []
    for i in range(n):
        list_of_dicts.append(run_process(numbers_of_each_machine))
    return list_of_dicts

def run_process(numbers_of_each_machine=[2,6,11,20,5,4,26,5,3,20]):
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
        number_required = numbers_of_each_machine[i]
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
    return machine_dict
# for name in machine_names:
#     machine_list = machine_dict[name]
#     for machine in machine_list:
#         print(f'{machine.name} finished {machine.number_finished} lbs')
# for buffer in buffer_list:
#     print(buffer.name + " has a level of " + str(buffer.level))
print(optimize(5,5, [4,7,12,21,6,5,29,10,6,20]))
