# neblina-python
Python scripts that interact with and simulate the behaviour of the Neblina Motion Capture module.

# Running the python scripts
Start by cloning the git repository onto your computer:
```
git clone https://github.com/Motsai/neblina-python.git
```

# Executing the unit tests
To be able to run interaction scripts, you must first instantiate the pyslip submodule:
```
cd pyslip
git submodule init
git submodule update
```

Execute the interaction shell:
```
PYTHONPATH=./pyslip/ python3 streammenu.py
```

#Running the unit tests
The unit tests allow for the validation of the decoding and encoding process of the packets. 
Make sure the pyslip submodule has been cloned and then you can now run the unit tests by executing the designated bash script:
```
./runNeblinaDataTests.sh
```

