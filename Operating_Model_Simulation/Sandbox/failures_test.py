import simpy
import random
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import pandas as pd
import matplotlib.patches

SPEC_PATH = "./Machine_Specs.csv"
specs = pd.read_csv(SPEC_PATH)
specs.set_index('Item', inplace=True)
print(specs.loc['Jet-Mill', 'MTBF-Two-Shift'])
# each time step is equal to 1 hour
HOURS_PER_DAY = 24
DAYS_PER_YEAR = 365
TWO_SHIFT_HOURS_WORKED_PER_DAY = 16
ONE_SHIFT_HOURS_WORKED_PER_DAY = 8
TWO_SHIFT_ANNUAL_HOURS = specs.loc['Jet-Mill', 'Two-Shift-Annual-Hours']
ONE_SHIFT_ANNUAL_HOURS = specs.loc['Jet-Mill', 'One-Shift-Annual-Hours']

# need poisson for ttf for machines
# need maintenance time distributed normally
# probabily of defect distributed binomially
# probability of batch defects distributed binomially

class Machine(object):

    """
    the machine produces units at a fixed processing speed
    it takes units from a buffer and places finished units into a buffer
    """

    def __init__(self, env, name, in_buffer, out_buffer, low, high, mtbf, part_single_failure_rate, part_batch_failure_rate):
        self.env = env
        self.name = name
        self.in_buffer = in_buffer
        self.out_buffer = out_buffer
        self.low = low
        self.high = high
        self.mtbf = mtbf
        self.number_finished = 0
        self.start_times = []
        self.finish_times = []
        self.fail_times = []
        self.single_failure_rate = part_single_failure_rate
        self.batch_failure_rate = part_batch_failure_rate
        # start running the process
        self.process = env.process(self.produce())

    def produce(self):
        """
        Runs the process for the machine
        """
        while True:
            # if a part is available get it from the buffer
            part = yield self.in_buffer.get()
            print(f'{self.env.now:.2f} {self.name} has got a part')
            # add to your start times list
            self.start_times.append(self.env.now)
            
            yield self.env.timeout(random.uniform(self.low, self.high))
            print(f'{self.env.now:.2f} {self.name} finished a part. Next buffer has {len(self.out_buffer.items)} and capacity of {self.out_buffer.capacity}')
            if random.uniform(0, 1) > self.mtbf:
                yield self.out_buffer.put(part)
                print(f'{self.env.now:.2f} {self.name} pushed a part to next buffer')
                self.number_finished += 1
                self.finish_times.append(self.env.now)
            else:
                print(f'{self.env.now:.2f} {self.name} failed')
                self.fail_times.append(self.env.now)

