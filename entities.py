import simpy
import random
import numpy as np

class Buffer(simpy.Container):
    """Extends simpy.Store to log number of items at each time step
    
    Attributes:
        env         A simpy.Environment
        record      The dictionary that stores the number of items at each time step
    """

    def __init__(self, env, name, *args, **kwargs):
        """Initiates the buffer
        
        Parameters:
        env (simpy.Environment): An environment simpy object

        Returns:
        None
        """
        super().__init__(env, *args, **kwargs)
        self.record = {}
        self.env = env
        self.name = name
    
    def put(self, *args, **kwargs):
        """Adds an item to the buffer and records the new state"""
        result = super().put(*args, **kwargs)
        self.record[self.env.now] = self.level
        return result
    
    def get(self, *args, **kwargs):
        """Removes an item from the buffer and records the new state"""
        result = super().get(*args, **kwargs)
        self.record[self.env.now] = self.level
        return result

class Machine(object):
    """Takes resources from a buffer and performs a process
    The machine records the times at which a process starts and completes
    The time for the process to complete is normally distributed
    The machine can output good or defective parts distributed binomially
    The machine can output good or defective batches distributed binomially
    The machine can itself fail and cease processing using a exponential distribution
    The machine will repair itself with the repair time distributed log-normally 

    Attributes:
        env                 The simpy environment in which the machine operates
        name                The unique name given to the machine
        type                The type of machine (jet-mill, etc)
        in_buffer           The buffer from which the machine retrieves items
        out_buffer          The buffer to which the machine outputs items
        mean                The average time to complete the process
        std_dev             The standard deviation from the mean for the process
        failure_rate        The rate at which individual parts fail
        batch_failure_rate  The rate at which batches fail
        number_finished     The total number of items completed in the run
        start_times         The times at which the machine started an item
        finish_times        The times at which the machine finished an item
        fail_times          The times at which the machine failed
        process             The process to run in the environment
        mtbf                The lambda parameter for the Poisson distribution
        mttr                The mean time to repair distributed log-normally
        repair_std_dev      The standard deviation time for repairs
    """

    def __init__(
            self, 
            env, 
            name, 
            item_type, 
            in_buffer, 
            out_buffer, 
            cycle_time, 
            cycle_time_sigma, 
            yield_rate,
            yield_sigma,
            batch_failure_rate,
            mtbf,
            mttr,
            repair_std_dev,
            batch_size,
            ):
        
        self.env = env
        self.name = name
        self.type = item_type
        self.in_buffer = in_buffer
        self.out_buffer = out_buffer
        self.cycle_time = cycle_time
        self.cycle_time_sigma = cycle_time_sigma
        self.yield_rate = yield_rate
        self.yield_sigma = yield_sigma
        self.batch_failure_rate = batch_failure_rate
        self.mtbf = mtbf
        self.mttr = mttr
        self.repair_std_dev = repair_std_dev
        self.batch_size = batch_size
        self.items_ready = 0
        self.number_finished = 0
        # start running the process
        self.break_time = random.expovariate(1/self.mtbf)
        self.repair_time = np.log(random.lognormvariate(self.mttr, self.repair_std_dev))
        self.process = env.process(self.produce())
        env.process(self.break_machine())

    def produce(self):
        """
        Runs the process for the machine
        """
        # continuously run the process
        while True:
            try:
                # when a load is available get it from the buffer
                yield self.in_buffer.get(amount = self.batch_size)
                # add to your start times list
                cycle = random.normalvariate(self.cycle_time, self.cycle_time_sigma)
                # ensure time is always non-negative
                if cycle < 0:
                    cycle = 0
                # process the quantity you just got
                yield self.env.timeout(cycle)
                # make sure the batch is successful
                if random.uniform(0, 1) > self.batch_failure_rate:
                    yielded_amount = random.normalvariate(self.batch_size * self.yield_rate, self.yield_sigma)
                    yield self.out_buffer.put(yielded_amount)
                    self.number_finished += yielded_amount
            # machine is broken
            except simpy.Interrupt:
        
                # set a new break time
                self.break_time = random.expovariate(1/self.mtbf)
                # wait until you are repaired
                yield(self.env.timeout(self.repair_time))
                # get a new repair time
                self.repair_time = np.log(random.lognormvariate(self.mttr, self.repair_std_dev))


                
                
    
    def break_machine(self):
        # Process to break the machine
        while True:
            # wait until the time to break
            yield self.env.timeout(self.break_time)
            # break
            self.process.interrupt()
            # wait until your repaired to restart the clock on breaking
            yield self.env.timeout(self.repair_time)
