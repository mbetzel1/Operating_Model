import simpy
import random
import matplotlib.pyplot as plt

high1 = 2
low1 = 6
high2 = 4
low2 = 5
time = 120

bufferStart_level = []
buffer1_level = []
bufferEnd_level = []
machine1_level = []
machine2_level = []

class Machine(object):

    """
    the machine produces units at a fixed processing speed
    it takes units from a buffer and places finished units into a buffer
    """

    def __init__(self, env, name, in_buffer, out_buffer, low, high):
        self.env = env
        self.name = name
        self.in_buffer = in_buffer
        self.out_buffer = out_buffer
        self.low = low
        self.high = high
        self.count = 0
        
        # start running the process
        self.process = env.process(self.produce())

    def produce(self):
        while True:
            part = yield self.in_buffer.get()
            print(f'{self.env.now:.2f} {self.name} has got a part')

            self.count = 1
            yield self.env.timeout(random.uniform(self.low, self.high))
            print(f'{self.env.now:.2f} {self.name} finished a part. Next buffer has {len(self.out_buffer.items)} and capacity of {self.out_buffer.capacity}')
            self.count = 0
            yield self.out_buffer.put(part)
            print(f'{self.env.now:.2f} {self.name} pushed a part to next buffer')

def gen_arrivals(env, buffer0, buffer1, buffer2):
    """
    start the process for each part by putting part in starting buffer
    """
    while True:

        yield env.timeout(random.uniform(2,5))
        print(f'{env.now:.2f} part has arrived')
        part = object()
        yield buffer0.put(part)
        bufferStart_level.append(len(buffer0.items))
        buffer1_level.append(len(buffer1.items))
        bufferEnd_level.append(len(buffer2.items))

def run_simulation():
    # Create environment and start the setup process
    env = simpy.Environment()
    bufferStart = simpy.Store(env)  # Buffer with unlimited capacity
    buffer1 = simpy.Store(env, capacity = 6) # Buffer between machines with limited capacity
    bufferEnd = simpy.Store(env)  # Last buffer with unlimited capacity

    # the machines __init__ starts the machine process so no env.process() is needed here
    machine_1 = Machine(env, 'Furnace', bufferStart, buffer1, low1, high1)
    machine_2 = Machine(env, 'Press', buffer1, bufferEnd, low2, high2)

    env.process(gen_arrivals(env, bufferStart, buffer1, bufferEnd))
    env.run(until = time)
    plt.plot(bufferStart_level, label="BufferStart")
    plt.plot(buffer1_level, label="Buffer1")
    plt.plot(bufferEnd_level, label="BufferEnd")
    plt.plot(machine1_level, label=machine_1.name)
    plt.plot(machine2_level, label=machine_2.name)
    plt.xlabel('Time')
    plt.ylabel('Number of Items')
    plt.legend()
    plt.show()

if __name__ == "__main__":
    run_simulation()

