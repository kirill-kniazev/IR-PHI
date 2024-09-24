import os, sys
from pathlib import Path

# add parent dir to Python search path
_directory = Path(__file__).resolve()
_parent_dir = _directory.parent
_parent_parent_dit = _parent_dir.parent
# sys.path.append(_parent_dir)

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

# try:
root = tk.Tk()
root.iconphoto(False, tk.PhotoImage(file=str(_parent_parent_dit / "docs" / "laser.png")))
root.title("Laser/Piezo manipulator")
root.resizable(0, 0)
root.protocol("WM_DELETE_WINDOW", on_closing)
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

piezo_gui = PiezoManipulation(root)
piezo_gui.grid(column=0,
                row=0, 
                sticky="NSEW")

root.mainloop()
    
# except Exception:
#     root.destroy()