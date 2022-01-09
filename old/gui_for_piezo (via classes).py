import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from madpiezo import Madpiezo
import numpy as np
import atexit
from ctypes import cdll, c_int, c_uint, c_double


#=====================================================================

class PiezoManipulation(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.grid(column=0, row=0, sticky='W')

        # label frame 1
        self.lf1 = ttk.LabelFrame(self, text='Go to position')
        self.lf1.grid(column=0, row=0, padx=5, pady=5)

        self.x_lab_lf1 = ttk.Label(self.lf1, text="X, μm (0-300): ")
        self.x_lab_lf1.grid(column=0, row=0)

        self.y_lab_lf1 = ttk.Label(self.lf1, text="Y, μm (0-300): ")
        self.y_lab_lf1.grid(column=0, row=1)

        self.z_lab_lf1 = ttk.Label(self.lf1, text="Z, μm (0-300): ")
        self.z_lab_lf1.grid(column=0, row=2)

        self.x_spin_lf1 = ttk.Spinbox(self.lf1, from_=0, to=300)
        self.x_spin_lf1.grid(column=1, row=0)

        self.y_spin_lf1 = ttk.Spinbox(self.lf1, from_=0, to=300)
        self.y_spin_lf1.grid(column=1, row=1)

        self.z_spin_lf1 = ttk.Spinbox(self.lf1, from_=0, to=300)
        self.z_spin_lf1.grid(column=1, row=2)

        self.go_button_lf1 = ttk.Button(self.lf1, text = "Go", command = self.on_go)
        self.go_button_lf1.grid(column=0, row=3)
        self.go_button_lf1.configure(state = "disabled")

        self.error_lab_lf1 = ttk.Label(self.lf1, text="")
        self.error_lab_lf1.grid(column=1, row=3)

        # label frame 2
        self.lf2 = ttk.LabelFrame(self, text='Current position')
        self.lf2.grid(column=0, row=1, padx=5, pady=5, sticky='W')

        self.x_lab_lf2 = ttk.Label(self.lf2, text="X, μm: ")
        self.x_lab_lf2.grid(column=0, row=0)

        self.y_lab_lf2 = ttk.Label(self.lf2, text="Y, μm: ")
        self.y_lab_lf2.grid(column=0, row=1)

        self.z_lab_lf2 = ttk.Label(self.lf2, text="Z, μm: ")
        self.z_lab_lf2.grid(column=0, row=2)

        self.x_coord_lab_lf2 = ttk.Label(self.lf2, text="")
        self.x_coord_lab_lf2.grid(column=1, row=0)

        self.y_coord_lab_lf2 = ttk.Label(self.lf2, text="")
        self.y_coord_lab_lf2.grid(column=1, row=1)

        self.z_coord_lab_lf2 = ttk.Label(self.lf2, text="")
        self.z_coord_lab_lf2.grid(column=1, row=2)

        self.go_to_origin_button = ttk.Button(self, text="Go to Origin", command = self.on_go_to_origin)
        self.go_to_origin_button.grid(column=0, row=3, padx=5, pady=5, sticky='W')
        self.go_to_origin_button.configure(state = "disabled")

        self.initialize_button = tk.Button(self, text = "Initialize Piezo", bg="green", fg = "white", command = self.on_initialize)
        self.initialize_button.grid(column=0, row=3, padx=5, pady=5, sticky='E')



    ## READ AND WRITE CURRENT POSITION TO WIDGET
    def read_position(self):
        global piezo
        coords = piezo.get_position()
        self.x_coord_lab_lf2['text'] = coords[0]
        self.y_coord_lab_lf2['text'] = coords[1]
        self.z_coord_lab_lf2['text'] = coords[2]



    ## ACTION WHEN CLICKED "Initialize Piezo" BUTTON
    def on_initialize(self):
        if self.initialize_button['text'] == "Initialize Piezo":
            try:
                global piezo
                piezo = Madpiezo()
                if piezo.handler != 0:
                    self.initialize_button.config(text = "Stop Piezo", bg = "red")
                    self.go_button_lf1.configure(state = "enabled")
                    self.go_to_origin_button.configure(state = "enabled")
                    self.read_position()
                else:
                    self.initialize_button.config(text = "Error initializing!", bg = "yellow", fg = "black")
            except:
                self.initialize_button.config(text = "Error initializing!", bg = "yellow", fg = "black")

        elif self.initialize_button['text'] == "Stop Piezo":
            piezo.goxy(0.0,0.0)
            piezo.goz(0.0)
            global root
            root.after(2000) # sleep for gui
            self.read_position()        
            piezo.mcl_close()
            self.initialize_button.config(text = "Initialize Piezo", bg = "green")
            self.go_button_lf1.configure(state = "disabled")
            self.go_to_origin_button.configure(state = "disabled")

    ## ACTION WHEN CLICKED "GO" BUTTON
    def on_go(self):
        flag = 1
        global piezo
        try:    
            # read data from spinboxes
            x = round(float(self.x_spin_lf1.get()), 1)
            y = round(float(self.y_spin_lf1.get()), 1)
            z = round(float(self.z_spin_lf1.get()), 1)

        except:
            flag = 0
            self.error_lab_lf1["text"] = "Bad values! Enter numbers."
        # check if values are in a proper range    
        if flag and (0 <= x <= 300) and (0 <= y <= 300) and (0 <= z <= 300):
            piezo.goxy(x, y)
            piezo.goz(z)
            global root
            root.after(2000) # sleep for gui
            self.read_position()
            self.error_lab_lf1["text"] = ""
        else:
            self.error_lab_lf1["text"] = "Values must be in a proper range! Try again."


    ## ACTION WHEN CLICKED "Go to Origin" BUTTON        
    def on_go_to_origin():
        global piezo
        piezo.goxy(0.0,0.0)
        piezo.goz(0.0)
        global root
        root.after(2000) # sleep for gui
        self.read_position()
        
    # # tree view for logging
    # frame2 = ttk.Frame(root, padding=10)
    # frame2.grid(column=1, row=0, sticky='W')
    # tree = ttk.Treeview(frame2, columns=("step", "time", "log"), show="headings")
    # tree.grid(column=0, row=0)
    
    # tree.heading('step', text='step')
    # tree.heading('time', text='time')
    # tree.heading('log', text='log')

   
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



root = tk.Tk()
root.title("Piezo manipulation")
root.resizable(0, 0)
root.protocol("WM_DELETE_WINDOW", on_closing)

notebook = ttk.Notebook(root)
notebook.grid()

piezo = PiezoManipulation(notebook)
notebook.add(piezo, text = "Piezo")

root.mainloop()
