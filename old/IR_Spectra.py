############################################################################
####                        INITIAL PARAMETERS                           ###
############################################################################


sample_name = 'PMMA_t6check-10212021'



############################################################################
############################################################################
















































#WavelengthScan_PHI _ZHinst

import numpy as np
import sys
import Piezo_Stage
import zhinst.ziPython, zhinst.utils
from numpy import *
import time
import Firefly3 #192.168.1.100
import Firefly3_a #192.168.1.187
from time import sleep
import pyqtgraph as pg
import ThorLabs_PM100_PowerMeter as PM
from PyQt4 import QtCore, QtGui
import os
from datetime import datetime as dt


start_time = time.time()

app = QtGui.QApplication(sys.argv)
#Lock-in parameters and initialization
rate=1000 #lock-in to PC data transfer rate Sa/s
tc=0.03 #time constant in seconds 
integration_time=tc*5 #integration time in seconds
scaling=sqrt(1) #RMS to PP convertation scaling
daq = zhinst.ziPython.ziDAQServer('192.168.70.26', 8004, 5) # Open connection to ziServer of lock-in
device = zhinst.utils.autoDetect(daq, exclude=None) #detect lock-in and record it address
#Set test settings, you can add more settings here
t1_sigOutIn_setting = [
   [['/'+device+'/demods/0/order'], 8], #low pass filter slope. 1-8, higher number gives beeter slope and slower response
   [['/'+device+'/demods/0/timeconstant'], tc], #set time constant
   [['/'+device+'/demods/0/rate'], rate], #set data transfer rate
   [['/'+device+'/sigins/0/scaling'], scaling], #set scaling
   [['/'+device+'/extrefs/0/enable'], 1], #enable external reference channel
   ]
daq.set(t1_sigOutIn_setting) #apply all settings
time.sleep(1)# wait 1s to get a settled lowpass filter
daq.flush() #clean queue

#meter = PM.power_meter(serial_port='1')

cur_time = dt.now()
f_name_prefix = str(cur_time.day)+'-' + str(cur_time.month)+"-" + str(
    cur_time.year)+"-" "%1.2d"%cur_time.hour+"%1.2d"%cur_time.minute+"_"+sample_name
dir_name = "C:\\Users\\Administrator\\Documents\\Ilia\\Data\\scans\\IR-PHI_spectra\\" + f_name_prefix

if os.path.exists(dir_name):  # check if folder already exists
    if os.listdir(dir_name):  # check if folder is empty
        dir_name = dir_name + "_1"  # change folder name if folder is not empty
        os.makedirs(dir_name)  # create another foder if folder is not empty
else:
    os.makedirs(dir_name)

# for stage initialization:
piezo = Piezo_Stage.madpiezo()
piezo.mcl_start()
piezo.goxy(0.0, 0.0)
piezo.goz(0.0)

x_position = 50.0 # edit here, input x,y positions from line scans
y_position = 50.0  #edit here, input x,y positions from line scans
z_position = 50.0    # edit here, required z position

piezo.goxy(x_position, y_position)
piezo.goz(z_position)

lambda1, lambda2 = 1550, 1800  # edit here, wavelength range for spectrum in nm, format: initial wavelength, final wavelength
lambda_stepsize = 2 # edit here, enter stepsize in nm, if >5nm steps, change sleep time in Firefly3 library
len_lambda = ((abs(lambda2-lambda1))/lambda_stepsize) + 1  # this is the number of steps in which the scan length will be divided

lambda_pattern = np.linspace(lambda1, lambda2, len_lambda)

print lambda_pattern
print "********************************************"

scan_shape = np.shape(lambda_pattern)
#data_PM = np.zeros(scan_shape)
data_lockin = np.zeros(scan_shape)
data_norm = np.zeros(scan_shape)
#data_lockinA = np.zeros(scan_shape)
#data_sigma = np.zeros(scan_shape)

# create empty lists for y axes on the plot
data1 = np.zeros(scan_shape)
pw = pg.plot() # calling the plot function

# for Firelfy laser initialization:
#Firefly3 = Firefly3.Firefly3(sock=None) #short WL
Firefly3 = Firefly3_a.Firefly3(sock=None) #long WL
Firefly3.go_to_wavelength(lambda1)
sleep(5)  # to allow Firefly to change wavelength
print piezo.get_position()
#spectrum measurement
for index in np.ndindex(scan_shape):
    Firefly3.go_to_wavelength(lambda_pattern[index])
    #meter.read_value()
    sleep(integration_time)  # dwell(integration) time in seconds
    sample = daq.getSample('/'+device+'/demods/0/sample') #Record one demodulator sample from the specified node, data here consist of everything lock-in have
    data_lockin[index] = float(sqrt(sample['x']**2+sample['y']**2)) #Extract R value from sample data
    
    print index, lambda_pattern[index], data_lockin[index], 'tc=',tc, '; dwell=',integration_time
    pw.plot(lambda_pattern, data_lockin, clear=True, pen='r')
    pg.QtGui.QApplication.processEvents()


data_lockin_norm = data_lockin/np.max(data_lockin)
full_data = np.vstack((lambda_pattern, data_lockin, data_lockin_norm)).T
np.savetxt(dir_name + "\\" + sample_name +".csv", full_data, delimiter=",")
#np.savetxt(dir_name + "\\" + "1041-1721_cm-1.csv", data_lockin, delimiter=",")
#np.savetxt("PHI_CaF2_532_1,5V_0,3_OD-Ir_05um-PMMA_1s-3s_2700-4000_5cm-1step_test3.csv", data_lockin, delimiter=",")
#np.savetxt("PHI_532_ITO-3_TEMgrid_300ms-1s_2700-4000_10cm-1step_rand.csv", data_norm, delimiter=",")
#np.savetxt("08umbeads_sms500Hz2,25v_realigned_test4_z=19_ref-dc500Hz_3stc_10sint_2800-3150cm-1_2cm-1step_2-OD-filter_sigma.csv", data_sigma, delimiter=",")

# to reset laser wavelength
Firefly3.go_to_wavelength(1041)
sleep(10)

end_time = time.time()
time_req = (end_time - start_time)/60
print(time_req, 'min')

# to reset stage to 0,0 position and disconnect
piezo.goxy(0.0, 0.0)
piezo.goz(0.0)
piezo.mcl_close()

sys.exit(app.exec_())  # end code for scan
