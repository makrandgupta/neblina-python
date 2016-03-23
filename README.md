[![Build Status](https://travis-ci.org/Motsai/neblina-python.svg)](https://travis-ci.org/Motsai/neblina-python)
# Neblina Python Scripts
![Python](https://www.python.org/static/community_logos/python-logo-master-v3-TM.png)
![ProMotion Board](http://i.imgur.com/FvKbWka.jpg)


Python scripts that interact with and simulate the behaviour of the Neblina Motion Capture module.
# Requirements
* python3
* pyserial
* Windows or Linux

Start by cloning the git repository onto your computer:
```
git clone https://github.com/Motsai/neblina-python.git
```
## Install the dependencies

```
pip3 install pyserial
```
To be able to run interaction scripts, you must first instantiate the pyslip submodule:
```
git submodule init
git submodule update
```

# Windows
### Include our directories to the Python Environment
![Path](http://i.imgur.com/ftOUSVX.png?1)
## Run the example shell menu
Before connecting the board to the computer, open up `Device Manager` and navigate to `Ports (COM & LTP)`
Now connect the board and note the COM port that it is associated with `COMx`

### Execute the interaction shell
```
> cd examples
> python3 streammenu.py
```
On the execution of the shell script, the program will ask you for the name of the COM port to connect to. Type the name of the dev path you just found `COMx` and press 'Enter'.

# Linux
## Include our directories to the Python Environment
We will edit `./bashrc` to include the directory of the cloned repository as well as its referenced submodules to `PYTHONPATH` everytime a shell is opened
```
$ vi ~/.bashrc
```
Edit the the following lines to point to the directoty where you cloned this repo and add them the end of the file:
```
export PYTHONPATH="${PYTHONPATH}:/path/to/the/repo/neblina-python"
export PYTHONPATH="${PYTHONPATH}:/path/to/the/repo/neblina-python/pyslip"
```

## Run the example shell menu
Connect the Neblina module to your computer through the Serial COM port. On the [ProMotion](http://promotion.motsai.com/) board, there is a serial USB-COM already provided.

### Set permissions on the dev path
Copy the code from [here] (https://gist.github.com/makrandgupta/0e891d0f8578640bcd83) and save it into a file called `dev_path_checker`
Then make the file executable and run it by doing:
```
$ chmod +x dev_path_checker
$ ./dev_path_checker
```
You should see an output similar to this:
```
/dev/ttyACM1 - I-SYST_inc._IDAP-Link_M_CMSIS-DAP_2030615000022
/dev/sdb - IDAP-M_IDAP-Link_M_CMSIS-DAP_2030615000022-0:0
```
Note the dev path with the pattern `/dev/ttyACMx` that corresponds to the device `I-SYST_inc._IDAP-Link_M_CMSIS-DAP_XXXXXXXXXXXXX`
Now set the permissons on that path like so (replace the `x` with the number from the dev path you got):
```
$ sudo chown user /dev/ttyACMx
```
### Execute the interaction shell
```
$ cd examples
$ python3 streammenu.py
```
On the execution of the shell script, the program will ask you for the name of the COM port to connect to. Type the name of the dev path you just found `/dev/ttyACMx` and press 'Enter'.

# Running the unit tests
The unit tests allow for the validation of the decoding and encoding process of the packets. 
Make sure the pyslip submodule has been cloned and then you can now run the unit tests by executing the designated bash script:
```
$ ./runNeblinaDataTests.sh
```

