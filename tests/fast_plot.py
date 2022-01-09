
import matplotlib.pyplot as plt
import numpy as np
import time
from random import randint
import tkinter as tk
import random
import matplotlib.animation as animation



fig, ax = plt.subplots()

x = np.random.randint(0, 100, 100)
y = np.random.randint(0, 100, 100)

ax.set_title("IR absorption Chart")
ax.set_xlabel("ν, cm⁻¹")
ax.set_ylabel("IR absorption")
ax.grid(visible=True)

(plot_r, ) = ax.plot(x, y, animated=True)

plt.show(block=False)

plt.pause(0.05)

# bg = fig.canvas.copy_from_bbox(fig.bbox)

ax.draw_artist(plot_r)
fig.canvas.blit(fig.bbox)

start = time.time()

for _ in range(1000):
    
    x = np.random.randint(0, 100, 100)
    y = np.random.randint(0, 100, 100)
    
                    
    # fig.canvas.restore_region(bg)
    
    plot_r.set_ydata(y)  
    
    ax.draw_artist(plot_r)
    
    fig.canvas.blit(fig.bbox)
    fig.canvas.flush_events()
    # time.sleep(0.5)

final = time.time()

print(final - start)
