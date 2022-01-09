import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import numpy as np
from matplotlib.widgets import Slider, Button
from time import sleep
from matplotlib.figure import Figure

def change():
    st = line.get_interpolation()
    if st == "antialiased":
        line.set_cmap('jet')
        line.set_interpolation("spline36")
        # line1.set_clim(30, 50)
        toolbar1.update()
    else:
        line.set_interpolation("antialiased")
    canvas.draw()

window = tk.Tk()
bar = ttk.Progressbar(window,
                      orient="horizontal",
                        length=100,
                        mode="determinate")
bar.grid(column=0, row=4)
prog_bar_values = np.linspace(1, 100, 50)
prog_bar_values.astype(int) # convert to int  



fig = Figure(figsize=(5, 4), dpi=100)
ax = fig.add_subplot()
ar = np.random.randint(0, 100, size = (40, 40))
line = ax.imshow(ar, cmap="jet", extent=[0,40,0,40])

canvas = FigureCanvasTkAgg(fig, master=window)
canvas.get_tk_widget().grid(row=0, column=0, ipadx=40, ipady=20)


fig.colorbar(line)

# navigation toolbar
toolbarFrame1 = tk.Frame(master=window)
toolbarFrame1.grid(row=1,column=0)
# canvas.draw()

toolbar1 = NavigationToolbar2Tk(canvas, toolbarFrame1)
but = tk.Button(window, text="Change background", command=change)
but.grid(column=0, row=3)
canvas.draw()

step = 0
for _ in range(50):
    bar["value"] = prog_bar_values[step]
    window.update() # try to update prog bar
    
    ar1 = np.random.randint(0, 100, size = (40, 40))
    line.set_data(ar1)
    canvas.draw()
    canvas.flush_events()
    sleep(0.01)
    
    step += 1

window.mainloop()

