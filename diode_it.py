import OssilaV16
import datetime
import time
import numpy as np
import matplotlib.pyplot as plt
import csv
import os

from threading import Thread, Event

bias = 1.0 # V
port = 5
irange = 3
averaging = 3
step = 2.0 # in sec. 

sample_name = 'rGO_10pc'
path = './data/'


def read_input(q_entered_event):
    c = input()
    if c == "q":
        print("Breaking")
        q_entered_event.set()
        
        

def measurement_it(filename, step):
    '''
    comments...
    comments...
    '''
    with open(filename + '.csv', 'a') as csvfile:
            writer = csv.writer(csvfile,  lineterminator='\n')
            writer.writerow(["# Time (sec)", "Drain (A)", "Drain (V)"])

    current_log = []
    time_log = []


    fig = plt.figure()  # make a figure
    ax = fig.add_subplot(111)
    line1, = ax.plot(time_log, current_log, 'r.')
    #line1, = ax.plot(time_arr, drain_current, label = r'$I_{DS}$', color='red', linewidth=2)
    plt.xlabel('Time / s', fontsize=14)
    plt.ylabel('Current / A', fontsize=14)
    plt.title(time_for_name + r', $V_{DS}$ = ' + str(bias), fontsize=14)
    plt.tick_params(labelsize = 14)

    # to skip drawing of first dot (draws with a big delay)
    line1.set_xdata(time_log)
    line1.set_ydata(current_log)
    ax.relim()
    ax.autoscale()
    fig.canvas.draw()
    fig.canvas.flush_events()
    ossila.set_v(bias)
    ossila.get_v()
    time.sleep(step)

    q_pressed_event = Event()
    input_thread = Thread(target=read_input, daemon=True, args=(q_pressed_event,)) 
    input_thread.start()
    message  = "***   Press q and Enter to stop the measurement  ***"
    print("="*len(message) + '\n' + message + '\n' + "="*len(message))
    
    #keithley.get_i_v()
    #time.sleep(step)
    start = time.time()


    while True:

        nt = time.time()

        while (nt - start) < (step * (len(time_log))):
            #print(f'{len(time_arr)=}, until next meas {-(nt - start) + (step * len(time_arr))}')
            nt = time.time() 
        [voltage, current] = ossila.get_i_v()
        current_log.append(current)
        time_log.append(nt - start)
        
        print('%.2f' % (nt - start), ' sec; ', current, ' A')
        # Write the data in a csv
        with open(filename + '.csv', 'a') as csvfile:
            writer = csv.writer(csvfile,  lineterminator='\n')
            writer.writerow(['%.3f' % (nt - start), current, bias])

        line1.set_xdata(time_log)
        line1.set_ydata(current_log)
        ax.relim()
        ax.autoscale()
        fig.canvas.draw()
        fig.canvas.flush_events()

        if q_pressed_event.is_set():
            break



ossila = OssilaV16.OssilaV16(port, irange, averaging)

time_for_name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
if not os.path.exists(path):
   os.makedirs(path)
   
filename = path + time_for_name + '_' + sample_name +'_it_' + str(bias)

print("Sample name: ", sample_name)

plt.ion()  # enable interactivity

try:
    measurement_it(filename, step)
    
# To catch attempts to stop by previously used ^c way
except Exception as err:
    #print(f"Catched error: {type(err).__name__}")
    pass



    

plt.ioff()
plt.close("all")
ossila.set_v(0)

recorded = np.loadtxt(filename + '.csv', delimiter=',')
OssilaV16.it2fig(recorded[:,0], recorded[:,1], ['Time, s'], filename, showfig=True, savefig=True)
# OssilaV16.it2fig(filename, recorded[:,0], recorded[:,1], ['Time, s'], showfig=True, savefig=True)

'''
def it2fig(x, fx, fx_names, filename, showfig=False, savefig=True):
    data2fig(x, fx, fx_names, filename, 'Time (s)', 'Current (A)', showfig, savefig)    

def data2fig(x, fx, fx_names, filename, x_name, y_name, showfig=False, savefig=True):
'''    
