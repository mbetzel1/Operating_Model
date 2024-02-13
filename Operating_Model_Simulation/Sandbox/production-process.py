import simpy
import random
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import pandas as pd
import matplotlib.patches

SIM_TIME = 50

MACHINE_1_LOW = 1
MACHINE_1_HIGH = 2
MACHINE_2_LOW = 2
MACHINE_2_HIGH = 4
MACHINE_3_LOW = 1
MACHINE_3_HIGH = 2
ARRIVAL_LOW = 0.5
ARRIVAL_HIGH = 1

FAILURE_RATE_1 = 0.15
FAILURE_RATE_2 = 0.3
FAILURE_RATE_3 = 0.15
N_MACHINES_1 = 2
N_MACHINES_2 = 4
N_MACHINES_3 = 2

machines_1_list = []
machines_2_list = []
machines_3_list = []

start_buffer_items = {}
buffer_1_items = {}
buffer_2_items = {}
end_buffer_items = {}

class Buffer(simpy.Store):
    def __init__(self, env, *args, **kwargs):
        super().__init__(env, *args, **kwargs)
        self.record = {}
        self.env = env
    
    def put(self, *args, **kwargs):
        result = super().put(*args, **kwargs)
        self.record[self.env.now] = len(self.items)
        return result
    
    def get(self, *args, **kwargs):
        result = super().get(*args, **kwargs)
        self.record[self.env.now] = len(self.items)
        return result

class Machine(object):

    """
    the machine produces units at a fixed processing speed
    it takes units from a buffer and places finished units into a buffer
    """

    def __init__(self, env, name, in_buffer, out_buffer, low, high, failure_rate):
        self.env = env
        self.name = name
        self.in_buffer = in_buffer
        self.out_buffer = out_buffer
        self.low = low
        self.high = high
        self.failure_rate = failure_rate
        self.number_finished = 0
        self.start_times = []
        self.finish_times = []
        self.fail_times = []
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
            if random.uniform(0, 1) > self.failure_rate:
                yield self.out_buffer.put(part)
                print(f'{self.env.now:.2f} {self.name} pushed a part to next buffer')
                self.number_finished += 1
                self.finish_times.append(self.env.now)
            else:
                print(f'{self.env.now:.2f} {self.name} failed')
                self.fail_times.append(self.env.now)


def gen_arrivals(env, buffer0, buffer1, buffer2, buffer3):
    """
    start the process for each part by putting part in starting buffer
    """
    while True:
        yield env.timeout(random.uniform(ARRIVAL_LOW, ARRIVAL_HIGH))
        print(f'{env.now:.2f} part has arrived')
        part = object()
        yield buffer0.put(part)
        start_buffer_items[env.now] = len(buffer0.items)
        buffer_1_items[env.now] = len(buffer1.items)
        buffer_2_items[env.now] = len(buffer2.items)
        end_buffer_items[env.now] = len(buffer3.items)

# def record_states(buffer0, buffer1, buffer2, buffer3, machines_1_list, machines_2_list, machines_3_list):
#     ''''
#     Uses existing records to build a dataframe of all data
#     columns are each agent
#     rows are agent states at specific times in process
#     '''
#     # get time steps for entire simulation in 0.05 increments
#     times = np.arange(0.0, SIM_TIME + 0.1, 0.1)
#     merged_df = pd.DataFrame({'time': times})
#     # go through all the machine data
#     for machine in (machines_1_list + machines_2_list + machines_3_list):
#         # 0 value for machine is empty, 1 value is working, and -1 value is a failure
#         values = [0] + ([1] * len(machine.start_times)) + ([0] * len(machine.finish_times)) + ([-1] * len(machine.fail_times))
#         times = [0.0] + machine.start_times + machine.finish_times + machine.fail_times
#         df = pd.DataFrame({'time': times, machine.name: values})
#         merged_df = pd.merge_asof(merged_df.sort_values('time'), df.sort_values('time'), on='time', direction='nearest')
#     # collect buffer data
#     buffer0_df = pd.DataFrame({'time': buffer0.record.keys(), 'buffer0': buffer0.record.values()})
#     buffer1_df = pd.DataFrame({'time': buffer1.record.keys(), 'buffer1': buffer1.record.values()})
#     buffer2_df = pd.DataFrame({'time': buffer2.record.keys(), 'buffer2': buffer2.record.values()})
#     buffer3_df = pd.DataFrame({'time': buffer3.record.keys(), 'buffer3': buffer3.record.values()})
#     merged_df = pd.merge_asof(merged_df.sort_values('time'), buffer0_df.sort_values('time'), on='time', direction='nearest')
#     merged_df = pd.merge_asof(merged_df.sort_values('time'), buffer1_df.sort_values('time'), on='time', direction='nearest')
#     merged_df = pd.merge_asof(merged_df.sort_values('time'), buffer2_df.sort_values('time'), on='time', direction='nearest')
#     merged_df = pd.merge_asof(merged_df.sort_values('time'), buffer3_df.sort_values('time'), on='time', direction='nearest')

#     return merged_df

