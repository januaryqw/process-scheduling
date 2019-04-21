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
import copy
try:
    import Queue as Q  # ver. < 3.0
except ImportError:
    import queue as Q

input_file = 'input.txt'

class Process:
    last_scheduled_time = 0
    def __init__(self, id, arrive_time, burst_time):
        self.id = id
        self.arrive_time = arrive_time
        self.burst_time = burst_time
    #for printing purpose
    def __repr__(self):
        return ('[id %d : arrival_time %d,  burst_time %d, last_scheduled_time %d]'%(self.id, self.arrive_time, self.burst_time, self.last_scheduled_time))

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

#Input: process_list, time_quantum (Positive Integer)
#Output_1 : Schedule list contains pairs of (time_stamp, proccess_id) indicating the time switching to that proccess_id
#Output_2 : Average Waiting Time
def RR_scheduling(process_list, time_quantum):
    process_list_clone = copy.deepcopy(process_list)
    schedule = []
    current_time = 0
    waiting_time = 0
    n = len(process_list_clone)
    if n == 0:
        return ([], 0.0)
    
    queue = [process_list_clone.pop(0)]
    last_process = Process(-1, -1, -1)
    while len(queue) > 0:
        process = queue.pop(0)
        if last_process.id != process.id or last_process.arrive_time != process.arrive_time:
            schedule.append((current_time, process.id))
        
        waiting_time += current_time - process.last_scheduled_time

        if process.burst_time - time_quantum > 0:
            current_time += time_quantum
            process.burst_time -= time_quantum
        else:
            current_time += process.burst_time
            process.burst_time = 0

        process.last_scheduled_time = current_time

        # get from the list and put in the queue until current_time
        while len(process_list_clone) > 0:
            new_process = process_list_clone[0]
            if new_process.arrive_time > current_time:
                break
            else:
                process_to_add = process_list_clone.pop(0)
                process_to_add.last_scheduled_time = process_to_add.arrive_time
                queue.append(process_to_add)

        if (process.burst_time > 0):
            queue.append(process)
        elif (len(queue) == 0 and len(process_list_clone) > 0):
            process_to_add = process_list_clone.pop(0)
            process_to_add.last_scheduled_time = process_to_add.arrive_time
            current_time = process_to_add.arrive_time
            queue.append(process_to_add)
        last_process = process

    average_waiting_time = waiting_time/float(n)
    return (schedule, average_waiting_time)

def SRTF_scheduling(process_list):
    process_list_clone = copy.deepcopy(process_list)
    schedule = []
    current_time = 0
    waiting_time = 0
    n = len(process_list_clone)
    if n == 0:
        return ([], 0.0)
    waiting_list = Q.PriorityQueue()
    last_process = Process(-1, -1, -1)
    while (not waiting_list.empty()) or (len(process_list_clone) > 0):
        if waiting_list.empty():
            next_process = process_list_clone.pop(0)
            next_process.last_scheduled_time = next_process.arrive_time
            current_time = next_process.arrive_time
            waiting_list.put((next_process.burst_time, next_process.arrive_time, next_process))
        
        cur_remain, cur_arrive, cur_process = waiting_list.get()

        if last_process.id != cur_process.id or last_process.arrive_time != cur_process.arrive_time:
            schedule.append((current_time, cur_process.id))
        
        waiting_time += current_time - cur_process.last_scheduled_time
        # get the next process
        if len(process_list_clone) > 0:
            next_process = process_list_clone[0]
            if cur_process.burst_time <= next_process.arrive_time - current_time:
                current_time += cur_process.burst_time
                cur_process.burst_time = 0
                cur_process.last_scheduled_time = current_time
                last_process = cur_process
                continue
            else:
                next_process = process_list_clone.pop(0)
                cur_process.burst_time -= next_process.arrive_time - current_time
                current_time = next_process.arrive_time
                cur_process.last_scheduled_time = current_time
                next_process.last_scheduled_time = next_process.arrive_time
                waiting_list.put((cur_process.burst_time, cur_process.arrive_time, cur_process))
                waiting_list.put((next_process.burst_time, next_process.arrive_time, next_process))
                last_process = cur_process
                continue
        else:
            current_time += cur_process.burst_time
            cur_process.burst_time = 0
            cur_process.last_scheduled_time = current_time
            last_process = cur_process
            continue

    average_waiting_time = waiting_time/float(n)
    return (schedule, average_waiting_time)

