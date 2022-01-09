import os,sys,inspect
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton,
                             QMessageBox, QFileDialog, QHBoxLayout)
from PyQt5 import uic
from PyQt5.QtCore import QTimer, QEventLoop, QCoreApplication


# to add parent dir to path
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from datetime import datetime

from madpiezo import Madpiezo
import numpy as np
from time import sleep, time
import re
# import Firefly_SW #192.168.1.229, separate py file
# import Firefly_LW #192.168.1.231, , separate py file
# import zhinst.ziPython, zhinst.utils
# import matplotlib.pyplot as plt
# from mpl_toolkits.axes_grid1 import make_axes_locatable

import pyqtgraph as pg


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi("piezo.ui", self)
        
        ## CONSTANTS
        self.SLEEP_TIME = 1 # in sec
        
        self.XYZ_LEFT_BORDER = 0 # position, μm
        self.XYZ_RIGHT_BORDER = 300 # position, μm
        
        self.WAVENUM_LEFT_BORDER = 1041 # wavenumber, cm⁻¹
        self.WAVENUM_RIGHT_BORDER = 1843 # wavenumber, cm⁻¹
        
        ## LOCK-IN PARAMETERS BY DEFAULT
        self.filter_slope = 8 
        self.time_constant = 0.03
        self.data_transafer_rate = 1000
        self.scaling = 1
        self.channel = 1
        self.fast_mode = 0

        ## VARIABLES
        self.initialized = False # check initialize status
        
        ## BUTTONS GROUP
        self.buttons = (self.BUT_apply_param_IMAGING, 
                        self.BUT_start_imag_IMAGING, 
                        self.BUT_go_GO_TO_POSITION,
                        self.BUT_go_to_origin_GO_TO_POSITION,
                        self.BUT_apply_param_SPECTRA,
                        self.BUT_start_spec_SPECTRA)
        
        #============================== SLOTS =================================

        self.BUT_initialize.clicked.connect(self.on_initialize)

        self.BUT_apply_param_IMAGING.clicked.connect(self.on_imag_apply_parameters)
        self.BUT_start_imag_IMAGING.clicked.connect(self.on_imag_start)

        self.BUT_apply_param_SPECTRA.clicked.connect(self.on_spec_apply_parameters)
        self.BUT_start_spec_SPECTRA.clicked.connect(self.on_spec_start)

        self.BUT_go_GO_TO_POSITION.clicked.connect(self.on_go)
        self.BUT_go_to_origin_GO_TO_POSITION.clicked.connect(self.on_go_to_origin)

        self.action_save_r.triggered.connect(self.on_save_r)
        self.action_save_theta.triggered.connect(self.on_save_theta)
        
        #============================== /SLOTS ================================
    
    def on_initialize(self):
        """
        Action when "Initialize" button is clicked 
        
        """
        text = self.BUT_initialize.text()
        if text == "INITIALIZE":
            
            try:
                # initialize piezo stage
                self.piezo = Madpiezo() 
                
                # initialize laser
                self.ff3 = Firefly_LW.Firefly_LW(sock=None) # long WL
                
                if self.piezo.handler != 0: # is good
                    self.BUT_initialize.setText("Stop")
                    self.BUT_initialize.setStyleSheet('QPushButton {background-color: red; color: white;}')
                    
                    # make buttons enabled
                    self.BUT_go_GO_TO_POSITION.setEnabled(True)
                    self.BUT_go_to_origin_GO_TO_POSITION.setEnabled(True)
                    
                    # initial coords when initialized. Edit here if needed
                    self.piezo_go_to_position(50, 50, 50) 
                
                    # used as a flag for some GUI elements
                    self.initialized = True 
                    
                    self.break_scan_loop = False # for emergency abort
                    self.experiment_type = None
                    
                    self.statusbar.showMessage("Successfully initialized!")
                    
                    
                else: # is bad
                
                    QMessageBox.warning(self, "Warning", "Error initializing!")
                    self.BUT_initialize.setText("Error initializing!")
                    self.BUT_initialize.setStyleSheet('QPushButton {background-color: yellow; color: black;}')
                    self.statusbar.showMessage("Error!")
                    
            except Exception as e: # is bad
                QMessageBox.critical(self, "Error", str(e))
                self.BUT_initialize.setText("Error initializing!")
                self.BUT_initialize.setStyleSheet('QPushButton {background-color: yellow; color: black;}')
                self.statusbar.showMessage("Error!")
                
        elif text == "Stop":
            self.piezo_stop()
            self.action_monitor_r.setEnabled(False)
            
            ex_type = self.experiment_type
            
            if ex_type == "Imaging":
                self.break_scan_loop = True
                self.statusbar.showMessage("Emergency abort imaging!")
                self.imag_win.close()
                
            elif ex_type == "Spectra":
                self.break_scan_loop = True
                self.ff3.go_to_wavelength(self.wavenum_pattern[0])
                self.statusbar.showMessage("Emergency abort spectra!")
                self.spec_win.close()
    
                
    def on_monitor_current_r(self):
        """
        Action when "Monitoring R" is chosen from menu.
        
        """
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Monitoring R")
        
        self.msgBox.show()
        
        while True:
            
            # read data
            sample = self.daq.getSample('/' + self.device + '/demods/0/sample')
            sample_x = float(sample['x'])
            sample_y = float(sample['y'])
            r_value = np.hypot(sample_x, sample_y) # sqrt(x^2 + y^2)
            
            prefix = "R: "
            st = prefix + str(round(r_value * 1E6, 6)) + " μV"
            dlg.setText(st)
        
            loop = QEventLoop()
            QTimer.singleShot(200, loop.quit)
            loop.exec_()
            
            
    def read_position(self):
        """
        Read and write current position of piezo stage

        """
        coords = self.piezo.get_position()
        
        self.LAB_x_val_CURRENT_VALUES.setText( str(round(coords[0], 2)) )
        self.LAB_y_val_CURRENT_VALUES.setText( str(round(coords[1], 2)) )
        self.LAB_z_val_CURRENT_VALUES.setText( str(round(coords[2], 2)) )
        
        
    def xyz_is_in_proper_range(self, x, y, z):
        """
        Checks that x, y, z coords are in proper range

        """
        flag = ((self.XYZ_LEFT_BORDER <= x <= self.XYZ_RIGHT_BORDER) and
                (self.XYZ_LEFT_BORDER <= y <= self.XYZ_RIGHT_BORDER) and 
                (self.XYZ_LEFT_BORDER <= z <= self.XYZ_RIGHT_BORDER))
        return flag
    
    
    def piezo_go_to_position(self, x, y, z):
        """
        1. Set coords for piezo stage.
        2. Then some "sleep" to reach position.
        3. Read and write current position.

        """
        self.piezo.goxy(x, y)
        self.piezo.goz(z)
        sleep(self.SLEEP_TIME) # "sleep" for gui
        self.read_position() # write current position 
        
        
    def set_lockin_parameters(self, 
                              filter_slope, 
                              time_constant, 
                              data_transafer_rate,
                              scaling,
                              enable_external_channel):
        """
        Tries to set-up lock-in parameters from spinbpxes.

        """
        try:
                        
            # open connection to ziServer of lock-in
            # edit here if needed
            self.daq = zhinst.ziPython.ziDAQServer('192.168.70.26', 8004, 5)
            
            # detect lock-in and record its address
            self.device = zhinst.utils.autoDetect(self.daq, exclude=None)
        except Exception:            
            QMessageBox.critical(self, "Error", "Error while opening ziServer!")
            return -1
        
        try:
            # set test settings
            t1_sigOutIn_setting = [
            # low pass filter slope. 1-8, higher number gives better slope
            # and slower response
            [['/' + self.device + '/demods/0/order'], filter_slope], 
            # set time constant
            [['/' + self.device + '/demods/0/timeconstant'], time_constant], 
            # set data transfer rate
            [['/' + self.device + '/demods/0/rate'], data_transafer_rate], 
            # set scaling
            [['/' + self.device + '/sigins/0/scaling'], scaling], 
            # enable external reference channel
            [['/' + self.device + '/extrefs/0/enable'], enable_external_channel], 
            ]
            
            # apply all settings
            self.daq.set(t1_sigOutIn_setting) 
            
            sleep(self.SLEEP_TIME) # wait for getting a settled lowpass filter
            self.daq.flush() # clean queue
            
        except Exception:
            QMessageBox.critical(self, "Error", "Error setting lock-in parameters!")
            return -1
        
        
    def piezo_stop(self):
        """
        Tries to stop piezo stage.

        """
        try:
            self.piezo_go_to_position(0, 0, 0)     
            self.piezo.mcl_close()
            
            self.initialize_button.config(text="Initialize", bg="green")
            self.go_button_lf1.configure(state="disabled")
            self.go_to_origin_button_lf1.configure(state="disabled")
            
            self.initialized = False
        except Exception:
            QMessageBox.critical(self, "Error", "Error stopping piezo!")
            return -1
        
        
    def on_go(self):
        """
        Tries to move piezo stage to entered coords.

        """
        try:    
            # read data from spinboxes
            x = self.SPIN_x_GO_TO_POSITION.value()
            y = self.SPIN_y_GO_TO_POSITION.value()
            z = self.SPIN_z_GO_TO_POSITION.value()
        except Exception:
            QMessageBox.warning(self, "Warning", "Bad values! Enter numbers.")
            return -1
        
        # check if values are in proper ranges  
        if self.xyz_is_in_proper_range(x, y, z):
            self.piezo_go_to_position(x, y, z)
        else:
            QMessageBox.warning(self, "Warning", "Values must be in proper ranges! Try again.")
            
            
    def on_go_to_origin(self):
        """
        Moves piezo stage to origin.

        """
        # edit here if needed
        self.piezo_go_to_position(50, 50, 50)
        
      
    def is_imag_param_good(self, z, x1, y1, x2, y2, delta_x, delta_y):
        """
        Checks whether entered imaging parameters are good.

        """
        z_bool = self.XYZ_LEFT_BORDER <= z <= self.XYZ_RIGHT_BORDER
        x1_bool = self.XYZ_LEFT_BORDER <= x1 <= self.XYZ_RIGHT_BORDER
        y1_bool = self.XYZ_LEFT_BORDER <= y1 <= self.XYZ_RIGHT_BORDER
        
        x2_bool = x1 < x2 <= self.XYZ_RIGHT_BORDER
        y2_bool = y1 < y2 <= self.XYZ_RIGHT_BORDER
        
        delta_x_bool = 0 < delta_x <= (x2 - x1)
        delta_y_bool = 0 < delta_y <= (y2 - y1)
        
        total_bool = (z_bool * x1_bool * y1_bool * x2_bool * y2_bool * 
                      delta_x_bool * delta_y_bool)
        return total_bool
    
    
    def is_lockin_param_good(self, filter_slope, time_constant, 
                    data_transafer_rate, scaling, enable_external_channel):
        """
        Checks if lock-in parameters are good
        
        """
        
        ## WRITE A CHECK FUNCTION HERE IF NEEDED!
        
        return True
    
    
    def on_save_r(self):
        """
        Save "R" data after the experiment
        
        """
        if self.experiment_type == "Imaging":     
            dir_name = "C:\\Users\\Administrator\\OneDrive - nd.edu\\Documents\\Measurements\\Maps"

        elif self.experiment_type == "Spectra":
            dir_name = "C:\\Users\\Administrator\\OneDrive - nd.edu\\Documents\\Measurements\\Spectra\\"
            
        try:
            
            date = datetime.today().strftime('[%Y-%m-%d@%H.%M] ')
            
            fname = QFileDialog.getSaveFileName(self, "Save R", dir_name + date, ".csv")[0]
            np.savetxt(fname, self.r_data, delimiter=",")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
       
        else:
            QMessageBox.information(self, "Information", "File was successfully saved!")
            
            
    def on_save_theta(self):
        """
        Save "Theta" data after the experiment
        
        """
        if self.experiment_type == "Imaging":     
            dir_name = "C:\\Users\\Administrator\\OneDrive - nd.edu\\Documents\\Measurements\\Maps"
        elif self.experiment_type == "Spectra":
            dir_name = "C:\\Users\\Administrator\\OneDrive - nd.edu\\Documents\\Measurements\\Spectra\\"
            
        try:
            
            date = datetime.today().strftime('[%Y-%m-%d@%H.%M] ')
            
            fname = QFileDialog.getSaveFileName(self, "Save Theta", dir_name + date, ".csv")[0]
            np.savetxt(fname, self.theta_data, delimiter=",")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
       
        else:
            QMessageBox.information(self, "Information", "File was successfully saved!")
        

    def read_current_wavelength(self, ff3, final_wavenumber=None):
        """
        Read and write current wavenumber
        
        """
        
        try:
            pattern = r"\"current_wavelength\":\[(\d+\.\d+)\]"
            status = ff3.wavelength_status()
            status = status.decode("utf-8")
            current_wavenumber = round(float(re.findall(pattern, status)[0]), 2)
            self.LAB_nu_val_CURRENT_VALUES.setText( str(current_wavenumber) )  
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
        
        if final_wavenumber is not None:
            try:
                delta = 3 
                
                # disable buttons while wavenumber is changing
                for button in self.buttons:
                    button.setEnabled(False)
                    
                while (abs((final_wavenumber - current_wavenumber)) > delta):
                    
                    #! MAYBE SOME UPDATE FUNC IS NEEDED
                    
                    status = str(ff3.wavelength_status())
                    current_wavenumber = round(float(re.findall(pattern, status)[0]), 2)
                    self.LAB_nu_val_CURRENT_VALUES.setText( str(current_wavenumber) ) 
                    sleep(0.2)
                
                # read value for the final time
                status = str(ff3.wavelength_status())
                current_wavenumber = round(float(re.findall(pattern, status)[0]), 2)
                self.LAB_nu_val_CURRENT_VALUES.setText( str(current_wavenumber) )
                
                # make buttons enabled
                for button in self.buttons:
                    button.setEnabled(True)
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))


    def on_imag_apply_parameters(self):
        """
        An action when "Apply" button (IMAGING) is pressed.
        
        """
        # used when saving file
        self.experiment_type = "Imaging"
        
        # make "save" actions disabled
        self.action_save_r.setEnabled(False)
        self.action_save_theta.setEnabled(False)
        
        if self.initialized: # if piezo initialized
            try:    
                # read scan area parameters
                z = self.SPIN_z_IMAGING.value()
                
                # "self" to be used elsewhere
                self.x1 = self.SPIN_x1_IMAGING.value()
                self.y1 = self.SPIN_y1_IMAGING.value()
                self.x2 = self.SPIN_x2_IMAGING.value()
                self.y2 = self.SPIN_y2_IMAGING.value()
                
                delta_x = self.SPIN_delta_x_IMAGING.value()
                delta_y = self.SPIN_delta_y_IMAGING.value()
                
            except Exception:
                QMessageBox.critical(self, "Error", "Error while reading imaging parameters!")
                return -1
            
            try:
                # read lock-in parameters
                
                #! TODO: add function to set lock-in parameters 
                
                filter_slope = self.filter_slope
                time_constant = self.time_constant
                data_transafer_rate = self.data_transafer_rate
                scaling = self.scaling
                enable_external_channel = self.channel
   
            except Exception:
                QMessageBox.critical(self, "Error", "Error while reading lock-in parameters!")
                return -1
                        
            scan_param_bool = self.is_imag_param_good(z, 
                                                      self.x1,
                                                      self.y1, 
                                                      self.x2, 
                                                      self.y2,
                                                      delta_x, 
                                                      delta_y)
            
            # check whether lock-in values are good
            lockin_param_bool = self.is_lockin_param_good(filter_slope,
            time_constant, data_transafer_rate, scaling, enable_external_channel)
                            
            # True if everything is fine
            is_proper_values = scan_param_bool and lockin_param_bool  
            
            if is_proper_values != 1:
                QMessageBox.warning(self, "Warning", "Check entered values for consistency!")
                return -1
            
            # aprox time const for imaging in sec
            self.INTEGRATION_TIME_IMAGING = time_constant * 3.3 

            self.PROGBAR_pb1_IMAGING.setValue(0) # initialize prog bar
            
            # try to set lock-in parameters
            self.set_lockin_parameters(filter_slope, 
                                       time_constant, 
                                       data_transafer_rate,
                                       scaling,
                                       enable_external_channel)
            
            # number of steps in "x" direction
            len_x = int( ((self.x2 - self.x1) / delta_x) ) + 1
            
            # number of steps in "y" direction
            len_y = int( ((self.y2 - self.y1) / delta_y) ) + 1
            
            # create a 2d grid of x and y scanning positions
            self.x_pattern, self.y_pattern = np.meshgrid(np.linspace(self.x1, 
                                                                     self.x2, 
                                                                     len_x), 
                                                         np.linspace(self.y1, 
                                                                     self.y2, 
                                                                     len_y))
            
            # go to the initial position of the scan
            self.piezo_go_to_position(self.x1, self.y1, z)
            
            wavenum = self.SPIN_scan_wavenum_IMAGING.value()
            
            # go to initial wavelength
            self.ff3.go_to_wavelength(wavenum)
            self.read_current_wavelength(self.ff3, final_wavenumber=wavenum)
            
            # make "start imaging" button active
            self.BUT_start_imag_IMAGING.setEnabled(True)
            
            # +0.05 sec is needed for getting data from lock-in
            needed_time_in_min = round(((self.INTEGRATION_TIME_IMAGING + 0.05) * len_x * len_y) / 60, 2) 
            
            # write aprox time for experiment to the statusbar
            self.statusbar.showMessage("Needed time for experiment: ~" + 
                                                str(needed_time_in_min) +
                                                " min")
            
            self.action_monitor_r.setEnabled(True)
        else:
            QMessageBox.warning(self, "Warning", "Initialize piezo first!")
            return -1
        
        
    def on_spec_apply_parameters(self):
        
        self.experiment_type = "Spectra"
        
        # make "save" actions disabled
        self.action_save_r.setEnabled(False)
        self.action_save_theta.setEnabled(False)

        if self.initialized:
            try:    
                # read spectra parameters
                wavenum1 = self.SPIN_nu1_SPECTRA.value()
                wavenum2 = self.SPIN_nu2_SPECTRA.value()
                delta_wavenum = self.SPIN_delta_nu_SPECTRA.value()               
            except Exception:
                QMessageBox.critical(self, "Error", "Error while reading spectra parameters!")
                return -1
            
            try:
               # read lock-in parameters
               
               #! TODO: add function to set lock-in parameters 
               
               filter_slope = self.filter_slope
               time_constant = self.time_constant
               data_transafer_rate = self.data_transafer_rate
               scaling = self.scaling
               enable_external_channel = self.channel
            except Exception:
                QMessageBox.critical(self, "Error", "Error while reading lock-in parameters!")
                return -1         
            
            spec_param_bool = self.is_spec_param_good(wavenum1, 
                                                      wavenum2, 
                                                      delta_wavenum)
            
            lockin_param_bool = self.is_lockin_param_good(filter_slope, 
                                                        time_constant,
                                                        data_transafer_rate, 
                                                        scaling, 
                                                        enable_external_channel)
                            
            # True if everything is fine
            is_proper_values = spec_param_bool and lockin_param_bool  
            
            if is_proper_values != 1:
                QMessageBox.warning(self, "Warning", "Check entered values for consistency!")
                return -1
            
            self.INTEGRATION_TIME_SPECTRA = time_constant * 3.3

            self.PROGBAR_pb1_SPECTRA.setValue(0) # initialize prog bar
            
            
            # try to set lock-in parameters
            self.set_lockin_parameters(filter_slope, 
                                       time_constant, 
                                       data_transafer_rate,
                                       scaling, 
                                       enable_external_channel)
            
            # number of scan wavelengths
            self.len_wavenum = int( ((wavenum2 - wavenum1) / delta_wavenum) ) + 1
    
            # an array of wavelengths
            self.wavenum_pattern = np.linspace(wavenum1, wavenum2, self.len_wavenum)
            
            # go to initial wavelength
            self.ff3.go_to_wavelength(wavenum1)
            self.read_current_wavelength(self.ff3, final_wavenumber=wavenum1)
                  
            # make "start spectra" button active
            self.BUT_apply_param_SPECTRA.setEnabled(True)
            
            needed_time_in_min = round(((self.INTEGRATION_TIME_SPECTRA + 0.05 + 0.5) * self.len_wavenum) / 60, 2) 
            
            # write aprox time for experiment
            self.statusbar.showMessage("Needed time for experiment: ~" + 
                                                str(needed_time_in_min) + 
                                                " min")
        else:
            QMessageBox.warning(self, "Warning", "Initialize piezo first!")
            return -1


    def imag_plot_initialize(self, need_plot_r, need_plot_theta):
        """
        Initialize plot when doing imaging.
        
        """
        self.imag_win = QtWidgets.QMainWindow()
        self.imag_win.resize(800,800)

        if need_plot_r and need_plot_theta:
            
            
            self.plot_layout = QHBoxLayout()
            
            self.imv_r = pg.ImageView()
            self.imv_theta = pg.ImageView()
            self.plot_layout.addWidget(self.imv_r)
            self.plot_layout.addWidget(self.imv_theta)
            
            self.widget = QWidget()
            self.widget.setLayout(self.plot_layout)
            self.imag_win.setCentralWidget(self.widget)
            
            self.imag_win.show()
            self.imag_win.setWindowTitle('Imaging Plot')
            
        elif need_plot_r:
           
            self.imv_r = pg.ImageView()
            self.imag_win.setCentralWidget(self.imv_r)
            
            self.imag_win.show()
            self.imag_win.setWindowTitle('Imaging Plot')
            
        elif need_plot_theta:

            self.imv_theta = pg.ImageView()
            self.imag_win.setCentralWidget(self.imv_theta)
            
            self.imag_win.show()
            self.imag_win.setWindowTitle('Imaging Plot')
            
            
    def imag_plot(self, need_plot_r, need_plot_theta):
        """
        Plotting imaging data in a loop.
        
        """
        if need_plot_r and need_plot_theta:
            
            self.imv_r.setImage(self.r_data)
            self.imv_theta.setImage(self.theta_data)
            
        elif need_plot_r:
            
            self.imv_r.setImage(self.r_data)
            
        elif need_plot_theta:
            
            self.imv_theta.setImage(self.theta_data)

        pg.QtGui.QApplication.processEvents()    
                 
    def on_imag_start(self):
        
        """
        ACTION WHEN CLICKED "START" BUTTON (IMAGING)
        
        """
        
        # make buttons disabled
        self.BUT_go_GO_TO_POSITION.setEnabled(False)
        self.BUT_go_to_origin_GO_TO_POSITION.setEnabled(False)
        
        scan_shape = np.shape(self.x_pattern)
        self.r_data = np.zeros(scan_shape)
        self.theta_data = np.zeros(scan_shape)
        
        length = scan_shape[0] * scan_shape[1]
        
        # set progressbar
        prog_bar_values = np.linspace(1, 100, length)
        prog_bar_values.astype(int) # convert to int       
        
        total_time_min = 0 # for time accumulation
        
        # check if there is something to plot from checkbuttons
        need_plot_r = self.CHBOX_plot_r_IMAGING.isChecked()
        need_plot_theta = self.CHBOX_plot_theta_IMAGING.isChecked()
        need_write_to_console = self.CHBOX_enable_con_log_SPECTRA.isChecked()
        
        # initialize plotting
        self.imag_plot_initialize(need_plot_r, need_plot_theta)
            
        # move the piezo over the scan area
        for step, index in enumerate(np.ndindex(scan_shape)):
            try:
                
                t1 = time() # start time
                
                self.read_position() # read current position
                # QCoreApplication.processEvents()  
                if self.break_loop:
                    break
                
                # invert index to fill array from the bottom to the top
                index_im = scan_shape[0] - 1 - index[0], index[1] 
                    
                # change value in progress bar 
                self.PROGBAR_pb1_IMAGING.setVa(prog_bar_values[step])

                # go to the next position and read position
                self.piezo.goxy(self.x_pattern[index], self.y_pattern[index])
                
                # use integration pause for plotting
                t1_integration = time()
                
                # plot one value
                self.imag_plot(need_plot_r, need_plot_theta)

                t2_integration = time()
                
                delta_t = t2_integration - t1_integration
                
                if delta_t < self.INTEGRATION_TIME_IMAGING:
                    sleep(self.INTEGRATION_TIME_IMAGING - delta_t)
                
                # record one demodulator sample from the specified node,
                # data here consist of everything lock-in have
               
                sample = self.daq.getSample('/' + self.device + '/demods/0/sample')
                
                sample_x = float(sample['x'])
                sample_y = float(sample['y'])
                x_coord = self.x_pattern[index]
                y_coord = self.y_pattern[index]
                
                # extract R value from sample data
                r_value = np.hypot(sample_x, sample_y) # sqrt(x^2 + y^2)
                self.r_data[index_im] = r_value
                
                # extract Theta values from sample data
                theta_rad = np.arctan(sample_y / sample_x) 
                theta_deg = np.rad2deg(theta_rad)
                self.theta_data[index_im] = theta_deg
                    
                t2 = time() # finish time
                time_ms = round((t2 - t1) * 1000, 2) # time in milliseconds
                
                total_time_min += time_ms / (1000 * 60) # time in minutes

                if need_write_to_console:
                    if step == 0:
                        print(f"{'STEP' : <7}{'X, μm' : ^10}{'Y, μm' : ^10}{'R' : ^15}{'THETA, deg' : ^15}{'DURATION, MS' : >20}")
                        print(f"{'='*77}")
                    else:  
                        print(f"{step : <7}{x_coord : ^10}{y_coord : ^10}{r_value : ^15,.4f}{theta_deg : ^15,.4f}{time_ms : >20}")      
            
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
                return -1

        pg.exec() # to keep plot window opened

        if self.break_loop == False: 
            
            self.imag_plot(need_plot_r, need_plot_theta)
                
            st = f"\n\nDone! For {length} steps it took {round(total_time_min, 2)} min.\
On average {round(total_time_min * 1000 * 60 / length, 2)} ms per step."
            
            self.action_save_r.setEnabled(True)
            self.statusbar.showMessage(st)


    def on_spec_start(self):
        
        # make buttons disabled
        self.BUT_go_GO_TO_POSITION.setEnabled(False)
        self.BUT_go_to_origin_GO_TO_POSITION.setEnabled(False)
                
        scan_shape = self.len_wavenum
        r_data = np.zeros(scan_shape)

        # initialize prog bar
        prog_bar_values = np.linspace(1, 100, scan_shape)
        prog_bar_values.astype(int) # convert to int

        # read current coords from "Current position" labelframe
        x_coord = round(float( self.LAB_x_val_CURRENT_VALUES.text() ), 2)
        y_coord = round(float( self.LAB_y_val_CURRENT_VALUES.text() ), 2)
        
        ## PLOT PRE-TREATMENT
        need_plot_r = self.CHBOX_plot_r_SPECTRA.isChecked()
            
        # plot R  
        if need_plot_r:
            
            self.spec_win = QtWidgets.QMainWindow()
            self.spec_win.resize(800, 800)

            self.graphWidget = pg.PlotWidget()
            self.spec_win.setCentralWidget(self.graphWidget)

            # some styling
            pen = pg.mkPen(color=(255, 0, 0), width=1)
            self.graphWidget.setBackground('w')
            self.graphWidget.showGrid(x=True, y=True)
            self.graphWidget.setTitle("<span style=\"font-size:20px\">IR absorption Chart</span>")
            self.graphWidget.setLabel("left", "<span style=\"font-size:20px\">IR absorption</span>")
            self.graphWidget.setLabel('bottom', "<span style=\"font-size:20px\">ν, cm⁻¹</span>")

            plot_r = self.graphWidget.plot(self.wavenum_pattern, r_data, pen=pen)

            self.spec_win.show()

            pg.exec()
            
        
        total_time_min = 0 # for time accumulation 
        
        need_write_to_console = self.log_to_console_var_fr_sp.get()
        
        # move the piezo over the scan area
        for step, index in enumerate(np.ndindex(scan_shape)):
            try:
                t1 = time() # start time
                

                self.read_current_wavelength(self.ff3)
            
                # change value in progress bar 
                self.PROGBAR_pb1_SPECTRA.setValue(prog_bar_values[step])

                # emergency abort
                if self.break_loop:
                    break
                
                # go to wavelength
                self.ff3.go_to_wavelength(self.wavenum_pattern[index])
                
                # plot R    
                if need_plot_r:
                    
                    plot_r.setData(r_data)
                    pg.QtGui.QApplication.processEvents() 

                
                # maybe not needed
                # sleep(self.INTEGRATION_TIME_SPECTRA) # some pause
                
                # record one demodulator sample from the specified node,
                # data here consist of everything lock-in have
                sample = self.daq.getSample('/' + self.device + '/demods/0/sample')
                
                sample_x = float(sample['x'])
                sample_y = float(sample['y'])
                wavenum_val = self.wavenum_pattern[index]
                
                # extract R value from sample data
                r_value = np.hypot(sample_x, sample_y) # sqrt(x^2 + y^2)
                r_data[index] = r_value                
            
                t2 = time() # finish time
                time_ms = round((t2 - t1) * 1000, 2) # time in milliseconds
                
                total_time_min += time_ms / (1000 * 60) # time in minutes
                
                if need_write_to_console:
                    if step == 0:
                        print(f"{'STEP' : <7}{'X, μm' : ^10}{'Y, μm' : ^10}{'ν, cm⁻¹' : ^10}{'R' : ^15}{'DURATION, ms' : >20}")
                        print(f"{'='*72}")
                    else:  
                        print(f"{step : <7}{x_coord : ^10}{y_coord : ^10}{wavenum_val : ^10}{r_value : ^15,.4f}{time_ms : >20}")   
            
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
                return -1
        
        # show static images when loop is over   
        if self.break_loop == False:
            if need_plot_r:

                plot_r.setData(r_data)
                pg.QtGui.QApplication.processEvents()
        
            st = f"Done! For {scan_shape} steps it took {round(total_time_min, 2)} min.\
On average {round(total_time_min * 1000 * 60 / scan_shape, 2)} ms per step."

            self.statusbar.showMessage(st)
            
            # to reset laser wavelength
            initial_wavenum = self.wavenum_pattern[0]
            self.ff3.go_to_wavelength(initial_wavenum)
            self.read_current_wavelength(self.ff3, final_wavenumber=initial_wavenum)
            
            # add R norm
            r_data_norm = r_data / np.max(r_data)
            
            # data to save to file
            self.data_save = np.transpose([self.wavenum_pattern, r_data, r_data_norm])
            
            # make "save" button active
            self.action_save_r.setEnabled(True)
            
            # disable "theta" checkbutton when save
            self.action_save_theta.setEnabled(False)

            pg.exec() # to keep plot window opened

            


    def is_spec_param_good(self, wavenum1, wavenum2, delta_wavenum):
        """
        CHECKS WHETHER SPEC PARAMETERS ARE GOOD

        """
        wavenum1_bool = self.WAVENUM_LEFT_BORDER <= wavenum1 <= self.WAVENUM_RIGHT_BORDER
        wavenum2_bool = wavenum1 < wavenum2 <= self.WAVENUM_RIGHT_BORDER
        delta_wavenum_bool = 0 < (wavenum2 - wavenum1)
        
        total_bool = (wavenum1_bool * wavenum2_bool * delta_wavenum_bool)
        return total_bool