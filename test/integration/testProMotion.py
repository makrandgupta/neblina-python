# ProMotion board test utility
# (C) 2015 Motsai Research Inc.
# Author(s):
# - Omid Sarbishei (o.sarbishei@motsai.com)
# - Alexandre Courtemanche (a.courtemanche@motsai.com)

# Tests specific to the ProMotion development kit

from __future__ import print_function
import os
import cmd
import time

import serial
import serial.tools.list_ports
import sys
import time
import logging
import unittest

from neblina import *
import neblinaAPI as nebapi
import neblinasim as sim


class ut_ProMotionTests(unittest.TestCase):
    """docstring for StreamMenu"""

    def setUp(self):
        # Give it a break between each test
        time.sleep(1)

        self.configFileName = 'streamconfig.txt'

        # Check if config file exists
        if(not os.path.exists(self.configFileName)):
            self.setCOMPortName()

        # Read the config file to get the name
        with open(self.configFileName, 'r') as configFile:
                comPortName = configFile.readline()

        # Try to open the serial COM port
        sc = None
        while sc is None:
            try:
                sc = serial.Serial(port=comPortName,baudrate=500000, timeout=1.5)
            except serial.serialutil.SerialException as se:
                if 'Device or resource busy:' in se.__str__():
                    print('Opening COM port is taking a little while, please stand by...')
                else:
                    print('se: {0}'.format(se))
                time.sleep(1)

        self.comm = nebapi.NeblinaComm(sc)
        self.comm.sc.flushInput()
        # Make the module stream towards the UART instead of the default BLE
        self.comm.setStreamingInterface(Interface.UART)
        self.comm.motionStopStreams()

    def tearDown(self):
        self.comm.sc.close()
        print('Closed COM Port')

    def testEEPROM(self):
        print('"Checking the EEPROM by issuing a write command followed by a read"')
        dataString = "UnitTest"
        dataString = dataString.encode()
        self.comm.EEPROMWrite(0, dataString)
        dataBytes = self.comm.EEPROMRead(0)
        self.assertEqual(dataBytes, dataString)

    def testFlashRecord(self):
        print('Flash Recorder Test on Euler Angle Data')
        self.comm.flashRecord(1000, neb.MotCmd_Quaternion)
        dataString = "Playing back 1000 Quaternion packets now..."
        print( dataString )
        num = self.comm.flashPlayback(65535)
        self.assertEqual(num, 1000)

        self.comm.flashRecord(1000, neb.MotCmd_EulerAngle)
        dataString = "Playing back 1000 Euler Angle packets now..."
        print( dataString )
        num = self.comm.flashPlayback(65535)
        self.assertEqual(num, 1000)

    def testBattery(self):
        batteryLevel = self.comm.getBatteryLevel()
        dataString = 'Battery Level: {0}%'.format(batteryLevel)

if __name__ == '__main__':
    print('======================')
    print('ProMotion Test Routine')
    print('======================')
    print('Initializing...')
    time.sleep(1)
    print('.')
    time.sleep(1)
    print('.')
    time.sleep(1)
    print('.')
    unittest.main() # run all tests
    print (unittest.TextTestResult)
