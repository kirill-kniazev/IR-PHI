import os, sys
from pathlib import Path

# get repo directory for future reference
repo_dir = Path(__file__).resolve().parent.parent

import tkinter as tk
from GUI import PiezoManipulation

# ============================== FUNCTIONS ==================================== 
def on_closing():
    is_initialized = piezo_gui.initialized
    
    if is_initialized:
        piezo_gui.piezo_stop()
        root.destroy()   
    else:
        root.destroy()
# =============================================================================

root = tk.Tk()
root.iconphoto(False, tk.PhotoImage(file=str(repo_dir / "docs" / "laser.png")))
root.title("IR-PHI GUI")
root.resizable(0, 0)
root.protocol("WM_DELETE_WINDOW", on_closing)
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

piezo_gui = PiezoManipulation(root)
piezo_gui.grid(column=0,
                row=0, 
                sticky="NSEW")

root.mainloop()