# build environment
env = simpy.Environment()
start_buffer = Buffer(env)
buffer1 = Buffer(env, capacity = 10)
buffer2 = Buffer(env, capacity = 10)
end_buffer = Buffer(env)

# build machines
for i in range(N_MACHINES_1):
    machine = Machine(env, f'MACHINE_1_{i}', start_buffer, buffer1, MACHINE_1_LOW, MACHINE_1_HIGH, FAILURE_RATE_1)
    machines_1_list.append(machine)

for i in range(N_MACHINES_2):
    machine = Machine(env, f'MACHINE_2_{i}', buffer1, buffer2, MACHINE_2_LOW, MACHINE_2_HIGH, FAILURE_RATE_2)
    machines_2_list.append(machine)

for i in range(N_MACHINES_3):
    machine = Machine(env, f'MACHINE_3_{i}', buffer2, end_buffer, MACHINE_3_LOW, MACHINE_3_HIGH, FAILURE_RATE_3)
    machines_3_list.append(machine)

# run process
env.process(gen_arrivals(env, start_buffer, buffer1, buffer2, end_buffer))
env.run(until=SIM_TIME)

# # print outcomes
# for machine in machines_1_list:
#     print(f'{machine.name} finished {machine.number_finished} parts')

# for machine in machines_2_list:
#     print(f'{machine.name} finished {machine.number_finished} parts')

# for machine in machines_3_list:
#     print(f'{machine.name} finished {machine.number_finished} parts')

# # record states
# df = record_states(start_buffer, buffer1, buffer2, end_buffer, machines_1_list, machines_2_list, machines_3_list)

# # df.iloc[[100, 200, 300]].plot(x="time", y=["buffer0", "buffer1", 'buffer2', 'buffer3',],  kind='bar')
# # plt.show()

# # build background for animation
# # set the arguments
# n_cols = 7
# box_margin = 25
# box_side = 50
# text_margin = 7
# max_machines = max(N_MACHINES_1, N_MACHINES_2, N_MACHINES_3)
# plot_height = box_margin * (max_machines + 2) + box_side * max_machines
# plot_width = n_cols * box_side + (n_cols + 2) * box_margin
# plot_max = max(plot_width, plot_height)
# buffer_bottom = (plot_max - box_side)/2 
# buffer_top = buffer_bottom + box_side
# fig, ax = plt.subplots(1)
# machine_texts = {}
# machine_status_color = {-1: "red", 0: "black", 1:"green"}

# time_text = plt.text(box_margin, box_margin, "Time: 0.0", fontsize="medium", horizontalalignment='left', verticalalignment='bottom')

# # build the buffer diagrams
# buffer0_left = box_margin
# buffer0_right = buffer0_left + box_side
# buffer0_rect = matplotlib.patches.Rectangle((buffer0_left, buffer_bottom), box_side, box_side, linewidth=1, edgecolor="black", facecolor="None")
# plt.text(buffer0_left, buffer_top, "Buffer 0", fontsize = "xx-small", horizontalalignment='left', verticalalignment='bottom')
# buffer0_text = ax.text(0.5 * (buffer0_left + buffer0_right), 0.5 * (buffer_top + buffer_bottom), "", fontsize = "xx-small", horizontalalignment='center', verticalalignment='center')

# buffer1_left = box_margin * 3 + box_side * 2
# buffer1_right = buffer1_left + box_side
# buffer1_rect = matplotlib.patches.Rectangle((buffer1_left, buffer_bottom), box_side, box_side, linewidth=1, edgecolor="black", facecolor="None")
# plt.text(buffer1_left, buffer_top, "Buffer 1", fontsize = "xx-small", horizontalalignment='left', verticalalignment='bottom')
# buffer1_text = ax.text(0.5 * (buffer1_left + buffer1_right), 0.5 * (buffer_top + buffer_bottom), "", fontsize = "xx-small", horizontalalignment='center', verticalalignment='center')

# buffer2_left = box_margin * 5 + box_side * 4
# buffer2_right = buffer2_left + box_side
# buffer2_rect = matplotlib.patches.Rectangle((buffer2_left, buffer_bottom), box_side, box_side, linewidth=1, edgecolor="black", facecolor="None")
# plt.text(buffer2_left, buffer_top, "Buffer 2", fontsize = "xx-small", horizontalalignment='left', verticalalignment='bottom')
# buffer2_text = ax.text(0.5 * (buffer2_left + buffer2_right), 0.5 * (buffer_top + buffer_bottom), "", fontsize = "xx-small", horizontalalignment='center', verticalalignment='center')

# buffer3_left = box_margin * 7 + box_side * 6
# buffer3_right = buffer3_left + box_side
# buffer3_rect = matplotlib.patches.Rectangle((buffer3_left, buffer_bottom), box_side, box_side, linewidth=1, edgecolor="black", facecolor="None")
# plt.text(buffer3_left, buffer_top, "Buffer 3", fontsize = "xx-small", horizontalalignment='left', verticalalignment='bottom')
# buffer3_text = ax.text(0.5 * (buffer3_left + buffer3_right), 0.5 * (buffer_top + buffer_bottom), "", fontsize = "xx-small", horizontalalignment='center', verticalalignment='center')

