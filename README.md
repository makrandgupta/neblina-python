# neblina-python
Python scripts that interact with and simulate the behaviour of the Neblina Motion Capture module.

# Running the python scripts 
Start by cloning the git repository onto your computer:
```
git clone https://github.com/Motsai/latero.git
```
Execute the python scripts:
```
python3 neblinasim.py
```
The example streaming data should appear in a new directory called "generated"

# Executing the unit tests
The unit tests allow for the validation of the decoding and encoding process of the packets. To be able to run them, you must first instantiate the pyslip submodule:
```
cd pyslip
git submodule init
git submodule update
```
Once the pyslip submodule has been clone, you can now run the unit tests by executing the designated bash script:
```
./runNeblinaDataTests.sh
```

