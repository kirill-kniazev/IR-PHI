
import matplotlib.pyplot as plt
import numpy as np
import time
# from random import randint
# import tkinter as tk
# import random
# import matplotlib.animation as animation
from mpl_toolkits.axes_grid1 import make_axes_locatable



fig, ax = plt.subplots()

ax.set_axis_off()
z = np.random.randint(0, 100, size = (500, 500))
line = ax.imshow(z, cmap="jet", extent=[0,100,0,100], interpolation="none", animated=True)

div = make_axes_locatable(ax)
cax = div.append_axes('right', '5%', '5%')
cbar = fig.colorbar(line, cax=cax)


plt.show(block=False)
plt.pause(0.05)

bg = fig.canvas.copy_from_bbox(fig.bbox)
ax.draw_artist(line)

fig.canvas.blit(fig.bbox)

start = time.time()

for i in range(10):
    
    if i % 2 == 0:
        z = np.random.randint(0, 500, size = (500, 500))
        line.set_clim(0, 500)

        
        # cax.cla()
        # cbar = fig.colorbar(line, cax=cax)
        # cbar.set_ticks([1,1000])
        # cbar.update_normal(line)
        # cbar.update_ticks()

    else:
        z = np.random.randint(0, 200, size = (500, 500))
        line.set_clim(0, 200)
        # cax.cla()
        # cbar = fig.colorbar(line, cax=cax)
        # cbar.update_normal(line)
        # cbar.update_ticks()

    # fig.canvas.restore_region(bg)
    line.set_data(z)
    # ax.redraw_in_frame()
    # fig.canvas.draw()
    ax.draw_artist(line)
    fig.canvas.blit(fig.bbox)
    # fig.canvas.flush_events()

    # cbar.draw_all()
    
    time.sleep(0.2)

final = time.time()

print(final - start)
# print(dir(cbar))
# print(help(cbar))