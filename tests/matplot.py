from math import pi
import matplotlib.pyplot as plt
import numpy as np
import time
from random import randint
import tkinter as tk
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import random
from matplotlib.widgets import Button
import matplotlib

plt.ion()


ar1 = np.random.randint(0, 100, size = (500, 500))
#ar2 = np.random.randint(0, 100, size = (40, 40))

#figure2, ax2 = plt.subplots()
figure1, ax1 = plt.subplots()

line1 = ax1.imshow(ar1, cmap="jet", extent=[0,100,0,100])
#line2 = ax2.imshow(ar1, cmap="jet", extent=[0,40,0,40])
ax1.set_axis_off()
#ax2.set_axis_off()
ax1.set_title("R")
#ax2.set_title("Theta")

figure1.colorbar(line1)
#figure2.colorbar(line2)

#++++++++++++++++++++ MATPLOTLIB WIDGETS ++++++++++++++++++++++++++
#def change_interpolation(event):
    #interpolation = line1.get_interpolation()
    #if interpolation == "antialiased":
        #line1.set_interpolation("spline36")
        #line2.set_interpolation("spline36")
    #if interpolation == "spline36":
        #line1.set_interpolation("antialiased")
        #line2.set_interpolation("antialiased")
        
    #figure1.canvas.draw()
    #figure1.canvas.flush_events()
    
    #figure2.canvas.draw()
    #figure2.canvas.flush_events()
    
#def change_cmap(event):
    #cmaps = ["inferno", "plasma", "magma", "jet"]
    #cur_cmap = random.choice(cmaps)
    #line1.set_cmap(cur_cmap)
    #line2.set_cmap(cur_cmap)
    
    #figure1.canvas.draw()
    #figure1.canvas.flush_events()
    
    #figure2.canvas.draw()
    #figure2.canvas.flush_events()
    

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++





start = time.time()
for _ in range(100):
    ar1 = np.random.randint(0, 100, size = (500, 500))
    #ar2 = np.random.randint(0, 100, size = (40, 40))
    line1.set_data(ar1)
    # line1.autoscale()
    #line2.set_data(ar2)
    # line2.autoscale()

    figure1.canvas.draw()
    figure1.canvas.flush_events()
    #figure2.canvas.draw()
    #figure2.canvas.flush_events()
    #time.sleep(0.1)

print(time.time() - start)
plt.ioff()
plt.show()