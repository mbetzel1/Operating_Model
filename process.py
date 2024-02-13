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
machine_names = specs.index

# Define constants
HOURS_PER_DAY = 24
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




def gen_arrivals(env, start_buffer):
    """
    start the process for each part by putting part in starting buffer
    """
    while True:
        yield env.timeout(random.normalvariate(DELIVERY_TIME, DELIVERY_TIME_SIGMA))
        #print(f'{env.now:.2f} part has arrived')
        yield start_buffer.put(random.normalvariate(DELIVERY_SIZE, DELIVERY_SIZE_SIGMA))


env = simpy.Environment()
start_buffer = Buffer(env)
end_buffer = Buffer(env)

name = machine_names[0]

print(float(specs.loc[name, "Yield"][:2])/100)
machine = Machine(
    env,
    name = name + "1",
    item_type = name,
    in_buffer = start_buffer,
    out_buffer = end_buffer,
    cycle_time = specs.loc[name, 'Cycle-Time'],
    cycle_time_sigma = specs.loc[name, 'Cycle-Time']/10,
    yield_rate = float(specs.loc[name, "Yield"][:2])/100,
    yield_sigma = float(specs.loc[name, "Yield"][:2])/100/100,
    batch_failure_rate = 0.05,
    mtbf = 100,
    mttr = 1,
    repair_std_dev= 0.1,
    batch_size = specs.loc[name, "Lbs-Per-Cycle"],
)

env.process(gen_arrivals(env, start_buffer))
env.run(until=100)
print(specs.loc[name, 'Cycle-Time'])
print(f'{machine.name} finished {machine.number_finished} lbs')
