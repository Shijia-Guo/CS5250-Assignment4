'''
CS5250 Assignment 4, Scheduling policies simulator
Sample skeleton program
Input file:
    input.txt
Output files:
    FCFS.txt
    RR.txt
    SRTF.txt
    SJF.txt
'''
import sys
import Queue
import copy
input_file = 'input.txt'

class Process:
    last_scheduled_time = 0
    remain_burst_time = 0
    def __init__(self, id, arrive_time, burst_time):
        self.id = id
        self.arrive_time = arrive_time
        self.burst_time = burst_time
        self.remain_burst_time = burst_time
    #for printing purpose
    def __repr__(self):
        return ('[id %d : arrival_time %d,  burst_time %d]'%(self.id, self.arrive_time, self.burst_time))
    # for the use of priority queue
    def __lt__(self,other):
        return self.remain_burst_time < other.remain_burst_time

def FCFS_scheduling(process_list):
    #store the (switching time, proccess_id) pair
    schedule = []
    current_time = 0
    waiting_time = 0
    for process in process_list:
        if(current_time < process.arrive_time):
            current_time = process.arrive_time
        schedule.append((current_time,process.id))
        waiting_time = waiting_time + (current_time - process.arrive_time)
        current_time = current_time + process.burst_time
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time
def put_process_ready_queue(processes,ready_process_queue,current_time):
    process_remove_indexes = []
    for i in range(0,len(processes)):
        if(processes[i].arrive_time <= current_time):
            ready_process_queue.put(processes[i])
            process_remove_indexes.append(i)         
    for i in sorted(process_remove_indexes, reverse=True): 
        del processes[i]

#Input: process_list, time_quantum (Positive Integer)
#Output_1 : Schedule list contains pairs of (time_stamp, proccess_id) indicating the time switching to that proccess_id
#Output_2 : Average Waiting Time
def RR_scheduling(process_list, time_quantum ):
    RR_processes = copy.deepcopy(process_list)
    if len(RR_processes) == 0 or time_quantum <= 0:
        return([],0.0)
    
    schedule = []
    length = float(len(RR_processes))
    current_time = 0
    waiting_time = 0
    ready_process_queue = Queue.Queue()
    terminate = False
    while True:
        ## check terminate condition
        if len(RR_processes) == 0 and ready_process_queue.empty():
            terminate = True
        if(terminate):
            break
        ## take the ready process from the process_list
        put_process_ready_queue(RR_processes,ready_process_queue,current_time)

        if ready_process_queue.empty():
            current_time = RR_processes[0].arrive_time
            ready_process_queue.put(RR_processes[0])
            RR_processes.pop(0)

        current_process = ready_process_queue.get()
        schedule.append((current_time,current_process.id))

        if current_process.remain_burst_time <= time_quantum:
            current_time = current_time + current_process.remain_burst_time
            waiting_time = waiting_time + current_time - current_process.arrive_time - current_process.burst_time
        else:
            current_time = current_time + time_quantum
            current_process.last_scheduled_time = current_time
            current_process.remain_burst_time = current_process.remain_burst_time - time_quantum
            ## take the ready process from the process_list
            put_process_ready_queue(RR_processes,ready_process_queue,current_time)
            ready_process_queue.put(current_process)
    return (schedule,waiting_time/length)

def SRTF_scheduling(process_list):
    SRTF_processes = copy.deepcopy(process_list)
    if len(SRTF_processes) == 0:
        return([],0.0)
    
    schedule = []
    length = float(len(SRTF_processes))
    current_time = 0
    waiting_time = 0
    ready_process_queue = Queue.PriorityQueue()
    terminate = False
    hasNext_arrival = True
    next_arrival_time = -1
    while True:
        ## check terminate condition
        if len(SRTF_processes) == 0 and ready_process_queue.empty():
            terminate = True
        if(terminate):
            break
        ## take the ready process from the process_list

        put_process_ready_queue(SRTF_processes,ready_process_queue,current_time)
        if ready_process_queue.empty():
            current_time = SRTF_processes[0].arrive_time
            ready_process_queue.put(SRTF_processes[0])
            SRTF_processes.pop(0)

        if len(SRTF_processes) == 0:
            hasNext_arrival = False
        else:
            next_arrival_time = SRTF_processes[0].arrive_time

        if(hasNext_arrival == False):
            while ready_process_queue.empty() == False:
                current_process = ready_process_queue.get()
                if current_process.last_scheduled_time != current_time:
                    schedule.append((current_time,current_process.id))    
                current_time = current_time + current_process.remain_burst_time
                waiting_time = waiting_time + current_time - current_process.arrive_time - current_process.burst_time
            break

        current_process = ready_process_queue.get()
        if current_process.last_scheduled_time != current_time or current_process.arrive_time == 0:
            schedule.append((current_time,current_process.id))

        if current_process.remain_burst_time + current_time <= next_arrival_time:
            current_time = current_process.remain_burst_time + current_time
            waiting_time = waiting_time + current_time - current_process.arrive_time - current_process.burst_time
        else:
            current_process.last_scheduled_time = next_arrival_time
            current_process.remain_burst_time = current_process.remain_burst_time - (next_arrival_time - current_time)
            current_time = next_arrival_time
            put_process_ready_queue(SRTF_processes,ready_process_queue,current_time)
            ready_process_queue.put(current_process)

    return (schedule,waiting_time/length)

