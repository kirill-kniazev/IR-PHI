
############################################################################
####                        INITIAL PARAMETERS                           ###
############################################################################


sample_name = 'PMMA'

#Image area
x1, x2 = 45, 55 # edit here, real area to be scanned in microns, format: inital position, final position
x_stepsize = 0.1 # edit here, enter stepsize in um1

y1, y2 = 45, 55 # edit here, real area to be scanned in microns, format: inital position, final position
y_stepsize = 0.1 # edit here, enter stepsize in um

############################################################################
############################################################################


import pyqtgraph as pg
import numpy as np
import sys
import Piezo_Stage
from time import sleep
from PyQt4 import QtCore, QtGui
import time
import os
from datetime import datetime as dt
import zhinst.ziPython, zhinst.utils
from numpy import *
import time, math



x3= x2-x1 
len_x = ((x2-x1)/x_stepsize) + 1  # this is the number of steps in which the scan length will be divided


#2DLockinScan_PHI_ZHinst

start_time = time.time()
#Lock-in parameters and initialization
rate=1000 #lock-in to PC data transfer rate Sa/s
integration_time = 0.1
#tc=0.03 #time constant in seconds. min 0.1
#integration_time=tc*3.3 #integration time in seconds (dwell time)
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

# for stage initialization:
piezo = Piezo_Stage.madpiezo()
piezo.mcl_start()
piezo.goxy(0.0, 0.0)
piezo.goz(0.0)

#for real-time ploting
win = pg.GraphicsWindow()

app = QtGui.QApplication(sys.argv)

win = QtGui.QMainWindow()
#win.resize (1000,350) Size for the theta map inclusion
win.resize (500,350)
win.setWindowTitle ('2D')

cw =QtGui.QWidget()
win.setCentralWidget(cw)
windw = QtGui.QGridLayout()
cw.setLayout(windw)

R_plot = pg.ImageView()  #plot
Theta_plot = pg.ImageView()

windw.addWidget(R_plot, 0, 0)
#windw.addWidget(Theta_plot, 0, 1) # Shows the phase map in real time
win.show()

# set 2D scan parameters

y3=y2-y1
len_y = ((y2-y1)/y_stepsize) + 1  # this is the number of steps in which the scan length will be divided

x_pattern, y_pattern = np.meshgrid(np.linspace(x1, x2, int(len_x)), np.linspace(y1, y2, int(len_y)))

print x_pattern
print "**********************************************************************************************"
print y_pattern

time_experiment = len_y*len_x*(integration_time+0.04)/60
print ('experiment length %s  min' %time_experiment)

cur_time = dt.now()
f_name_prefix = str(cur_time.day)+'-' + str(cur_time.month)+"-" + str(
    cur_time.year)+"-" "%1.2d"%cur_time.hour+"%1.2d"%cur_time.minute+"_"+sample_name
dir_name = "C:\\Users\\Administrator\\Documents\\Ilia\\Data\\scans\\IR-PHI_maps\\" + f_name_prefix #"C:\\Users\\Administrator\\Documents\\Ilia\\Data\\scans\\IR-PHI_maps\\" + f_name_prefix

if os.path.exists(dir_name):  # check if folder already exists
    if os.listdir(dir_name):  # check if folder is empty
        dir_name = dir_name + "_1"  # change folder name if folder is not empty
        os.makedirs(dir_name)  # create another foder if folder is not empty
else:
    os.makedirs(dir_name)


# create 2D arrays to store data
scan_shape = np.shape(x_pattern)

#print scan_shape
#print (np.ndindex(scan_shape))
#sleep(1000)

data_lockin = np.zeros(scan_shape)
data_theta = np.zeros(scan_shape)
data_theta_rad = np.zeros(scan_shape)
data_x = np.zeros(scan_shape)
data_y = np.zeros(scan_shape)

# move to initial points of scan area
piezo.goxy(x1, y1)
piezo.goz(50)  # edit here, enter required z-value
sleep(2)

# loop for 2D scan
for index in np.ndindex(scan_shape):
    piezo.goxy(x_pattern[index], y_pattern[index])
    t2 = time.time()
    sleep(integration_time)  # dwell(integration) time in seconds
    sample = daq.getSample('/'+device+'/demods/0/sample') #Record one demodulator sample from the specified node, data here consist of everything lock-in have
    data_lockin[index] = float(sqrt(sample['x']**2+sample['y']**2)) #Extract R value from sample data
    data_theta_rad[index] = math.atan(float(sample['y'])/float(sample['x'])) #extract theta values from sample data
    data_theta[index] = np.rad2deg(math.atan(float(sample['y'])/float(sample['x'])))
    data_x[index] = float(sample['x'])
    data_y[index] = float(sample['y'])
    t3 = time.time()
    QtCore.QCoreApplication.processEvents()
    time_ms = round((t3-t2)*1000, 2) 
    print index, x_pattern[index], y_pattern[index], 'theta=', data_theta[index], 'R=', data_lockin[index], '; t=', time_ms, 'ms'
    R_plot.setImage(data_lockin)
    Theta_plot.setImage(data_theta)

    #except float(lockinA.data) == 0
        #print "the beam blocked"


# edit here, filename for saved data
#np.savetxt(dir_name + "\\" + "MA_IRPHI_test1_4V_FAMACsPbI3_20x65um_500nmstep_100mstc_300msint_1450cm-1-pump_1064nm-probe_1ODIR_21percentNIR.dat", data_lockin, fmt='%1.4f', delimiter=",", newline=",\n")
#np.savetxt(dir_name + "\\" + "FA_IRPHI_test2c_5V_FAMACsPbI3_30x65um_500nmstep_100mstc_220msint_1710cm-1-pump_1064nm-probe_1ODIR_21percentNIR.dat", data_lockin, fmt='%1.4f', delimiter=",", newline=",\n")
#np.savetxt(dir_name + "\\" + "abs_map_test2-1_FAPbI3_532_3OD_10dBGain_Si-det_10x10um_250nmsptep_.csv", data_lockin, delimiter=",")
#np.savetxt(dir_name + "\\" + "PHI_532nm-1,5V-50mW_3000cm-1_CaF2_PMMA_05um_0,3D-Ir_100ms_300ms_6x6um_100nmstep_test4.csv", data_lockin, delimiter=",")
#np.savetxt(dir_name + "\\" +str(x3)+"x"+str(y3)+"_um_.txt", data_lockin, delimiter=",") # Uneeded
#np.savetxt(dir_name + "\\" + "theta_map.txt", data_theta, delimiter=",")   # saving the phase at each pixel
np.savetxt(dir_name + "\\" + "map_"+"TC="+str(int((tc*1000)))+"ms"+"_area = "+str(x3)+"x"+str(y3)+"um.txt", data_lockin, delimiter=",")
#np.savetxt(dir_name + "\\" + "x_map.txt", data_x, delimiter=",") #Unknown purpose
#np.savetxt(dir_name + "\\" + "y_map.txt", data_y, delimiter=",") #Unknown purpose


# to reset stage to 0,0 position and disconnect
piezo.goxy(0.0, 0.0)
piezo.goz(0.0)
piezo.mcl_close()
end_time = time.time()
time_req = (end_time - start_time)/60
print 'Time required = ',time_req,' m'

sys.exit(app.exec_())  # end code for scan
