# Close copy of KeithleyV16.py, an interface-wrapper for OssilaV15.py with IV measurement.

import numpy as np
import datetime
import os

import xtralien

import matplotlib.pyplot as plt

from dataclasses import dataclass


@dataclass
class OssilaV16(object):

    __com_no    : int
    __i_range   : int # Current range to use, see manual for details
    __osr       : int # Oversample Rate (OSR) can take values 0-9 for my case (Peter)
    

    def __init__(self, __com_no = 12, __i_range = 3, __osr = 3):
        assert __com_no >= 0 and __com_no <= 20
        assert __i_range >= 1 and __i_range <= 5
        assert __osr >= 0 and __osr <= 9

        self.com_no = __com_no
        self.i_range = __i_range
        self.osr = __osr
        
        self.xtr = xtralien.Device(f'COM{self.com_no}')
        self.xtr.smu1.set.range(self.i_range, response=0)
        self.xtr.smu1.set.osr(self.osr, response=0)
        
        self.xtr.smu1.set.enabled(True, response=0)

        match self.i_range:
            case 1:
                print(f"Current range ±200 mA (no. {self.i_range})")
            case 2:
                print(f"Current range ±20 mA (no. {self.i_range})")
            case 3:
                print(f"Current range ±2 mA (no. {self.i_range})")
            case 4:
                print(f"Current range ±200 µA (no. {self.i_range})")
            case 5:
                print(f"Current range ±20 µA (no. {self.i_range})")
            case _:
                assert False           
           
    def set_v(self, voltage):
        self.xtr.smu1.set.voltage(voltage, response=0)
    
    def get_v(self):
#        return self.xtr.smu1.getvoltage()
        # or
        return self.xtr.smu1.measurev()[0]
    
    def get_i_v(self):
#        return self.xtr.smu1.oneshot(set_voltage)[0]
        # or
        meas = self.xtr.smu1.measure()
        return meas[0]

    
    def iv(self, __begin=0.0, __end=2.0, __step=0.2) -> [list, list]:
        v_limit = 10.0
        assert abs(__begin) <= v_limit
        assert abs(__end) <= v_limit
        assert abs(__step) <= v_limit
        
        if __begin > __end:
            __step = -1 * np.abs(__step)
        else:
            __step = np.abs(__step)        
        
        # self.xtr.smu1.set.enabled(True, response=0)

        # additional measurement to exclude error of first measurement
        self.set_v(__begin)
        self.get_i_v()

        steps = int((__end - __begin) / __step) + 1
        currents = np.zeros(steps)
        voltages = np.empty(steps)
        for i in range(steps):
            voltages[i] = __begin + (__step * i)
            
        for nr in range(steps):
            self.set_v(voltages[nr])
            [voltage, current] = self.get_i_v()
            currents[nr] = current
            #print(str('%.2f' % voltage) +' V; '+str('%.5e' % current)+' A')
        
        self.set_v(0)
        # disable the output
        # self.xtr.smu1.set.enabled(False, response=0)
        
        return [voltages, currents]

    def __del__(self):
        # self.xtr.smu1.set.enabled(False, response=0) # OSError: [WinError 6] Неверный дескриптор       
        self.xtr.close()
        pass

        
def it(__step=1.0, duration=1000):
        return 0
        
def it_from_iv():
        return 0    

def pulsed(warm_up, duration, cool_down, __step):
        return 0

def iv2fig(x, fx, fx_names, filename, showfig=False, savefig=True):
    data2fig(x, fx, fx_names, filename, 'Voltage (v)', 'Current (A)', showfig, savefig)
    
def it2fig(x, fx, fx_names, filename, showfig=False, savefig=True):
    data2fig(x, fx, fx_names, filename, 'Time (s)', 'Current (A)', showfig, savefig)    

def data2fig(x, fx, fx_names, filename, x_name, y_name, showfig=False, savefig=True):
    
    fig = plt.figure(figsize=(8,6))
    if len(fx.shape) == 1:
        plt.plot(x, fx, label=fx_names, linewidth=2)
    else:
        for i in range(fx.shape[0]):
            plt.plot(x, fx[i,:], label=fx_names[i], linewidth=2)

    plt.xlabel(x_name, fontsize=14)
    plt.ylabel(y_name, fontsize=14)
    time_for_title = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    plt.title(time_for_title, fontsize=14)
    plt.tick_params(labelsize = 14)
    plt.legend() #(loc='upper left')
    if savefig == True:
        plt.savefig(filename + '.png')
    if showfig == True:
        plt.show()


def data2file(data, filename, column_names=[]):
#    lists2file(column_names_str, filename_raw, lst_raw)
    delim = ','
    column_names_str = delim.join(column_names)
    
    np.savetxt(filename + '.csv', data, fmt='%.10g', delimiter=delim, header=column_names_str) 


    
if __name__ == "__main__":

    path = './data/'
    if not os.path.exists(path):
       os.makedirs(path)
           
    sweep_start = 0.0
    sweep_step = 0.2
    sweep_end = 5.0
    sample_name = 'rGO_10pc'
    time_for_name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = path + time_for_name + '_' + sample_name +'_IV_' + str(sweep_end)
    
    port = 12
    irange = 3
    averaging = 3
    ossila = OssilaV16(port, irange, averaging)
    [voltages, currents] = ossila.iv(sweep_start, sweep_end, sweep_step) # 

    column_names = ('V','I')
    iv2fig(voltages, currents, column_names[1:], filename, True, True)    
    data2file(np.stack((voltages, currents), axis=0).T, filename, column_names)
    # np.savetxt(filename + '.csv', np.stack((voltages, currents), axis=0).T, fmt='%.10g', delimiter=',', header='Voltage (V), ' + column_names)    
