import os, sys, inspect, path

# add parent dir to Python search path
_directory = path.Path(__file__).abspath()
_parent_dir = _directory.parent.parent
sys.path.append(_parent_dir)

from datetime import datetime

# tkinter
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo, showwarning, showerror
from idlelib.tooltip import Hovertip # for tips

from madpiezo import Madpiezo
import numpy as np
from time import sleep, time
import re
import Firefly_SW #192.168.1.229
import Firefly_LW #192.168.1.231
import zhinst.ziPython, zhinst.utils
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

class PiezoManipulation(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        
        #* CONSTANTS
        self.SLEEP_TIME = 1 # in sec
        
        self.XYZ_LEFT_BORDER = 0 # position, μm
        self.XYZ_RIGHT_BORDER = 300 # position, μm
        
        self.WAVENUM_LEFT_BORDER = 1041 # wavenumber, cm⁻¹
        self.WAVENUM_RIGHT_BORDER = 1843 # wavenumber, cm⁻¹
        
        #* FORM VARIABLES (VALUES BY DEFAULT)
        self.filter_slope_var = tk.IntVar(value=8) 
        self.time_constant_var = tk.DoubleVar(value=0.03)
        self.data_transafer_rate_var = tk.IntVar(value=1000)
        self.scaling_var = tk.IntVar(value=1)
        self.channel_var = tk.IntVar(value=1)
        self.fast_mode_var = tk.IntVar(value=0)
        
        self.log_to_console_var_fr_im = tk.IntVar(value=0) # for imaging
        self.log_to_console_var_fr_sp = tk.IntVar(value=0) # for spectra
        self.plot_theta_var_fr_im = tk.IntVar(value=0) # for imaging only
        self.plot_r_var_fr_im = tk.IntVar(value=1) # for imaging
        self.plot_r_var_fr_sp = tk.IntVar(value=1) # for spectra
        
        self.save_r_lf5_var = tk.IntVar(value=1) # save file for R
        self.save_theta_lf5_var = tk.IntVar(value=0) # save file for Theta
        
        self.file_name = tk.StringVar()
        
        #* VARIABLES
        self.initialized = False # check initialize status

        #* FRAME
        self.grid(sticky="NSEW")
        
        # for streching elements when resize
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        #* IMAGES
        self.logo = tk.PhotoImage(file=_parent_dir + "\images\path22064.png")
        
        #!+++++++++++++++++++++++ GUI DESCRIPTION +++++++++++++++++++++++++++++
                
        #*+++++++++++++++++++ LABELFRAME GO TO POSITION +++++++++++++++++++++++
        
        self.lf1 = ttk.LabelFrame(self, text = "Go to position")
        self.lf1.grid(column=0,
                      row=0,
                      padx=5,
                      pady=5,
                      sticky="NW")
        
        ## LABEL X
        self.x_lab_lf1 = ttk.Label(self.lf1,
                                   text="X, μm (" +
                                   str(self.XYZ_LEFT_BORDER) +
                                   "-" +
                                   str(self.XYZ_RIGHT_BORDER) +
                                   "): ")
        self.x_lab_lf1.grid(column=0, 
                            row=0,
                            padx=5,
                            sticky="E")
        
        ## LABEL Y
        self.y_lab_lf1 = ttk.Label(self.lf1,
                                    text="Y, μm (" +
                                    str(self.XYZ_LEFT_BORDER) +
                                    "-" +
                                    str(self.XYZ_RIGHT_BORDER) +
                                    "): ")
        self.y_lab_lf1.grid(column=0, 
                            row=1,
                            padx=5,
                            sticky="E")
        
        ## LABEL Z
        self.z_lab_lf1 = ttk.Label(self.lf1,
                                    text="Z, μm (" +
                                    str(self.XYZ_LEFT_BORDER) +
                                    "-" +
                                    str(self.XYZ_RIGHT_BORDER) +
                                    "): ")
        self.z_lab_lf1.grid(column=0, 
                            row=2,
                            padx=5,
                            sticky="E")
        
        ## SPINBOX X
        self.x_spin_lf1 = ttk.Spinbox(self.lf1,
                                      from_=self.XYZ_LEFT_BORDER,
                                      to=self.XYZ_RIGHT_BORDER,
                                      width=10)
        self.x_spin_lf1.grid(column=1, 
                             row=0,
                             padx=5,
                             sticky="E")

        ## SPINBOX Y
        self.y_spin_lf1 = ttk.Spinbox(self.lf1, 
                                      from_=self.XYZ_LEFT_BORDER,
                                      to=self.XYZ_RIGHT_BORDER, 
                                      width=10)
        self.y_spin_lf1.grid(column=1, 
                             row=1,
                             padx=5,
                             sticky="E")

        ## SPINBOX Z
        self.z_spin_lf1 = ttk.Spinbox(self.lf1, 
                                      from_=self.XYZ_LEFT_BORDER, 
                                      to=self.XYZ_RIGHT_BORDER, 
                                      width=10)
        self.z_spin_lf1.grid(column=1, 
                             row=2,
                             padx=5,
                             sticky="E")
        
        ## BUTTON GO
        self.go_button_lf1 = ttk.Button(self.lf1,
                                        text="Go",
                                        command=self.on_go)
        self.go_button_lf1.grid(column=0,
                                row=3,
                                sticky="W",
                                padx=5,
                                pady=5)
        self.go_button_lf1.configure(state="disabled")
        
        ## BUTTON GO TO ORIGIN
        self.go_to_origin_button_lf1 = ttk.Button(self.lf1,
                                              text="Go to Origin",
                                              command=self.on_go_to_origin)
        self.go_to_origin_button_lf1.grid(column=1,
                                      row=3,
                                      padx=5,
                                      pady=5,
                                      sticky='E')
        self.go_to_origin_button_lf1.configure(state="disabled")
        
        
        #*+++++++++++++++++++ /LABELFRAME GO TO POSITION ++++++++++++++++++++++


        #*+++++++++++++++++ LABELFRAME CURRENT VALUES +++++++++++++++++++++++++
        
        bg_color = "#ABEBC6"
        self.lf2 = tk.LabelFrame(self, text='Current values:', 
                                 bg=bg_color, 
                                 relief="flat")
        self.lf2.grid(column=1,
                      row=0,
                      padx=5,
                      pady=5,
                      sticky="EN")
        
        ## LABEL X
        self.x_lab_lf2 = tk.Label(self.lf2, text="X, μm: ", bg=bg_color)
        self.x_lab_lf2.grid(column=0, 
                            row=0,
                            padx=5,
                            sticky="E")

        ## LABEL Y
        self.y_lab_lf2 = tk.Label(self.lf2, text="Y, μm: ", bg=bg_color)
        self.y_lab_lf2.grid(column=0,
                            row=1,
                            padx=5,
                            sticky="E")

        ## LABEL Z
        self.z_lab_lf2 = tk.Label(self.lf2, text="Z, μm: ", bg=bg_color)
        self.z_lab_lf2.grid(column=0,
                            row=2,
                            padx=5,
                            sticky="E")
        
        ## LABEL CURRENT WAVENUMBER
        self.wavenum_lab_lf2 = tk.Label(self.lf2, text="ν‎, cm⁻¹: ", bg=bg_color)
        self.wavenum_lab_lf2.grid(column=0,
                                  row=3, 
                                  padx=5,
                                  pady=5,
                                  sticky="E")
        
        ## LABEL X COORD
        self.x_coord_lab_lf2 = tk.Label(self.lf2, text="---", bg=bg_color)
        self.x_coord_lab_lf2.grid(column=1,
                                  row=0,
                                  padx=5,
                                  sticky="E")

        ## LABEL Y COORD
        self.y_coord_lab_lf2 = tk.Label(self.lf2, text="---", bg=bg_color)
        self.y_coord_lab_lf2.grid(column=1,
                                  row=1,
                                  padx=5,
                                  sticky="E")

        ## LABEL Z COORD
        self.z_coord_lab_lf2 = tk.Label(self.lf2, text="---", bg=bg_color)
        self.z_coord_lab_lf2.grid(column=1, 
                                  row=2,
                                  padx=5,
                                  sticky="E")
        
        ## LABEL CURRENT WAVENUMBER VAL
        self.wavenum_val_lab_lf2 = tk.Label(self.lf2, text="---", bg=bg_color)
        self.wavenum_val_lab_lf2.grid(column=1,
                                      row=3, 
                                      padx=5,
                                      pady=5,
                                      sticky="E")
        
        #*+++++++++++++++++ /LABELFRAME CURRENT POSITION ++++++++++++++++++++++
         

        #*+++++++++++++++++++++++++ NOTEBOOK ++++++++++++++++++++++++++++++++++

        self.nb = ttk.Notebook(self)
        self.nb.grid(column=0, row=1)
        
        #*+++++++++++++++++++++++++ /NOTEBOOK +++++++++++++++++++++++++++++++++
        

        #*++++++++++++++++++++++ FRAME IMAGING ++++++++++++++++++++++++++++++++
        
        ## FRAME IMAGING FRAME
        self.imaging_frame = ttk.Frame(self.nb)
        self.imaging_frame.grid(column=0,
                        row=0,
                        padx=0,
                        pady=0,
                        sticky="NSEW")
        # stretch row "11" down to the bottom
        self.imaging_frame.rowconfigure(12, weight=1) 
        
        # stretch column "1" to the right
        self.imaging_frame.columnconfigure(1, weight=1)
        
        
        ## LABEL Z
        self.z_lab_fr_im = ttk.Label(self.imaging_frame,
                                    text="Z, μm (" +
                                    str(self.XYZ_LEFT_BORDER) +
                                    "-" +
                                    str(self.XYZ_RIGHT_BORDER) +
                                    "): ")
        self.z_lab_fr_im.grid(column=0, 
                            row=0,
                            padx=5,
                            pady=(5, 0),
                            sticky="E")
        Hovertip(self.z_lab_fr_im, "Height")
        
        ## SPINBOX Z
        self.z_spin_fr_im = ttk.Spinbox(self.imaging_frame,
                                from_=self.XYZ_LEFT_BORDER,
                                to=self.XYZ_RIGHT_BORDER,
                                width=10)
        self.z_spin_fr_im.grid(column=1, 
                             row=0, 
                             padx=5,
                             pady=(5, 0),
                             sticky="E")
                
        ## LABEL X1
        self.x1_lab_fr_im = ttk.Label(self.imaging_frame,
                                    text="X1, μm (" +
                                    str(self.XYZ_LEFT_BORDER) +
                                    "-" +
                                    str(self.XYZ_RIGHT_BORDER) +
                                    "): ")
        self.x1_lab_fr_im.grid(column=0, 
                               row=1,
                               padx=5,
                               pady=(7, 0),
                               sticky="E")
        
        ## SPINBOX X1
        self.x1_spin_fr_im = ttk.Spinbox(self.imaging_frame,
                                from_=self.XYZ_LEFT_BORDER,
                                to=self.XYZ_RIGHT_BORDER,
                                width=10)
        self.x1_spin_fr_im.grid(column= 1,
                                row=1, 
                                padx=5,
                                pady=(7, 0),
                                sticky="E")
        
        ## LABEL Y1
        self.y1_lab_fr_im = ttk.Label(self.imaging_frame,
                                    text="Y1, μm (" +
                                    str(self.XYZ_LEFT_BORDER) +
                                    "-" +
                                    str(self.XYZ_RIGHT_BORDER) +
                                    "): ")
        self.y1_lab_fr_im.grid(column=0,
                               row=2, 
                               padx=5,
                               sticky="E")
        
        ## SPINBOX Y1
        self.y1_spin_fr_im = ttk.Spinbox(self.imaging_frame,
                                from_=self.XYZ_LEFT_BORDER,
                                to=self.XYZ_RIGHT_BORDER, 
                                width=10)
        self.y1_spin_fr_im.grid(column=1,
                              row=2,
                              padx=5,
                              sticky="E")
        
        ## LABEL X2
        self.x2_lab_fr_im = ttk.Label(self.imaging_frame,
                                    text="X2, μm (" +
                                    str(self.XYZ_LEFT_BORDER) +
                                    "-" +
                                    str(self.XYZ_RIGHT_BORDER) +
                                    "): ")
        self.x2_lab_fr_im.grid(column=0, 
                               row=3, 
                               padx=5,
                               pady=(7, 0),
                               sticky="E")
        
        ## SPINBOX X2
        self.x2_spin_fr_im = ttk.Spinbox(self.imaging_frame,
                                from_=self.XYZ_LEFT_BORDER,
                                to=self.XYZ_RIGHT_BORDER,
                                width=10)
        self.x2_spin_fr_im.grid(column=1,
                                row=3,
                                padx=5,
                                pady=(7, 0),
                                sticky="E")
        
        ## LABEL Y2
        self.y2_lab_fr_im = ttk.Label(self.imaging_frame,
                                    text="Y2, μm (" +
                                    str(self.XYZ_LEFT_BORDER) +
                                    "-" +
                                    str(self.XYZ_RIGHT_BORDER) +
                                    "): ")
        self.y2_lab_fr_im.grid(column=0,
                                row=4,
                                padx=5,
                                sticky="E")
        
        ## SPINBOX Y2
        self.y2_spin_fr_im = ttk.Spinbox(self.imaging_frame, 
                                from_=self.XYZ_LEFT_BORDER,
                                to=self.XYZ_RIGHT_BORDER,
                                width=10)
        self.y2_spin_fr_im.grid(column=1, 
                                row=4,
                                padx=5,
                                sticky="E")
        
        ## LABEL ΔX
        self.delta_x_lab_fr_im = ttk.Label(self.imaging_frame, text="ΔX, μm: ")
        self.delta_x_lab_fr_im.grid(column=0,
                                    row=5,
                                    padx=5,
                                    pady=(7, 0),
                                    sticky="E")
        
        ## SPINBOX ΔX
        self.delta_x_spin_fr_im = ttk.Spinbox(self.imaging_frame,
                                            from_=self.XYZ_LEFT_BORDER,
                                            to=self.XYZ_RIGHT_BORDER,
                                            width=10)
        self.delta_x_spin_fr_im.grid(column=1,
                                    row=5,
                                    padx=5,
                                    pady=(7, 0),
                                    sticky="E")
        
        ## LABEL ΔY
        self.delta_y_lab_fr_im = ttk.Label(self.imaging_frame, text="ΔY, μm: ")
        self.delta_y_lab_fr_im.grid(column=0,
                                    row=6,
                                    padx=5,
                                    sticky="E")
        
        ## SPINBOX ΔY
        self.delta_y_spin_fr_im = ttk.Spinbox(self.imaging_frame,
                                from_=self.XYZ_LEFT_BORDER,
                                to=self.XYZ_RIGHT_BORDER,
                                width=10)
        self.delta_y_spin_fr_im.grid(column=1, 
                                   row=6,
                                   padx=5,
                                   sticky="E")
        
        ## LABEL SCAN WAVENUMBER
        self.scan_wavenumber_lab_fr_im = ttk.Label(self.imaging_frame, 
                                                      text="Scan wavenumber, cm⁻¹: ")
        self.scan_wavenumber_lab_fr_im.grid(column=0,
                                            row=7,
                                            padx=5,
                                            pady=(7, 0),
                                            sticky="E")
        
        ## SPINBOX CURRENT WAVENUMBER
        self.scan_wavenumber_spin_fr_im = ttk.Spinbox(self.imaging_frame,
                                from_=self.WAVENUM_LEFT_BORDER,
                                to=self.WAVENUM_RIGHT_BORDER,
                                width=10)
        self.scan_wavenumber_spin_fr_im.grid(column=1, 
                                            row=7,
                                            padx=5,
                                            pady=(7, 0),
                                            sticky="E")
        
        ## IMAGELABEL RECT
        self.rec_image = ttk.Label(self.imaging_frame, image=self.logo)
        self.rec_image.grid(column=0,
                                row=8,
                                columnspan=2,
                                padx=5,
                                pady=5)
        
        ## CHECKBUTTON LOG TO CONSOLE
        self.log_to_console_checkbut_fr_im = ttk.Checkbutton(self.imaging_frame,
                                variable=self.log_to_console_var_fr_im,
                                text="Enable console logging",
                                onvalue=1,
                                offvalue=0)
        self.log_to_console_checkbut_fr_im.grid(column=0,
                                row=9,
                                columnspan=2,
                                sticky="W",
                                padx=(5, 0),
                                pady=(10,0),
                                )
        
        ## CHECKBUTTON PLOT THETA
        self.plot_theta_checkbut_fr_im = ttk.Checkbutton(self.imaging_frame,
                                variable=self.plot_theta_var_fr_im,
                                text="Plot Theta",
                                onvalue=1,
                                offvalue=0)
        self.plot_theta_checkbut_fr_im.grid(column=0,
                                row=10,
                                columnspan=2,
                                sticky="W",
                                padx=(5, 0),
                                pady=0)
        
        ## CHECKBUTTON PLOT R
        self.plot_r_checkbut_fr_im = ttk.Checkbutton(self.imaging_frame,
                                variable=self.plot_r_var_fr_im,
                                text="Plot R",
                                onvalue=1,
                                offvalue=0)
        self.plot_r_checkbut_fr_im.grid(column=0,
                                row=11,
                                columnspan=2,
                                sticky="W",
                                padx=(5, 0),
                                pady=0)

        ## BUTTON APPLY PARAMETERS
        self.apply_parameters_button_fr_im = ttk.Button(self.imaging_frame, 
                                text = "Apply parameters",
                                command=self.on_imag_apply_parameters)
        self.apply_parameters_button_fr_im.grid(column=0,
                                row=12,
                                padx=5,
                                pady=5, 
                                sticky="W")
        
        ## LABEL TAKE TIME
        self.take_time_lab_fr_im = tk.Label(self.imaging_frame, text="")
        self.take_time_lab_fr_im.grid(column=1, 
                                    row=12,
                                    padx=5,
                                    pady=5,
                                    sticky="E")
        
      
        ## BUTTON START
        self.start_button_fr_im = ttk.Button(self.imaging_frame,
                                       text="Start imaging", 
                                       command=self.on_imag_start)
        self.start_button_fr_im.grid(column=0,
                                row=13,
                                padx=5,
                                pady=(10, 5), 
                                sticky="SW")
        self.start_button_fr_im.configure(state="disabled")
        
        
        ## PROGRESSBAR IMAGING PROCESS
        self.imag_prog_bar_fr_im = ttk.Progressbar(self.imaging_frame, 
                                orient="horizontal",
                                mode="determinate")
        self.imag_prog_bar_fr_im.grid(column=1, 
                                row=13,
                                padx=(0, 5),
                                pady=(10, 7), 
                                sticky="SEW")  
        
        #*++++++++++++++++++++++ /FRAME IMAGING +++++++++++++++++++++++++++++++          
        
       
        #*+++++++++++++++++++++++++ FRAME SPECTRA +++++++++++++++++++++++++++++
       
        ## FRAME SPECTRA
        self.spectra_frame = ttk.Frame(self.nb)
        self.spectra_frame.grid(column=0,
                                row=0,
                                padx=0,
                                pady=0,
                                sticky="NSEW")
        # stretch row "6" down to the bottom
        self.spectra_frame.rowconfigure(6, weight=1)   
        
        # stretch column "1" to the right
        self.spectra_frame.columnconfigure(1, weight=1)  
        
        ## LABEL ν‎1
        self.wavenum1_lab_fr_sp = ttk.Label(self.spectra_frame,
                                    text="ν‎1, cm⁻¹ (" +
                                    str(self.WAVENUM_LEFT_BORDER) +
                                    "-" +
                                    str(self.WAVENUM_RIGHT_BORDER) +
                                    "): ")
        self.wavenum1_lab_fr_sp.grid(column=0, 
                            row=0,
                            padx=(5, 5),
                            pady=(5, 0),
                            sticky="E")
        
        ## SPINBOX ν‎1
        self.wavenum1_spin_fr_sp = ttk.Spinbox(self.spectra_frame,
                                from_=self.WAVENUM_LEFT_BORDER,
                                to=self.WAVENUM_RIGHT_BORDER,
                                width=10)
        self.wavenum1_spin_fr_sp.grid(column=1, 
                              row=0, 
                              padx=5,
                              pady=(5, 0),
                              sticky="E")
        
        ## LABEL ν‎2
        self.wavenum2_lab_fr_sp = ttk.Label(self.spectra_frame,
                                    text="ν‎2, cm⁻¹ (" +
                                    str(self.WAVENUM_LEFT_BORDER) +
                                    "-" +
                                    str(self.WAVENUM_RIGHT_BORDER) +
                                    "): ")
        self.wavenum2_lab_fr_sp.grid(column=0, 
                            row=1,
                            padx=(5, 5),
                            pady=(7, 0),
                            sticky="E")
        
        ## SPINBOX ν‎2
        self.wavenum2_spin_fr_sp = ttk.Spinbox(self.spectra_frame,
                                from_=self.WAVENUM_LEFT_BORDER,
                                to=self.WAVENUM_RIGHT_BORDER,
                                width=10)
        self.wavenum2_spin_fr_sp.grid(column=1, 
                              row=1, 
                              padx=5,
                              pady=(7, 0),
                              sticky="E")
        
        ## LABEL Δν
        self.delta_wavenum_lab_fr_sp = ttk.Label(self.spectra_frame,
                                    text="Δν, cm⁻¹: ")
        self.delta_wavenum_lab_fr_sp.grid(column=0, 
                                        row=2,
                                        padx=(5, 5),
                                        pady=(7, 0),
                                        sticky="E")
                    
        ## SPINBOX Δν‎
        self.delta_wavenum_spin_fr_sp = ttk.Spinbox(self.spectra_frame,
                                from_=0,
                                to=self.WAVENUM_RIGHT_BORDER,
                                width=10)
        self.delta_wavenum_spin_fr_sp.grid(column=1, 
                                          row=2, 
                                          padx=5,
                                          pady=(7, 0),
                                          sticky="E")
        
        
        ## CHECKBUTTON LOG TO CONSOLE
        self.log_to_console_checkbut_fr_sp = ttk.Checkbutton(self.spectra_frame,
                                variable=self.log_to_console_var_fr_sp,
                                text="Enable console logging",
                                onvalue=1,
                                offvalue=0)
        self.log_to_console_checkbut_fr_sp.grid(column=0,
                                row=3,
                                columnspan=2,
                                sticky="W",
                                padx=5,
                                pady=(10, 0))
        
        ## CHECKBUTTON PLOT R
        self.plot_r_checkbut_fr_sp = ttk.Checkbutton(self.spectra_frame,
                                variable=self.plot_r_var_fr_sp,
                                text="Plot R",
                                onvalue=1,
                                offvalue=0)
        self.plot_r_checkbut_fr_sp.grid(column=0,
                                row=4,
                                columnspan=2,
                                sticky="W",
                                padx=5,
                                pady=0)
        
        ## BUTTON APPLY PARAMETERS
        self.apply_parameters_button_fr_sp = ttk.Button(self.spectra_frame, 
                                text = "Apply parameters",
                                command=self.on_spec_apply_parameters)
        self.apply_parameters_button_fr_sp.grid(column=0,
                                row=5,
                                padx=5,
                                pady=10, 
                                sticky="W") 
        
        ## LABEL TAKE TIME
        self.take_time_lab_fr_sp = tk.Label(self.spectra_frame, text="")
        self.take_time_lab_fr_sp.grid(column=1, 
                                        row=5,
                                        padx=5,
                                        pady=5,
                                        sticky="E")

        
        ## BUTTON START
        self.start_button_fr_sp = ttk.Button(self.spectra_frame,
                                        text="Start spectra", 
                                        command=self.on_spec_start)
        self.start_button_fr_sp.grid(column=0,
                                    row=6,
                                    padx=5,
                                    pady=(10, 5), 
                                    sticky="SW")
        self.start_button_fr_sp.configure(state="disabled")
        
        ## PROGRESSBAR IMAGING PROCESS
        self.spec_prog_bar_fr_sp = ttk.Progressbar(self.spectra_frame, 
                                orient="horizontal",
                                mode="determinate")
        self.spec_prog_bar_fr_sp.grid(column=1, 
                                row=6,
                                padx=(0, 5),
                                pady=(10, 7), 
                                sticky="SEW")  
        
        #*+++++++++++++++++++++++++ /FRAME SPECTRA ++++++++++++++++++++++++++++
        
        
        #*+++++++++++++++++++++++ ADD FRAMES TO NOTEBOOK ++++++++++++++++++++++
        
        self.nb.add(self.imaging_frame, text="Imaging")
        self.nb.add(self.spectra_frame, text="Spectra")
        
        #*+++++++++++++++++++++++ /ADD FRAMES TO NOTEBOOK +++++++++++++++++++++


        #*++++++++++++++ LABELFRAME LOCK-IN PARAMETERS ++++++++++++++++++++++++
        
        self.lf4 = ttk.LabelFrame(self, text="Lock-in parameters")
        self.lf4.grid(column=1,
                                row=1,
                                padx=5,
                                pady=(13, 5), 
                                sticky="NW")
        
        ## LABEL FILTER SLOPE
        self.filter_slope_lab_lf4 = ttk.Label(self.lf4, text="Low pass filter slope: ")
        self.filter_slope_lab_lf4.grid(column=0,
                                row=0,
                                sticky="E",
                                padx=5)
        
        ## SPINBOX FILTER SLOPE
        self.filter_slope_spin_lf4 = ttk.Spinbox(self.lf4,
                                from_=1,
                                to=8,
                                width=10,
                                textvariable=self.filter_slope_var)
        self.filter_slope_spin_lf4.grid(column=1,
                                row=0,
                                sticky="NW",
                                padx=5)
        
        ## LABEL TIME CONSTANT
        self.time_constant_lab_lf4 = ttk.Label(self.lf4, 
                                text="Time constant: ")
        self.time_constant_lab_lf4.grid(column=0,
                                row=1,
                                sticky="E",
                                padx=5)
        
        ## SPINBOX TIME CONSTANT
        self.time_constant_spin_lf4 = ttk.Spinbox(self.lf4,
                                from_=0,
                                to=1,
                                increment=0.1,
                                width=10,
                                textvariable=self.time_constant_var)
        self.time_constant_spin_lf4.grid(column=1,
                                row=1,
                                sticky="NW",
                                padx=5)
        
        ## LABEL DATA TRANSFER RATE
        self.data_transafer_rate_lab_lf4 = ttk.Label(self.lf4, 
                                text="Data transafer rate: ")
        self.data_transafer_rate_lab_lf4.grid(column=0,
                                row=2,
                                sticky="E",
                                padx=5)
        
        ## SPINBOX DATA TRANSFER RATE
        self.data_transafer_rate_spin_lf4 = ttk.Spinbox(self.lf4,
                                from_=1,
                                to=10000,
                                width=10,
                                textvariable=self.data_transafer_rate_var)
        self.data_transafer_rate_spin_lf4.grid(column=1,
                                row=2,
                                sticky="NW",
                                padx=5)
        
        ## LABEL SCALING
        self.scaling_lab_lf4 = ttk.Label(self.lf4, text="Scaling: ")
        self.scaling_lab_lf4.grid(column=0,
                                row=3,
                                sticky="E",
                                padx=5)
        
        ## SPINBOX SCALING
        self.scaling_spin_lf4 = ttk.Spinbox(self.lf4,
                                from_=1,
                                to=10,
                                width=10,
                                textvariable=self.scaling_var)
        self.scaling_spin_lf4.grid(column=1,
                                row=3,
                                sticky="NW",
                                padx=5)
        
        ## LABEL EXTERNAL REFERENCE CHANNEL
        self.scaling_lab_lf4 = ttk.Label(self.lf4, text="Enable external reference channel: ")
        self.scaling_lab_lf4.grid(column=0,
                                row=4,
                                sticky="E",
                                padx=5)
        
        ## CHECKBUTTON EXTERNAL REFERENCE CHANNEL
        self.channel_checkbut_lf4 = ttk.Checkbutton(self.lf4,
                                variable=self.channel_var,
                                onvalue=1,
                                offvalue=0)
        self.channel_checkbut_lf4.grid(column=1,
                                row=4,
                                sticky="W",
                                padx=(3, 5))
        
        #*++++++++++++++ /LABELFRAME LOCK-IN PARAMETERS +++++++++++++++++++++++       


        #*+++++++++++++++++++++++++ SETTIGNS ++++++++++++++++++++++++++++++++++
        
        self.lf6 = ttk.LabelFrame(self, text='Settigns')
        self.lf6.grid(column=1,
                      row=1,
                      padx=5,
                      sticky='WE')
        
        ## BUTTON READ CURRENT R VALUE
        self.monitor_current_r_but_lf6 = ttk.Button(self.lf6, 
                                                 text="Monitor current R",
                                                 command=self.on_monitor_current_r)
        self.monitor_current_r_but_lf6.grid(column=0, 
                                         row=0,
                                         padx=5,
                                         sticky="W")
        self.monitor_current_r_but_lf6.configure(state="disable")
        
        self.current_r_lab_lf6 = ttk.Label(self.lf6, text="---")
        self.current_r_lab_lf6.grid(column=1, 
                                    row=0, 
                                    padx=5,
                                    sticky="W")
        
        # CHECKBUTTON FAST MODE
        self.fast_mode_checkbut_lf6 = ttk.Checkbutton(self.lf6,
                                        text="Fast mode",
                                        variable=self.fast_mode_var,
                                        onvalue=1,
                                        offvalue=0)
        self.fast_mode_checkbut_lf6.grid(column=0, 
                                               row=1, 
                                               padx=5,
                                               sticky="W")
        Hovertip(self.fast_mode_checkbut_lf6, "When checked the program will run \
as fast as it can while disabling\nsome tracking functions and emergency abort")
        
        
        #*++++++++++++++++++++++ /SETTIGNS ++++++++++++++++++++++++++++++++++++

        #*++++++++++++++++ LABELFRAME SAVE FILE +++++++++++++++++++++++++++++++
        
        ## LABELFRAME SAVE FILE
        self.lf5 = ttk.Labelframe(self, text="Save data to file")
        self.lf5.grid(column=1, 
                      row=1, 
                      sticky="SEW",
                      pady=(140, 0),
                      padx=5)
        
        ## LABEL SAVE FILE
        self.save_file_lab_lf5 = ttk.Label(self.lf5, text="Enter file name: ")
        self.save_file_lab_lf5.grid(column=0, 
                                    row=0, 
                                    padx=5,
                                    sticky="E")
        
        ## ENTRY SAVE FILE
        self.save_file_entry_lf5 = ttk.Entry(self.lf5, 
                                             width=26, 
                                             textvariable=self.file_name)
        self.save_file_entry_lf5.grid(column=1, 
                                      row=0,
                                      padx=5,
                                      sticky="EW")
        
        ## CHECKBUTTON SAVE THETA
        self.save_theta_checkbut_lf5 = ttk.Checkbutton(self.lf5,
                                text="Save Theta",
                                variable=self.save_theta_lf5_var,
                                onvalue=1,
                                offvalue=0)
        self.save_theta_checkbut_lf5.grid(column=0,
                                row=1,
                                sticky="W",
                                padx=(5, 0))
        
        ## CHECKBUTTON SAVE R
        self.save_r_checkbut_lf5 = ttk.Checkbutton(self.lf5,
                                text="Save R",
                                variable=self.save_r_lf5_var,
                                onvalue=1,
                                offvalue=0)
        self.save_r_checkbut_lf5.grid(column=0,
                                row=2,
                                sticky="W",
                                padx=(5, 0))
        
        ## BUTTON SAVE FILE
        self.save_but_lf5 = ttk.Button(self.lf5,
                                       text="Save",
                                       command=self.on_save_file)
        self.save_but_lf5.grid(column=0,
                                row=3,
                                sticky="W",
                                padx=(5, 0),
                                pady=5)
        self.save_but_lf5.configure(state="disable")
        
        #*++++++++++++++++ /LABELFRAME SAVE FILE +++++++++++++++++++++++++++++++

        ## BUTTON INITIALIZE
        self.initialize_button = tk.Button(self,
                                            text="Initialize",
                                            command=self.on_initialize)
        self.initialize_button.config(bg="green", 
                                      fg="white")
        self.initialize_button.grid(column=0,
                                    row=3,
                                    padx=(5, 0),
                                    pady=5,
                                    sticky="SW")
        
        Hovertip(self.initialize_button, "Press this button first\nto initialize \
hardware and software")
                

        #*+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        
        # list of buttons to be disabled while experiment is in progress
        self.buttons = [self.apply_parameters_button_fr_im, 
                        self.apply_parameters_button_fr_sp,
                        self.start_button_fr_im,
                        self.start_button_fr_sp]
                            

    #!============================= FUNCTIONS =================================
    
    def on_monitor_current_r(self):
        """
        Monitor current R value
        
        """
        text = self.monitor_current_r_but_lf6["text"]
        if text == "Monitor current R":
            self.monitor_current_r_but_lf6["text"] = "Stop monitoring"
            self.brake_monitoring = False
            
            while self.brake_monitoring is False:
                sample = self.daq.getSample('/' + self.device + '/demods/0/sample')
                sample_x = float(sample['x'])
                sample_y = float(sample['y'])
                r_value = np.hypot(sample_x, sample_y) # sqrt(x^2 + y^2)
                self.current_r_lab_lf6["text"] = str(round(r_value * 1E6, 6)) + " μV"
                self.update()
                
        elif text == "Stop monitoring":
            self.brake_monitoring = True
            self.monitor_current_r_but_lf6["text"] = "Monitor current R"


    def read_position(self):
        """
        Read and write position of piezo stage

        """
        coords = self.piezo.get_position()
        self.x_coord_lab_lf2["text"] = round(coords[0], 2)
        self.y_coord_lab_lf2["text"] = round(coords[1], 2)
        self.z_coord_lab_lf2["text"] = round(coords[2], 2)


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
            #TODO: edit here if needed
            self.daq = zhinst.ziPython.ziDAQServer('192.168.70.26', 8004, 5)
            
            # detect lock-in and record its address
            self.device = zhinst.utils.autoDetect(self.daq, exclude=None)
        except Exception:
            showerror(message="Error while opening ziServer!")
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
            showerror(message="Error setting lock-in parameters!")
            return -1


    def on_initialize(self):
        """
        Action when "Initialize" button is clicked 
        
        """
        text = self.initialize_button["text"]
        if text == "Initialize":
            try:
                # initialize piezo stage
                self.piezo = Madpiezo() 
                
                # initialize laser
                self.ff3 = Firefly_LW.Firefly_LW(sock=None) # long WL
                
                if self.piezo.handler != 0: # is good
                    self.initialize_button.config(text="Stop", bg="red")
                    
                    # make buttons enabled
                    self.go_button_lf1.configure(state="enabled")
                    self.go_to_origin_button_lf1.configure(state="enabled")
                    
                    # initial coords when initialized. Edit here if needed
                    self.piezo_go_to_position(50, 50, 50) 
                
                    # used as a flag for some GUI elements
                    self.initialized = True 
                    self.break_loop = False # for emergency abort
                    self.experiment_type = None
                    
                    self.save_but_lf5.configure(state="disable")
                    
                    
                else: # is bad
                    showinfo(message="Error initializing!")
                    self.initialize_button.config(text="Error initializing!",
                                                  bg="yellow", 
                                                  fg="black")
            except Exception as e: # is bad
                showerror(message=e)
                self.initialize_button.config(text="Error initializing!", 
                                              bg="yellow", 
                                              fg="black")
                
        elif text == "Stop":
            self.piezo_stop()
            self.monitor_current_r_but_lf6.configure(state="disable")
            
            ex_type = self.experiment_type
            
            if ex_type == "Imaging":
                self.break_loop = True
                print("Emergency abort imaging!")
                plt.close() # close plot window
                
            elif ex_type == "Spectra":
                self.break_loop = True
                self.ff3.go_to_wavelength(self.wavenum_pattern[0])
                print("Emergency abort spectra!")
                plt.close() # close plot window
    
             
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
            showerror(message="Error stopping piezo!")
            return -1


    def on_go(self):
        """
        Tries to move piezo stage to entered coords.

        """
        try:    
            # read data from spinboxes
            x = round(float(self.x_spin_lf1.get()), 2)
            y = round(float(self.y_spin_lf1.get()), 2)
            z = round(float(self.z_spin_lf1.get()), 2)
        except Exception:
            showwarning(message="Bad values! Enter numbers.")
            return -1
        
        # check if values are in proper ranges  
        if self.xyz_is_in_proper_range(x, y, z):
            self.piezo_go_to_position(x, y, z)
        else:
            showwarning(message="Values must be in proper ranges! Try again.")
            
      
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
    
    
    ## CHECKING LOCK-IN PARAMETERS
    def is_lockin_param_good(self, filter_slope, time_constant, 
                    data_transafer_rate, scaling, enable_external_channel):
        """
        Check if entered lock-in parameters are good
        
        """
        
        #TODO: WRITE A CHECK FUNCTION HERE IF NEEDED!
        
        return True
    

    def on_save_file(self):
        """
        Save file

        """
        need_save_r = self.save_r_lf5_var.get()
        need_save_theta = self.save_theta_lf5_var.get()
        
        if need_save_r == 0 and need_save_theta == 0:
            showwarning(message="Check what do you want to save!")
            return -1
        
        filename = self.file_name.get()
        
        if filename:
            try:
                # date in format like this: [YYYY-MM-DD@HH-MM]
                date = datetime.today().strftime('[%Y-%m-%d@%H-%M] ')
                ext = ".csv"
                if self.experiment_type == "Imaging":
                    dir_name = "C:\\Users\\Administrator\\OneDrive - nd.edu\\\
Documents\\Measurements\\Maps\\"
                    
                    if need_save_r and need_save_theta:
                        postfix_r = "__r"
                        postfix_theta = "__theta"
                        
                        full_name_r = (dir_name + date + filename + 
                                       postfix_r + ext)
                        np.savetxt(full_name_r, self.r_data, delimiter=",")
                        
                        
                        full_name_theta = (dir_name + date + filename +
                                           postfix_theta + ext)
                        np.savetxt(full_name_theta, self.theta_data, delimiter=",")
                    elif need_save_r:
                        postfix_r = "__r"
                        
                        full_name_r = (dir_name + date + filename + 
                                       postfix_r + ext)
                        np.savetxt(full_name_r, self.r_data, delimiter=",")
                        
                    elif need_save_theta:
                        postfix_theta = "__theta"
                        
                        full_name_theta = (dir_name + date + filename +
                                           postfix_theta + ext)
                        np.savetxt(full_name_theta, self.theta_data, delimiter=",")
                        
                elif self.experiment_type == "Spectra" and need_save_r:
                    dir_name = "C:\\Users\\Administrator\\OneDrive - nd.edu\\\
Documents\\Measurements\\Spectra\\"
                    full_name = dir_name + date + filename + ext
                    np.savetxt(full_name, self.data_save, delimiter=",")
            except Exception as e:
                showerror(message=e)
            else:
                showinfo(message="All files were successfully saved!")
                    
        else:
            showwarning(message="Enter file name!")
            return -1


    def imag_plot_initialize(self, need_plot_r, need_plot_theta, 
                             interpolation="None", 
                             cmap="jet"):
        """
        Initialize plot when doing imaging.
        
        """
        
        if need_plot_r and need_plot_theta:
            
            fig, ax = plt.subplots(1, 2) # two plots in a row
            fig.tight_layout(pad=4.0) # add space between plots
            
            ax[0].set_title("IR-PHI signal [a.u.]")
            ax[1].set_title("Phase")
            
            # disable axis
            ax[0].set_axis_off()
            ax[1].set_axis_off()
            
            plot_r = ax[0].imshow(self.r_data, cmap=cmap, 
                    extent=[self.x1, self.x2, self.y1, self.y2], 
                    vmin=0, vmax=1, interpolation=interpolation, 
                    animated=True)
                
            plot_theta = ax[1].imshow(self.theta_data, cmap=cmap, 
                extent=[self.x1, self.x2, self.y1, self.y2],
                vmin=0, vmax=1, interpolation=interpolation, 
                animated=True)
            
            #! colorbar is not updating in a loop. Thus, it is off

            # divider1 = make_axes_locatable(ax[0])
            # cax1 = divider1.append_axes("right", size="5%", pad=0.3)
            
            # divider2 = make_axes_locatable(ax[1])
            # cax2 = divider2.append_axes("right", size="5%", pad=0.3)
            
            # # add colorbars to plots
            # fig.colorbar(plot_r, cax=cax1)
            # fig.colorbar(plot_theta, cax=cax2)
            
            plt.pause(0.05)
            
            plt.show(block=False)
            
            bg = fig.canvas.copy_from_bbox(fig.bbox)
            
            ax[0].draw_artist(plot_r)
            ax[1].draw_artist(plot_theta)
            
            fig.canvas.blit(fig.bbox)
            
            return plot_r, plot_theta, fig, ax, bg
        
        elif need_plot_r:
                        
            fig, ax = plt.subplots(1, 1)
            ax.set_title("IR-PHI signal [a.u.]")        
            
            # disable axis
            ax.set_axis_off()
            
            plot_r = ax.imshow(self.r_data, cmap=cmap, 
                extent=[self.x1, self.x2, self.y1, self.y2],
                vmin=0, vmax=1, interpolation=interpolation,
                animated=True) 
            
            #! colorbar is not updating in a loop. Thus, it is off

            # add colorbar to plots
            # fig.colorbar(plot_r)
            
            plt.pause(0.05)
            
            plt.show(block=False)
            bg = fig.canvas.copy_from_bbox(fig.bbox)
            ax.draw_artist(plot_r)
            fig.canvas.blit(fig.bbox)
            
            return plot_r, fig, ax, bg
        
        elif need_plot_theta:
                
            fig, ax = plt.subplots(1, 1)
            ax.set_title("Phase")        
            
            # disable axis
            ax.set_axis_off()
            
            plot_theta = ax.imshow(self.theta_data, cmap=cmap, 
                extent=[self.x1, self.x2, self.y1, self.y2],
                vmin=0, vmax=1, interpolation=interpolation, 
                animated=True)
            
            #! colorbar is not updating in a loop. Thus, it is off

            # add colorbar to plots
            # fig.colorbar(plot_theta)
            
            plt.pause(0.05)
            plt.tight_layout()
            plt.show(block=False)
            bg = fig.canvas.copy_from_bbox(fig.bbox)
            ax.draw_artist(plot_theta)
            fig.canvas.blit(fig.bbox)
            
            return plot_theta, fig, ax, bg
        
     
    def on_imag_apply_parameters(self):
        """
        An action when "Apply" button (IMAGING) is pressed.
        
        """
        # set eperiment type for "save" procedure
        self.experiment_type = "Imaging"
        
        self.save_but_lf5.configure(state="disable")
        
        if self.initialized: # if piezo initialized
            try:    
                # read scan area parameters
                self.z = round( float(self.z_spin_fr_im.get()), 2)
                
                # "self" for variables that will be used elsewhere
                self.x1 = round( float(self.x1_spin_fr_im.get()), 2)
                self.y1 = round( float(self.y1_spin_fr_im.get()), 2)
                self.x2 = round( float(self.x2_spin_fr_im.get()), 2)
                self.y2 = round( float(self.y2_spin_fr_im.get()), 2)
                
                delta_x = round( float(self.delta_x_spin_fr_im.get()), 2)
                delta_y = round( float(self.delta_y_spin_fr_im.get()), 2)
                
            except Exception:
                showerror(message="Error while reading imaging parameters!")
                return -1
            
            try:
                # read lock-in parameters
                filter_slope = int( self.filter_slope_spin_lf4.get() )
                time_constant = float( self.time_constant_spin_lf4.get() )
                data_transafer_rate = int( self.data_transafer_rate_spin_lf4.get() )
                scaling = int( self.scaling_spin_lf4.get() )
                enable_external_channel = int( self.channel_var.get() )
            except Exception:
                showerror(message="Error while reading lock-in parameters!")
                return -1
                        
            scan_param_bool = self.is_imag_param_good(self.z, 
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
                showwarning(message="Check entered values for consistency!")
                return -1
            
            # aprox time const for imaging in sec
            self.INTEGRATION_TIME_IMAGING = time_constant * 3.3 

            self.imag_prog_bar_fr_im["value"] = 0 # initialize prog bar
            
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
            
            wavenum = int(self.scan_wavenumber_spin_fr_im.get())
            
            # go to initial wavelength
            self.ff3.go_to_wavelength(wavenum)
            self.read_current_wavelength(self.ff3, final_wavenumber=wavenum)
            
            # make "start imaging" button active
            self.start_button_fr_im.configure(state="enable")
            
            # 0.05 sec is needed for getting data from lock-in
            needed_time_in_min = round(((self.INTEGRATION_TIME_IMAGING +\
0.05) * len_x * len_y) / 60, 2) 
            
            # write aprox time for experiment
            self.take_time_lab_fr_im['text'] = ("Needed time: ~" + 
                                                str(needed_time_in_min) +
                                                " min")
            
            self.monitor_current_r_but_lf6.configure(state="enable")
        else:
            showwarning(message="Initialize piezo first!")
            return -1
           
     
    def on_imag_start(self):  
        """
        Action when "Start Imaging" button is clicked
        
        """      
        
        # go to the initial position of the scan
        self.piezo_go_to_position(self.x1, self.y1, self.z)

        # make buttons disabled
        self.go_button_lf1.configure(state="disabled")
        self.go_to_origin_button_lf1.configure(state="disabled")
        
        scan_shape = np.shape(self.x_pattern)

        self.r_data = np.zeros(scan_shape)
        self.theta_data = np.zeros(scan_shape)
        
        length = scan_shape[0] * scan_shape[1]
        
        # set values for progressbar
        if self.fast_mode_var.get() == 0:
            prog_bar_values = np.linspace(1, 100, length)
            prog_bar_values.astype(int) # convert to int       
        
        total_time_min = 0 # for time accumulation
        
        ## PLOT PRE-TREATMENT
        
        # check if there is something to plot from checkbuttons
        need_plot_r = self.plot_r_var_fr_im.get()
        need_plot_theta = self.plot_theta_var_fr_im.get()
        
        # plot both R and Theta
        if need_plot_r and need_plot_theta:
            
            # initialize min and max value for cmap real-time updating
            min_r_value = 1000
            min_theta_value = 1000
            
            max_r_value = -100
            max_theta_value = -100
            
            # initialize values for first plot
            r_value = 0
            theta_deg = 0
            
            plot_r, plot_theta, fig, ax, bg = self.imag_plot_initialize(1, 1, 
                                                           interpolation="None",
                                                           cmap="jet")
            
        # plot R only   
        elif need_plot_r:
            
            # initialize min and max value for cmap real-time updating
            min_r_value = 1000
            max_r_value = -100
            
            # initialize value for first plot
            r_value = 0
            
            plot_r, fig, ax, bg = self.imag_plot_initialize(1, 0,
                                                    interpolation="None",
                                                    cmap="jet")
            
        # plot Theta only
        elif need_plot_theta:
            
            # initialize min and max value for cmap real-time updating
            min_theta_value = 1000
            max_theta_value = -100
            
            # initialize value for first plot
            theta_deg = 0
            
            plot_theta, fig, ax, bg = self.imag_plot_initialize(0, 1,
                                                    interpolation="None",
                                                    cmap="jet")
            
        need_write_to_console = self.log_to_console_var_fr_im.get()
            
        # move the piezo over the scan area
        for step, index in enumerate(np.ndindex(scan_shape)):
            try:
                
                t1 = time() # start time
                
                if self.fast_mode_var.get() == 0:
                    self.read_position() # read current position
                    self.update()  
                    if self.break_loop:
                        break
                
                # invert index to fill array from the bottom to the top
                index_im = scan_shape[0] - 1 - index[0], index[1] 
                
                if self.fast_mode_var.get() == 0:
                    
                    # change value in progress bar 
                    self.imag_prog_bar_fr_im["value"] = prog_bar_values[step]
                    # self.update_idletasks() # try to update prog bar

                # go to the next position and read position
                self.piezo.goxy(self.x_pattern[index], self.y_pattern[index])
                
                # use integration pause for plotting
                t1_integration = time()

                # plot R and Theta
                if need_plot_r and need_plot_theta:
                
                    fig.canvas.restore_region(bg)
                    
                    plot_r.set_data(self.r_data)
                    plot_theta.set_data(self.theta_data)
                                
                    if r_value < min_r_value : min_r_value = r_value
                    if r_value > max_r_value : max_r_value = r_value
                    
                    if theta_deg < min_theta_value : min_theta_value = theta_deg
                    if theta_deg > max_theta_value : max_theta_value = theta_deg
                    
                    # reset color range
                    plot_r.set_clim(min_r_value, max_r_value) 
                    plot_theta.set_clim(min_theta_value, max_theta_value) 
                    
                    ax[0].draw_artist(plot_r)
                    ax[1].draw_artist(plot_theta)
                    
                    fig.canvas.blit(fig.bbox)
                    fig.canvas.flush_events()
                
                # plot R
                elif need_plot_r:
                    
                    fig.canvas.restore_region(bg)
                    
                    plot_r.set_data(self.r_data)
                    
                    if r_value < min_r_value : min_r_value = r_value
                    if r_value > max_r_value : max_r_value = r_value
                    
                    # reset color range
                    plot_r.set_clim(min_r_value, max_r_value) 
                    
                    ax.draw_artist(plot_r)
                    
                    fig.canvas.blit(fig.bbox)
                    fig.canvas.flush_events() 
                
                # plot Theta
                elif need_plot_theta:
                    
                    fig.canvas.restore_region(bg)
                    
                    plot_theta.set_data(self.theta_data)
                    
                    if theta_deg < min_theta_value : min_theta_value = theta_deg
                    if theta_deg > max_theta_value : max_theta_value = theta_deg

                    plot_theta.set_clim(min_theta_value, max_theta_value)
                    
                    ax.draw_artist(plot_theta)
                    
                    fig.canvas.blit(fig.bbox)
                    fig.canvas.flush_events()

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
                        print(f"{'STEP' : <7}{'X, μm' : ^10}{'Y, μm' : ^10}\
{'R' : ^15}{'THETA, deg' : ^15}{'DURATION, MS' : >20}")
                        print(f"{'='*77}")
                    else:  
                        print(f"{step : <7}{x_coord : ^10}{y_coord : ^10}\
{r_value : ^15,.4f}{theta_deg : ^15,.4f}{time_ms : >20}")      

            except Exception as e:
                showerror(message=e)
                return -1
            
        if self.break_loop == False: 
            if need_plot_r and need_plot_theta:
                #--------------------------------------------------------------
                divider1 = make_axes_locatable(ax[0])
                cax1 = divider1.append_axes("right", size="5%", pad=0.3)
                
                divider2 = make_axes_locatable(ax[1])
                cax2 = divider2.append_axes("right", size="5%", pad=0.3)
                
                # add colorbars to plots
                fig.colorbar(plot_r, cax=cax1)
                fig.colorbar(plot_theta, cax=cax2)
                #--------------------------------------------------------------
                fig.canvas.restore_region(bg)
                
                plot_r.set_data(self.r_data)
                plot_theta.set_data(self.theta_data)
                            
                if r_value < min_r_value : min_r_value = r_value
                if r_value > max_r_value : max_r_value = r_value
                
                if theta_deg < min_theta_value : min_theta_value = theta_deg
                if theta_deg > max_theta_value : max_theta_value = theta_deg
                
                # reset color range
                plot_r.set_clim(min_r_value, max_r_value) 
                plot_theta.set_clim(min_theta_value, max_theta_value) 
                
                ax[0].draw_artist(plot_r)
                ax[1].draw_artist(plot_theta)
                
                fig.canvas.blit(fig.bbox)
                fig.canvas.flush_events()

                plt.tight_layout()
                plt.show()
            
            # plot R
            elif need_plot_r:
                
                fig.canvas.restore_region(bg)
                
                plot_r.set_data(self.r_data)
                
                if r_value < min_r_value : min_r_value = r_value
                if r_value > max_r_value : max_r_value = r_value
                
                # reset color range
                plot_r.set_clim(min_r_value, max_r_value) 
                
                ax.draw_artist(plot_r)

                divider = make_axes_locatable(ax)
                cax = divider.append_axes("right", size="5%", pad=0.3)
                fig.colorbar(plot_r, cax=cax, orientation='vertical')
                
                fig.canvas.blit(fig.bbox)
                fig.canvas.flush_events()

                plt.show()
            
            # plot Theta
            elif need_plot_theta:
                
                fig.canvas.restore_region(bg)
                
                plot_theta.set_data(self.theta_data)
                
                if theta_deg < min_theta_value : min_theta_value = theta_deg
                if theta_deg > max_theta_value : max_theta_value = theta_deg

                plot_theta.set_clim(min_theta_value, max_theta_value)
                
                ax.draw_artist(plot_theta)

                divider = make_axes_locatable(ax)
                cax = divider.append_axes("right", size="5%", pad=0.3)
                fig.colorbar(plot_theta, cax=cax, orientation='vertical')
                
                fig.canvas.blit(fig.bbox)
                fig.canvas.flush_events()

                plt.show()
    
            
            print(f"\n\nDone! For {length} steps it took {round(total_time_min, 2)} min.\
On average {round(total_time_min * 1000 * 60 / length, 2)} ms per step.")
            
            self.save_but_lf5.configure(state="enable")
            self.take_time_lab_fr_im['text'] = ""

            # maybe not needed
            
            # try:
            #     self.piezo_stop() # stop piezo
            # except Exception:
            #     showerror(message="Error stopping piezo after imaging!")


    #!============================ SPECTRA FUNCTIONS ==========================
    
    def on_spec_apply_parameters(self):

        """
        Action when "Apply Parameters" for Spectra is clicked

        """
        
        self.experiment_type = "Spectra"
        self.save_but_lf5.configure(state="disable")
        
        if self.initialized:
            try:    
                # read spectra parameters
                wavenum1 = int(self.wavenum1_spin_fr_sp.get())
                wavenum2 = int(self.wavenum2_spin_fr_sp.get())
                delta_wavenum = int(self.delta_wavenum_spin_fr_sp.get())                
            except Exception:
                showerror(message="Error while reading spectra parameters!")
                return -1
            
            try:
                # read lock-in parameters
                filter_slope = int(self.filter_slope_spin_lf4.get())
                time_constant = float(self.time_constant_spin_lf4.get())
                data_transafer_rate = int(self.data_transafer_rate_spin_lf4.get())
                scaling = int(self.scaling_spin_lf4.get())
                enable_external_channel = int(self.channel_var.get())
            except Exception:
                showerror(message="Error while reading lock-in parameters!")
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
                showwarning(message="Check entered values for consistency!")
                return -1
            
            self.INTEGRATION_TIME_SPECTRA = time_constant * 3.3

            self.spec_prog_bar_fr_sp["value"] = 0 # prog bar
            
            
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
            self.start_button_fr_sp.configure(state="enable")
            
            needed_time_in_min = round(((self.INTEGRATION_TIME_SPECTRA +\
0.05 + 0.5) * self.len_wavenum) / 60, 2) 
            
            # write aprox time for experiment
            self.take_time_lab_fr_sp['text'] = ("Needed time: ~" + 
                                                str(needed_time_in_min) + 
                                                " min")
        else:
            showwarning(message="Initialize piezo first!")
            return -1
    

    def on_spec_start(self):
        """
        Action when "Start Spectra" button is clicked
        
        """
        
        # make buttons disabled
        self.go_button_lf1.configure(state="disabled")
        self.go_to_origin_button_lf1.configure(state="disabled")
        
        
        scan_shape = self.len_wavenum
        r_data = np.zeros(scan_shape)
        
        if self.fast_mode_var.get() == 0:
            # initialize prog bar
            prog_bar_values = np.linspace(1, 100, scan_shape)
            prog_bar_values.astype(int) # convert to int
        

        # read current coords from "Current position" labelframe
        x_coord = round( float(self.x_coord_lab_lf2.cget("text")), 2)
        y_coord = round( float(self.y_coord_lab_lf2.cget("text")), 2)
        
        ## PLOT PRE-TREATMENT
        need_plot_r = self.plot_r_var_fr_sp.get()
            
        # plot R  
        if need_plot_r:
            
            min_r_value = 1000
            max_r_value = -100
            
            # initialize value for first plot
            r_value = 0

            plt.ion()
            fig, ax = plt.subplots() # for R 
            ax.set_title("IR absorption Chart")
            ax.set_xlabel("ν, cm⁻¹")
            ax.set_ylabel("IR absorption")
            ax.grid(visible=True)
            # ax.set_yticks([]) 

            (plot_r, ) = ax.plot(self.wavenum_pattern, r_data)
                 
        
        total_time_min = 0 # for time accumulation 
        
        need_write_to_console = self.log_to_console_var_fr_sp.get()
        
        # move the piezo over the scan area
        for step, index in enumerate(np.ndindex(scan_shape)):
            try:
                t1 = time() # start time
                
                if self.fast_mode_var.get() == 0:
                    self.read_current_wavelength(self.ff3)
                
                    # change value in progress bar 
                    self.spec_prog_bar_fr_sp["value"] = prog_bar_values[step]
                    self.update()
                    
                    if self.break_loop:
                        break
                
                # go to wavelength
                self.ff3.go_to_wavelength(self.wavenum_pattern[index])
                
                # plot R    
                if need_plot_r:
                    
                    plot_r.set_ydata(r_data)
                    
                    if r_value < min_r_value : min_r_value = r_value
                    if r_value > max_r_value : max_r_value = r_value

                    ax.set_ylim(min_r_value, max_r_value) 
                    fig.canvas.draw()
                    fig.canvas.flush_events()

                    
                
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
                        print(f"{'STEP' : <7}{'X, μm' : ^10}{'Y, μm' : ^10}\
{'ν, cm⁻¹' : ^10}{'R' : ^15}{'DURATION, ms' : >20}")
                        print(f"{'='*72}")
                    else:  
                        print(f"{step : <7}{x_coord : ^10}{y_coord : ^10}\
{wavenum_val : ^10}{r_value : ^15,.4f}{time_ms : >20}")   
            
            except Exception as e:
                showerror(message=e)
                return -1
        
        # show static image when loop is over   
        if self.break_loop == False:
            if need_plot_r:

                # set new data
                plot_r.set_ydata(r_data)
                
                if r_value < min_r_value : min_r_value = r_value
                if r_value > max_r_value : max_r_value = r_value
                ax.set_ylim(min_r_value, max_r_value) 

                fig.canvas.draw()
                fig.canvas.flush_events()

                plt.ioff()
                plt.show()

                
        
        print(f"Done! For {scan_shape} steps it took {round(total_time_min, 2)} min.\
On average {round(total_time_min * 1000 * 60 / scan_shape, 2)} ms per step.")
        
        # to reset laser wavelength
        initial_wavenum = self.wavenum_pattern[0]
        self.ff3.go_to_wavelength(initial_wavenum)
        self.read_current_wavelength(self.ff3, final_wavenumber=initial_wavenum)
        
        # add R norm
        r_data_norm = r_data / np.max(r_data)
        
        # data to save to file
        self.data_save = np.transpose([self.wavenum_pattern, r_data, r_data_norm])
        
        self.save_but_lf5.configure(state="enable")
        self.take_time_lab_fr_im['text'] = ""
        
        # disable "theta" checkbutton when save
        self.save_theta_checkbut_lf5.configure(state="disable")

            # maybe not needed
            # try:
            #     self.piezo_stop() # stop piezo
            # except Exception:
            #     showerror(message="Error stopping piezo after imaging!")


    ## CHECKS WHETHER SPEC PARAMETERS ARE GOOD
    def is_spec_param_good(self, wavenum1, wavenum2, delta_wavenum):
        wavenum1_bool = self.WAVENUM_LEFT_BORDER <= wavenum1 <= self.WAVENUM_RIGHT_BORDER
        wavenum2_bool = wavenum1 < wavenum2 <= self.WAVENUM_RIGHT_BORDER
        delta_wavenum_bool = 0 < (wavenum2 - wavenum1)
        
        total_bool = (wavenum1_bool * wavenum2_bool * delta_wavenum_bool)
        return total_bool
    
    
    ## READ CURRENT WAVELENGTH
    def read_current_wavelength(self, ff3, final_wavenumber=None):
        try:
            pattern = r"\"current_wavelength\":\[(\d+\.\d+)\]"
            status = ff3.wavelength_status()
            status = status.decode("utf-8")
            current_wavenumber = round(float(re.findall(pattern, status)[0]), 2)
            self.wavenum_val_lab_lf2["text"] = current_wavenumber         
        except Exception as e:
            showerror(message=e)
        
        if final_wavenumber is not None:
            try:
                delta = 3 
                for button in self.buttons:
                    button.configure(state="disable")
                    
                while (abs((final_wavenumber - current_wavenumber)) > delta):
                    self.update()
                 
                    status = str(ff3.wavelength_status())
                    current_wavenumber = round(float(re.findall(pattern, status)[0]), 2)
                    self.wavenum_val_lab_lf2["text"] = current_wavenumber 
                    sleep(0.2)
                
                # read value for the final time
                status = str(ff3.wavelength_status())
                current_wavenumber = round(float(re.findall(pattern, status)[0]), 2)
                self.wavenum_val_lab_lf2["text"] = current_wavenumber
                
                # make buttons enabled
                for button in self.buttons:
                    button.configure(state="enable")
                    
            except Exception as e:
                showerror(message=e)