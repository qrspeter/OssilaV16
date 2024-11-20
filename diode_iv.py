import OssilaV16
import datetime
import numpy as np
import matplotlib.pyplot as plt
import os

sweep_start = 0.0
sweep_step = 0.2
sweep_end = 1.0

port = 12
irange = 3
averaging = 3
ossila = OssilaV16.OssilaV16(port, irange, averaging)

sample_name = 'rGO_100pc-NPl'
time_for_name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
path = './data/'
if not os.path.exists(path):
   os.makedirs(path)
   
time_for_name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
filename = path + time_for_name + '_' + sample_name +'_IV_' + str(sweep_end)


column_names = []
data = []
column_names.append("Voltage (V)")
'''
voltages = np.empty(steps)
for i in range(steps):
    voltages[i] = sweep_start + (sweep_step * i)

data.append(voltages)
'''
print("Sample set name: ", sample_name)


while True:
    print('Enter sample label (or press Enter to finish): ')
    sample_num = input()
    if sample_num == "":
        break
    column_names.append(sample_num)
    [voltages, currents] = ossila.iv(sweep_start, sweep_end, sweep_step)
    if data == []:
        data.append(voltages)
    data.append(currents)
    OssilaV16.iv2fig(voltages, currents, ' ', filename, showfig=True, savefig=False)
    plt.show()

np_data = np.stack(data, axis=0)   

OssilaV16.data2file(np_data.T, filename, column_names)
OssilaV16.iv2fig(np_data[0,:], np_data[1:,:], column_names[1:], filename, showfig=True, savefig=True)