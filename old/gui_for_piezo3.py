import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from madpiezo import Madpiezo
import numpy as np
import atexit
from ctypes import cdll, c_int, c_uint, c_double

#=====================================================================
def on_closing():
    global piezo
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        try:
            piezo.goxy(0.0,0.0)
            piezo.goz(0.0)
            root.after(2000) # sleep for gui
            piezo.mcl_close()
            root.destroy()
        except:
            root.destroy()


## READ AND WRITE CURRENT POSITION TO WIDGET
def read_position():
    global piezo
    coords = piezo.get_position()
    x_coord_lab_lf2['text'] = coords[0]
    y_coord_lab_lf2['text'] = coords[1]
    z_coord_lab_lf2['text'] = coords[2]

## ACTION WHEN CLICKED "GO" BUTTON
def on_go():
    global piezo
    flag = 1
    try:
        # read data from spinboxes
        x = round(float(x_spin_lf1.get()), 1)
        y = round(float(y_spin_lf1.get()), 1)
        z = round(float(z_spin_lf1.get()), 1)

    except:
        flag = 0
        error_lab_lf1["text"] = "Bad values! Enter numbers."
    # check if values are in a proper range
    if flag and (0 <= x <= 300) and (0 <= y <= 300) and (0 <= z <= 300):
        piezo.goxy(x, y)
        piezo.goz(z)
        root.after(2000) # sleep for gui
        read_position()
        error_lab_lf1["text"] = ""
    else:
        error_lab_lf1["text"] = "Values must be in a proper range! Try again."
        
## ACTION WHEN CLICKED "Initialize Piezo" BUTTON
def on_initialize():
    if initialize_button['text'] == "Initialize Piezo":
        global piezo
        try:
            piezo = Madpiezo()
            if piezo.handler != 0:
                initialize_button.config(text = "Stop Piezo", bg = "red")
                go_button_lf1.configure(state = "enabled")
                go_to_origin_button.configure(state = "enabled")
                read_position()
            else:
                initialize_button.config(text = "Error initializing!", bg = "yellow", fg = "black")
        except:
            initialize_button.config(text = "Error initializing!", bg = "yellow", fg = "black")

    elif initialize_button['text'] == "Stop Piezo":
        piezo.goxy(0.0,0.0)
        piezo.goz(0.0)
        root.after(2000) # sleep for gui
        read_position()        
        piezo.mcl_close()
        initialize_button.config(text = "Initialize Piezo", bg = "green")
        go_button_lf1.configure(state = "disabled")
        go_to_origin_button.configure(state = "disabled")
        
## ACTION WHEN CLICKED "Go to Origin" BUTTON        
def on_go_to_origin():
    global piezo
    piezo.goxy(0.0,0.0)
    piezo.goz(0.0)
    root.after(2000) # sleep for gui
    read_position() 
#=====================================================================

root = tk.Tk()
root.title("Piezo manipulation")
root.resizable(0, 0)

frame1 = ttk.Frame(root, padding=10)
frame1.grid(column=0, row=0, sticky='W')

# label frame 1
lf1 = ttk.LabelFrame(frame1, text='Go to position')
lf1.grid(column=0, row=0, padx=5, pady=5)


x_lab_lf1 = ttk.Label(lf1, text="X, μm (0-300): ")
x_lab_lf1.grid(column=0, row=0)

y_lab_lf1 = ttk.Label(lf1, text="Y, μm (0-300): ")
y_lab_lf1.grid(column=0, row=1)

z_lab_lf1 = ttk.Label(lf1, text="Z, μm (0-300): ")
z_lab_lf1.grid(column=0, row=2)

x_spin_lf1 = ttk.Spinbox(lf1, from_=0, to=300)
x_spin_lf1.grid(column=1, row=0)

y_spin_lf1 = ttk.Spinbox(lf1, from_=0, to=300)
y_spin_lf1.grid(column=1, row=1)

z_spin_lf1 = ttk.Spinbox(lf1, from_=0, to=300)
z_spin_lf1.grid(column=1, row=2)

go_button_lf1 = ttk.Button(lf1, text = "Go", command = on_go)
go_button_lf1.grid(column=0, row=3)
go_button_lf1.configure(state = "disabled")

error_lab_lf1 = ttk.Label(lf1, text="")
error_lab_lf1.grid(column=1, row=3)

# Label frame 2
lf2 = ttk.LabelFrame(frame1, text='Current position')
lf2.grid(column=0, row=1, padx=5, pady=5, sticky='W')

x_lab_lf2 = ttk.Label(lf2, text="X, μm: ")
x_lab_lf2.grid(column=0, row=0)

y_lab_lf2 = ttk.Label(lf2, text="Y, μm: ")
y_lab_lf2.grid(column=0, row=1)

z_lab_lf2 = ttk.Label(lf2, text="Z, μm: ")
z_lab_lf2.grid(column=0, row=2)

x_coord_lab_lf2 = ttk.Label(lf2, text="")
x_coord_lab_lf2.grid(column=1, row=0)

y_coord_lab_lf2 = ttk.Label(lf2, text="")
y_coord_lab_lf2.grid(column=1, row=1)

z_coord_lab_lf2 = ttk.Label(lf2, text="")
z_coord_lab_lf2.grid(column=1, row=2)

go_to_origin_button = ttk.Button(frame1, text="Go to Origin", command = on_go_to_origin)
go_to_origin_button.grid(column=0, row=3, padx=5, pady=5, sticky='W')
go_to_origin_button.configure(state = "disabled")

initialize_button = tk.Button(frame1, text = "Initialize Piezo", bg="green", fg = "white", command = on_initialize)
initialize_button.grid(column=0, row=3, padx=5, pady=5, sticky='E')

# # tree view for logging
# frame2 = ttk.Frame(root, padding=10)
# frame2.grid(column=1, row=0, sticky='W')
# tree = ttk.Treeview(frame2, columns=("step", "time", "log"), show="headings")
# tree.grid(column=0, row=0)

# tree.heading('step', text='step')
# tree.heading('time', text='time')
# tree.heading('log', text='log')


root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
