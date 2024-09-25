dont use clr packege
pip uninstall clr
pip install pythonnet (will not wirk), so install wheel manually:

link for the wheel: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pythonnet
examples: 
pip install C:\Users\kuno\Downloads\pythonnet-2.5.2-cp39-cp39-win_amd64.whl
pip install C:\Users\kuno\Downloads\pythonnet-2.5.2-cp39-cp39-win32.whl


2022:
It has been merged into master. We will not backport support for 3.10 (or 3.9) back to the current stable version. 
You can install the prerelease using pip install --pre pythonnet.