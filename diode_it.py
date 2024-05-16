import OssilaV16
import datetime
import time
import numpy as np
import matplotlib.pyplot as plt
import csv
import os

bias = 1.0 # V

port = 11
irange = 3
averaging = 3
ossila = OssilaV16.OssilaV16(port, irange, averaging)
step = 2.0 # in sec. 

sample_name = 'rGO_10pc'
time_for_name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
path = './data/'
if not os.path.exists(path):
   os.makedirs(path)
   
filename = path + time_for_name + '_' + sample_name +'_it_' + str(bias)



print("Sample set name: ", sample_name)

with open(filename + '.csv', 'a') as csvfile:
        writer = csv.writer(csvfile,  lineterminator='\n')
        writer.writerow(["# Time (sec)", "Drain (A)", "Drain (V)"])

current_log = []
time_log = []


plt.ion()  # enable interactivity
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

try:
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



except KeyboardInterrupt:
    pass
    

plt.ioff()

OssilaV16.it2fig(time_log, current_log, 'Time, s', filename, showfig=True, savefig=True)
plt.show()

