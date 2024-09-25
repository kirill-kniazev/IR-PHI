# IR-PHI laser manipulator

A simple gui that manipulates infrared photothermal heterodyne imaging (IR-PHI) equipment (including piezo stage). More information about IR-PHI can be found [here](https://aip.scitation.org/doi/abs/10.1063/1.5142277).

## Features
- Mad City piezo stage manipulation
- IR-PHI imaging across predetermined area with real-time monitoring
- Doing spectroscopy in predetermined point with real-time monitoring

## Dependecies

To run gui correctly these python packages must be installed prior running from 'requirements.txt'

soft tested with python 3.8

connect to pieo stage. Mad City Labs: Nano Drive and Mad Piezo drivers has to be requested from the compeny.

connect to the morror corection close loop motor.
.NET Framework 4.8 is required https://dotnet.microsoft.com/en-us/download/dotnet-framework/net48
do not install clr from pip
dont use clr packege
pip uninstall clr
pip install pythonnet (will not wirk), so install wheel manually:
link for the wheel: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pythonnet
examples: 
pip install C:\Users\kuno\Downloads\pythonnet-2.5.2-cp39-cp39-win_amd64.whl
pip install C:\Users\kuno\Downloads\pythonnet-2.5.2-cp39-cp39-win32.whl
masage from dev in 2022:
It has been merged into master. We will not backport support for 3.10 (or 3.9) back to the current stable version. 
You can install the prerelease using pip install --pre pythonnet.

connect to lockin aplifuer. NI visa has to be insalled for functiong of the pyvisa packeges
lab one from zurich onstruments has to be instlled for loking aplifyes controls

connect the laser. use the guidlines from the m squared company.
but remember that you will need to set up static ip for the laser controls. follow - https://pureinfotech.com/set-static-ip-address-windows-10/

## Running

To run gui `run.py` (with console) or `run_no_console.pyw` (without console) files should be used.

## Examples

### Imaging

![Imaging](/Examples/imaging_2_speed_x3.gif "Imaging example, speed x3")

### Spectroscopy

![Spectroscopy](/Examples/spectroscopy_1_speed_x7.gif "Spectroscopy example, speed x7")
