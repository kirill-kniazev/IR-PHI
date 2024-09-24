import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.axes_grid1 import make_axes_locatable

fig, ax = plt.subplots()
ax.set_axis_off()

z = np.random.randint(0, 100, size = (500, 500))
line = ax.imshow(z, cmap="jet", extent=[0,100,0,100], interpolation="none")

div = make_axes_locatable(ax)
cax = div.append_axes('right', '5%', '5%')
cbar = fig.colorbar(line, cax=cax)

def animate(i):

    if i % 2 == 0:
        z = np.random.randint(0, 500, size = (500, 500))
        line.set_clim(0, 500)
    
        
        cax.cla()
        cbar = fig.colorbar(line, cax=cax)

    else:
        z = np.random.randint(0, 200, size = (500, 500))
        line.set_clim(0, 200)
        cax.cla()
        cbar = fig.colorbar(line, cax=cax)

    line.set_data(z)
    return line,

ani = animation.FuncAnimation(fig, animate, frames=20, interval=200, blit=True, repeat=False)

plt.show()