[![Build Status](https://travis-ci.org/Motsai/neblina-python.svg)](https://travis-ci.org/Motsai/neblina-python)
# Neblina Python Scripts
![Python](https://www.python.org/static/community_logos/python-logo-master-v3-TM.png)
![ProMotion Board](http://i.imgur.com/FvKbWka.jpg)


Python scripts that interact with and simulate the behaviour of the Neblina Motion Capture module.
# Requirements
* python3
* pyserial
* Windows or Linux

# Running the python scripts
Start by cloning the git repository onto your computer:
```
git clone https://github.com/Motsai/neblina-python.git
```
Install the dependencies:
```
pip3 install pyserial
```
To be able to run interaction scripts, you must first instantiate the pyslip submodule:
```
git submodule init
git submodule update
```

Connect the Neblina module to your computer through the Serial COM port. On the [ProMotion](http://promotion.motsai.com/) board, there is a serial USB-COM already provided. Once the module is connected, take note of the COM port name. On Windows, the name would be COMx. On Linux, it would be /dev/ttyACMx.

Execute the interaction shell (Linux):
```
PYTHONPATH=./pyslip/ python3 streammenu.py
```

On the execution of the shell script, the program will ask you for the name of the COM port to connect to. Type the name of the COM port associated with the module and press 'Enter'.


#Running the unit tests
The unit tests allow for the validation of the decoding and encoding process of the packets. 
Make sure the pyslip submodule has been cloned and then you can now run the unit tests by executing the designated bash script:
```
./runNeblinaDataTests.sh
```