def put_process_ready_queue_with_predict(processes,ready_process_queue,current_time,predict_dict,alpha):
    process_remove_indexes = []
    for i in range(0,len(processes)):
        if(processes[i].arrive_time <= current_time):
            guess = predict_dict.get(processes[i].id)
            processes[i].remain_burst_time = guess[0] * (1-alpha) + alpha * guess[1]
            ready_process_queue.put(processes[i])
            process_remove_indexes.append(i)         
    for i in sorted(process_remove_indexes, reverse=True): 
        del processes[i]

def SJF_scheduling(process_list, alpha):
    SJF_processes = copy.deepcopy(process_list)
    if len(SJF_processes) == 0:
        return([],0.0)
    
    schedule = []
    length = float(len(SJF_processes))
    current_time = 0
    waiting_time = 0
    ready_process_queue = Queue.PriorityQueue()
    terminate = False
    ## key is process_id   value:[guess,actual time]
    guess_actual_dict = dict()
    for process in SJF_processes:
         guess_actual_dict[process.id] = [5,0]
    while True:
        ## check terminate condition
        if len(SJF_processes) == 0 and ready_process_queue.empty():
            terminate = True
        if(terminate):
            break
        ## take the ready process from the process_list
        put_process_ready_queue_with_predict(SJF_processes,ready_process_queue,current_time,guess_actual_dict,alpha)
        if ready_process_queue.empty():
            current_time = SJF_processes[0].arrive_time
            ready_process_queue.put(SJF_processes[0])
            SJF_processes.pop(0)
        current_process = ready_process_queue.get()
        schedule.append((current_time,current_process.id))
        
        waiting_time = waiting_time + current_time - current_process.arrive_time
        current_time = current_time + current_process.burst_time

        ##update the predict information
        guess_actual = guess_actual_dict.get(current_process.id)
        guess_actual[1] =  current_process.burst_time
        guess_actual[0] =  guess_actual[0] * (1-alpha) + alpha * guess_actual[1]
        guess_actual_dict[current_process.id] = guess_actual

    return (schedule,waiting_time/length)
    


def read_input():
    result = []
    with open(input_file) as f:
        for line in f:
            array = line.split()
            if (len(array)!= 3):
                print ("wrong input format")
                exit()
            result.append(Process(int(array[0]),int(array[1]),int(array[2])))
    return result
def write_output(file_name, schedule, avg_waiting_time):
    with open(file_name,'w') as f:
        for item in schedule:
            f.write(str(item) + '\n')
        f.write('average waiting time %.2f \n'%(avg_waiting_time))


def main(argv):
    process_list = read_input()
    print ("printing input ----")
    for process in process_list:
        print (process)
    print ("simulating FCFS ----")
    FCFS_schedule, FCFS_avg_waiting_time =  FCFS_scheduling(process_list)
    write_output('FCFS.txt', FCFS_schedule, FCFS_avg_waiting_time )

    print ("simulating RR ----")  ## optimal time_quantum is 10
   
    RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list,time_quantum = 2)
    write_output('RR.txt', RR_schedule, RR_avg_waiting_time )
   
    print ("simulating SRTF ----")
    SRTF_schedule, SRTF_avg_waiting_time =  SRTF_scheduling(process_list)
    write_output('SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time )
    
    print ("simulating SJF ----")    #optimal alpha is 0.0
    
    SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha = 0.5)
    write_output('SJF.txt', SJF_schedule, SJF_avg_waiting_time )
   
if __name__ == '__main__':
    main(sys.argv[1:])

