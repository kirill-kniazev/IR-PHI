
import matplotlib.pyplot as plt
import numpy as np
import time
from random import randint
import tkinter as tk
import random
import matplotlib.animation as animation



figure1, ax1 = plt.subplots()
ax1.set_axis_off()
z = np.random.randint(0, 100, size = (500, 500)) 
line1 = ax1.pcolormesh(z, cmap="jet", shading='auto')
ax1.set_aspect('equal')
start = time.time()    
figure1.colorbar(line1)
   
def animate(i):
    z = np.random.randint(0, 100, size = (500, 500)) 
    line1.set_array(z)
    
    if i == 999:
        print(time.time() - start)
    
    return line1,


anim = animation.FuncAnimation(figure1, animate, 
                               frames=1000, interval=0, blit=True, repeat=False)