def SJF_scheduling(process_list, alpha):
    process_list_clone = copy.deepcopy(process_list)
    predicted_burst = {}
    schedule = []
    current_time = 0
    waiting_time = 0
    n = len(process_list_clone)
    if n == 0:
        return ([], 0.0)
    waiting_list = Q.PriorityQueue()
    while (not waiting_list.empty()) or (len(process_list_clone) > 0):
        if waiting_list.empty():
            next_process = process_list_clone.pop(0)
            next_process.last_scheduled_time = next_process.arrive_time
            current_time = next_process.arrive_time
            predict_time = 5
            if next_process.id in predicted_burst:
                predict_time = predicted_burst[next_process.id]
            waiting_list.put((predict_time, next_process.arrive_time, next_process))
        
        predict_time, cur_arrive, cur_process = waiting_list.get()
        schedule.append((current_time, cur_process.id))
        waiting_time += current_time - cur_process.last_scheduled_time

        # process job
        current_time += cur_process.burst_time
        cur_process.last_scheduled_time = current_time
        predicted_burst[cur_process.id] = alpha * cur_process.burst_time + (1 - alpha) * predict_time

        # add next jobs
        while len(process_list_clone) > 0:
            new_process = process_list_clone[0]
            if new_process.arrive_time > current_time:
                break
            else:
                next_process = process_list_clone.pop(0)
                next_process.last_scheduled_time = next_process.arrive_time
                predict_time = 5
                if next_process.id in predicted_burst:
                    predict_time = predicted_burst[next_process.id]
                waiting_list.put((predict_time, next_process.arrive_time, next_process))
    
    average_waiting_time = waiting_time/float(n)
    return (schedule, average_waiting_time)


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
    print ("simulating RR ----")
    RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list,time_quantum = 2)
    write_output('RR.txt', RR_schedule, RR_avg_waiting_time )
    print ("simulating SRTF ----")
    SRTF_schedule, SRTF_avg_waiting_time =  SRTF_scheduling(process_list)
    write_output('SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time )
    print ("simulating SJF ----")
    SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha = 0.5)
    write_output('SJF.txt', SJF_schedule, SJF_avg_waiting_time )



    # find the optimal value of Q [1,10]
    print ("Finding optimal Q for RR ----")
    least_awt = float("inf")
    optimal_q = 11
    for q in range(1,11):
        RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list,time_quantum = q)
        print("Q {} Avg. Waiting Time {}".format(q, RR_avg_waiting_time))
        if RR_avg_waiting_time < least_awt:
            optimal_q = q
            least_awt = RR_avg_waiting_time
    print("Optimal Q is {}".format(optimal_q))
    RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list,time_quantum = optimal_q)
    write_output('RR_{}.txt'.format(optimal_q), RR_schedule, RR_avg_waiting_time )

    # find the optimal value of alpha [0, 1] with precision 2
    print ("Finding optimal alpha for SJF ----")
    least_awt = float("inf")
    optimal_alpha = 0
    for i in range(0, 11):
        alpha = i / 10
        SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha = alpha)
        print("alpha {} Avg. Waiting Time {}".format(alpha, SJF_avg_waiting_time))
        if SJF_avg_waiting_time < least_awt:
            optimal_alpha = alpha
            least_awt = SJF_avg_waiting_time
    print("Optimal alpha is {}".format(optimal_alpha))
    SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha = optimal_alpha)
    write_output('SJF_{}.txt'.format(optimal_alpha), SJF_schedule, SJF_avg_waiting_time )

if __name__ == '__main__':
    main(sys.argv[1:])