# # add the rectangles to plot
# ax.add_patch(buffer0_rect)
# ax.add_patch(buffer1_rect)
# ax.add_patch(buffer2_rect)
# ax.add_patch(buffer3_rect)

# # build the machine diagrams
# for i, machine in enumerate(machines_1_list):
#     left = box_margin * 2 + box_side
#     right = left + box_side
#     increment = plot_max/(N_MACHINES_1 + 1)
#     bottom = increment * (i + 1) - (box_side/2)
#     top = bottom + box_side
#     machine_rect = matplotlib.patches.Rectangle((left, bottom), box_side, box_side, linewidth=1, edgecolor="black", facecolor="None")
#     ax.add_patch(machine_rect)
#     plt.text(left, top, machine.name, fontsize = "xx-small", horizontalalignment='left', verticalalignment='bottom')
#     machine_texts[machine.name] = ax.text(0.5 * (left + right), 0.5 * (top + bottom), "", fontsize = "xx-small", horizontalalignment='center', verticalalignment='center')

# for i, machine in enumerate(machines_2_list):
#     left = box_margin * 4 + box_side * 3
#     right = left + box_side
#     increment = plot_max/(N_MACHINES_2 + 1)
#     bottom = increment * (i + 1) - (box_side/2)
#     top = bottom + box_side
#     machine_rect = matplotlib.patches.Rectangle((left, bottom), box_side, box_side, linewidth=1, edgecolor="black", facecolor="None")
#     ax.add_patch(machine_rect)
#     plt.text(left, top, machine.name, fontsize = "xx-small", horizontalalignment='left', verticalalignment='bottom')
#     machine_texts[machine.name] = ax.text(0.5 * (left + right), 0.5 * (top + bottom), "", fontsize = "xx-small", horizontalalignment='center', verticalalignment='center')

# for i, machine in enumerate(machines_3_list):
#     left = box_margin * 6 + box_side * 5
#     right = left + box_side
#     increment = plot_max/(N_MACHINES_3 + 1)
#     bottom = increment * (i + 1) - (box_side/2)
#     top = bottom + box_side
#     machine_rect = matplotlib.patches.Rectangle((left, bottom), box_side, box_side, linewidth=1, edgecolor="black", facecolor="None")
#     ax.add_patch(machine_rect)
#     plt.text(left, top, machine.name, fontsize = "xx-small", horizontalalignment='left', verticalalignment='bottom')
#     machine_texts[machine.name] = ax.text(0.5 * (left + right), 0.5 * (top + bottom), "", fontsize = "xx-small", horizontalalignment='center', verticalalignment='center')

# ax.set_xlim(left=0, right=plot_max)
# ax.set_ylim(bottom=0, top=plot_max)
# plt.xticks([], [])
# plt.yticks([], [])
# text_list = []

# def init():
#     # build background for animation
#     # set the arguments
#     row = df.iloc[0]

#     time_text.set_text(f'Time: {row["time"]:.1f}')
#     row = row.astype(int)
#     # build the buffer diagrams
#     buffer0_text.set_text(row['buffer0'])
#     buffer1_text.set_text(row['buffer1'])
#     buffer2_text.set_text(row['buffer2'])
#     buffer3_text.set_text(row['buffer3'])

    

#     # build the machine diagrams
#     for machine in machines_1_list:
#         value = row[machine.name]
#         machine_texts[machine.name].set_text(value)
#         machine_texts[machine.name].set_color(machine_status_color[value])
        

#     for machine in machines_2_list:
#         value = row[machine.name]
#         machine_texts[machine.name].set_text(value)
#         machine_texts[machine.name].set_color(machine_status_color[value])

#     for machine in machines_3_list:
#         value = row[machine.name]
#         machine_texts[machine.name].set_text(value)
#         machine_texts[machine.name].set_color(machine_status_color[value])

# def animate(i):
#     # build background for animation
#     # set the arguments
#     row = df.iloc[i]

#     time_text.set_text(f'Time: {row["time"]:.1f}')
#     row = row.astype(int)
#     # build the buffer diagrams
#     buffer0_text.set_text(row['buffer0'])
#     buffer1_text.set_text(row['buffer1'])
#     buffer2_text.set_text(row['buffer2'])
#     buffer3_text.set_text(row['buffer3'])

#     ## build the machine diagrams
#     for machine in machines_1_list:
#         value = row[machine.name]
#         machine_texts[machine.name].set_text(value)
#         machine_texts[machine.name].set_color(machine_status_color[value])
        

#     for machine in machines_2_list:
#         value = row[machine.name]
#         machine_texts[machine.name].set_text(value)
#         machine_texts[machine.name].set_color(machine_status_color[value])

#     for machine in machines_3_list:
#         value = row[machine.name]
#         machine_texts[machine.name].set_text(value)
#         machine_texts[machine.name].set_color(machine_status_color[value])

# anim = FuncAnimation(fig, animate, init_func=init, repeat=True, save_count=len(df))
# anim.save('test_animation.gif', writer='imagemagick', fps=10, dpi=240)

