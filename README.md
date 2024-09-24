# IR-PHI laser manipulator

A simple gui that manipulates infrared photothermal heterodyne imaging (IR-PHI) equipment (including piezo stage). More information about IR-PHI can be found [here](https://aip.scitation.org/doi/abs/10.1063/1.5142277).

## Features
- Mad City piezo stage manipulation
- IR-PHI imaging across predetermined area with real-time monitoring
- Doing spectroscopy in predetermined point with real-time monitoring

## Dependecies

To run gui correctly these python packages must be installed prior running:
- `tkinter`
- `numpy`
- `matplotlib`
- ```path```
- `idlelib.tooltip`
- `zhinst`

## Running

To run gui `run.py` (with console) or `run_no_console.pyw` (without console) files should be used.

## Examples

### Imaging

![Imaging](/images/Examples/imaging_2_speed_x3.gif "Imaging example, speed x3")

### Spectroscopy

![Spectroscopy](/images/Examples/spectroscopy_1_speed_x7.gif "Spectroscopy example, speed x7")
