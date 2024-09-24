# link to mclpiezo: https://github.com/yurmor/mclpiezo/blob/master/mcl_piezo_lib.py

from ctypes import cdll, c_int, c_uint, c_double
import atexit
from time import sleep
import numpy as np

class madpiezo():
	def __init__(self):
		# provide valid path to Madlib.dll. Madlib.h and Madlib.lib should also be in the same folder
        path_to_dll = 'C:\\Program Files\\Mad City Labs\\NanoDrive\\Madlib.dll'
        
		self.madlib = cdll.LoadLibrary(path_to_dll)
		self.handler = self.mcl_start()
		atexit.register(self.mcl_close)

	def mcl_start(self):
		"""
		Requests control of a single Mad City Labs Nano-Drive.

		Return Value:
			Returns a valid handle or returns 0 to indicate failure.
		"""
		mcl_init_handle = self.madlib['MCL_InitHandle']
		mcl_init_handle.restype = c_int
		handler = mcl_init_handle()
		if (handler == 0):
			print("MCL init error")
			return -1
		if (handler == 1):
			print ("Nano-Drive connected\n")
		return 	handler
		
	def mcl_read(self,axis_number):
		"""
		Read the current position of the specified axis.
	
		Parameters:
			axis [IN] Which axis to move. (X = 1, Y = 2, Z = 3, AUX = 4)
			handle [IN] Specifies which Nano-Drive to communicate with.
		Return Value:
			Returns a position value or the appropriate error code.
		"""
		mcl_single_read_n = self.madlib['MCL_SingleReadN']
		mcl_single_read_n.restype = c_double
		return  mcl_single_read_n(c_uint(axis_number), c_int(self.handler))
		
	def mcl_write(self,position, axis_number):
		"""
		Commands the Nano-Drive to move the specified axis to a position.
	
		Parameters:
			position [IN] Commanded position in microns.
			axis [IN] Which axis to move. (X = 1, Y = 2, Z = 3, AUX = 4)
			handle [IN] Specifies which Nano-Drive to communicate with.
		Return Value:
			Returns MCL_SUCCESS or the appropriate error code.
		"""
		mcl_single_write_n = self.madlib['MCL_SingleWriteN']
		mcl_single_write_n.restype = c_int
		error_code = mcl_single_write_n(c_double(position), c_uint(axis_number), c_int(self.handler))
		if(error_code !=0):
			print("MCL write error = ", error_code)
		return error_code
		
	def gox(self, x_position):
		self.mcl_write(x_position, 1)

	def goy(self, y_position):
		self.mcl_write(y_position, 2)

	def goxy(self,x_position,y_position):
		self.mcl_write(x_position,1)
		self.mcl_write(y_position,2)
		
	def goz(self,z_position):
		self.mcl_write(z_position,3)
		
	def get_position(self):
		x = self.mcl_read(1)
		y = self.mcl_read(2)
		z = self.mcl_read(3)
		print ("X =", x, "um; Y =", y, "um; Z =", z,"um\n")
		
	def mcl_close(self):
		"""
		Releases control of all Nano-Drives controlled by this instance of the DLL.
		"""
		mcl_release_all = self.madlib['MCL_ReleaseAllHandles']
		mcl_release_all()
		print ("Nano-Drive disconnected\n")

if __name__ == "__main__":
    piezo = madpiezo() # intialize the piezo
    # piezo.mcl_start() # not needed as it runs when intialize takes place

	#will scan over a rectangular area, from (x1, y1) to (x2, y2) 
	#with len_x steps in x-direction and len_y steps in y-direction
	
	delta_x = 64  # number of steps in x-direction
	delta_y = 64  # number of steps in y-direction 
	x1, x2 = 0.,16. # x coordinates
	y1, y2 = 0., 16. # y coordinates
	z_postion = 50. # z position 


	# go to the origin of the scan
    piezo.goxy(0.00, 0.00)
    piezo.goz(0.00)
    sleep(2)
    print (piezo.get_position())


    piezo.goxy(50.00, 50.00)
    piezo.goz(50.00)
    sleep(2)
    print (piezo.get_position())

    # len_x = 1  # edit here
    # len_y = 1  # edit here
    # x1, x2 = 0.0,1.0 # edit here
    # y1, y2 = 0.0, 1.0 # edit here
    # x_pattern, y_pattern = np.meshgrid(np.linspace(x1, x2, len_x), np.linspace(y1, y2, len_y))
    # scan_shape = np.shape(x_pattern)

    while True:
        cmd_axis = input("Define axis (X, Y or Z) or type 'Q' to quit: ")
        if cmd_axis == 'Q' or cmd_axis == 'q':
            piezo.goxy(0.0,0.0)
            piezo.goz(0.0)
            sleep(2)
            print (piezo.get_position())
            piezo.mcl_close()
            exit()
        else:
            if cmd_axis == 'x' or cmd_axis == 'X':
                while True:
                    cmd_x = input("enter X position in microns: ")
                    if float(cmd_x) < 0.00 or float(cmd_x) > 300.00 :
                        print ("Value out of range. Enter value between 0.00 and 300.00 um.\n")
                        break

                    else:
                        piezo.gox(float(cmd_x))
                        sleep(2)
                        print (piezo.get_position())
                        break

            if cmd_axis == 'y' or cmd_axis == 'Y':
                while True:
                    cmd_y = input("enter Y position in microns: ")
                    if float(cmd_y) < 0.00 or float(cmd_y) > 300.00 :
                        print ("Value out of range. Enter value between 0.00 and 300.00 um.\n")
                        break

                    else:
                        piezo.goy(float(cmd_y))
                        sleep(2)
                        print (piezo.get_position())
                        break

            if cmd_axis == 'z' or cmd_axis == 'Z':
                while True:
                    cmd_z = input("enter Z position in microns: ")
                    if float(cmd_z) < 0.00 or float(cmd_z) > 300.00 :
                        print ("Value out of range. Enter value between 0.00 and 300.00 um.\n")
                        break

                    else:
                        piezo.goz(float(cmd_z))
                        sleep(2)
                        print (piezo.get_position())
                        break
