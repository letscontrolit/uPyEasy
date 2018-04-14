All modules are now relative symbolic links!

To make the links work, please ensure that you follow the following directory structure:
Root directory (for micropython, upyeasy, etc):
- micropython
- micropython-lib
- picoweb
- utemplate
- micropython-async
- upyeasy
- modbus

Temporary:
- micropython-stm32


Instructions for creating above directory structure:

git clone https://github.com/micropython/micropython.git micropython

git clone https://github.com/micropython/micropython-lib.git micropython-lib

git clone https://github.com/pfalcon/picoweb picoweb

git clone https://github.com/pfalcon/utemplate utemplate

git clone https://github.com/peterhinch/micropython-async.git micropython-async

git clone https://github.com/letscontrolit/upyeasy upyeasy

git clone https://github.com/pycom/pycom-modbus modbus

git clone https://github.com/micropython/micropython.git micropython-stm32


If you do this, then the relative modules symbolic links are all correct.
