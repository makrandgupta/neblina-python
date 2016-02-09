
# ProMotion board test utility
# (C) 2015 Motsai Research Inc.
# Author: Omid Sarbishei (o.sarbishei@motsai.com)

from __future__ import print_function
import os
import cmd
import binascii
import serial
import serial.tools.list_ports
import slip
import neblina as neb
import neblinacomm as nebcomm
import neblinasim as sim
import sys
import time


class TestProMotion(cmd.Cmd):
    """docstring for StreamMenu"""
    
    def __init__(self):
        cmd.Cmd.__init__(self)

        self.bigLine = '-------------------------------------------------------------------\n'
        self.configFileName = 'streamconfig.txt'
        self.prompt = '>>'
        self.intro = "ProMotion Test Routine!"
        
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
        
        self.comm = nebcomm.NeblinaComm(sc)
        self.comm.sc.flushInput()
        # Make the module stream towards the UART instead of the default BLE
        self.comm.switchStreamingInterface(True)
        self.comm.motionStopStreams()

        thefile = open('ProMotionTestLog.txt', 'w')
        print(" ")
        dataString = "*** ProMotion Board Test Routine ***\n"
        print(dataString)
        thefile.write(dataString)
        thefile.write("\n")
        dataString = "=================================================================================="
        print( dataString )
        thefile.write(dataString)
        thefile.write("\n")
        dataString = "Test#1: Checking communication with the LSM9DS1 chip by getting the temperature..."
        print( dataString )
        thefile.write(dataString)
        thefile.write("\n")
        dataString = "=================================================================================="
        print( dataString )
        thefile.write(dataString)
        thefile.write("\n")
        temp = self.comm.getTemperature()
        dataString = 'Board Temperature: {0} degrees (Celsius)'.format(temp)
        print(dataString)
        thefile.write(dataString)
        thefile.write("\n")

        dataString =  "Test#1 Passed!!!"
        print( dataString )
        thefile.write(dataString)
        thefile.write("\n\n")
        print(" ")
        dataString = "================================================================================================="
        print( dataString )
        thefile.write(dataString)
        thefile.write("\n")
        dataString = "Test#2: Checking communication between Nordic and KL26 chips by getting the firmware versions..."
        print( dataString )
        thefile.write(dataString)
        thefile.write("\n")
        dataString = "================================================================================================="
        print( dataString )
        thefile.write(dataString)
        thefile.write("\n")
        versionPacket = self.comm.debugFWVersions()
        print(versionPacket.data)
        if (versionPacket.data.bleFWVersion[0]==255):
            dataString = "The Nordic firmware is still unknown."
            print( dataString )
            thefile.write(dataString)
            thefile.write("\n")
            dataString = "Try running the script again after 20 seconds to make sure that Nordic sends its firmware version!"
            print( dataString )
            thefile.write(dataString)
            thefile.write("\n")
            dataString = "If the problem persists, there is a communication problem between Nordic and KL26 chips..."
            print( dataString )
            thefile.write(dataString)
            thefile.write("\n")
            self.comm.switchStreamingInterface(False)
            dataString = "Exiting..."
            print( dataString )
            thefile.write(dataString)
            thefile.write("\n")
            return
        dataString = "Test#2 Passed!!!"
        print( dataString )
        thefile.write(dataString)
        thefile.write("\n\n")
        print(" ")
        dataString = "=========================================================================="
        print( dataString )
        thefile.write(dataString)
        thefile.write("\n")
        dataString = "Test#3: Checking the EEPROM by issuing a write command followed by a read"
        print( dataString )
        thefile.write(dataString)
        thefile.write("\n")
        dataString = "=========================================================================="
        print( dataString )
        thefile.write(dataString)
        thefile.write("\n")
        dataString = "UnitTest"
        dataString = dataString.encode('utf-8')
        self.comm.EEPROMWrite(0, dataString)
        dataBytes = self.comm.EEPROMRead(0)
        if (dataBytes==dataString):
            dataString = "Test#3 Passed!!!"
            print( dataString )
            thefile.write(dataString)
            thefile.write("\n\n")
            print(" ")
            dataString = "=============================================="
            print( dataString )
            thefile.write(dataString)
            thefile.write("\n")
            dataString = "Test#4: Flash Recorder Test on Quaternion Data"
            print( dataString )
            thefile.write(dataString)
            thefile.write("\n")
            dataString = "=============================================="
            print( dataString )
            thefile.write(dataString)
            thefile.write("\n")
            dataString = "Recording 1000 Quaternion packets now..."
            print( dataString )
            thefile.write(dataString)
            thefile.write("\n")
            self.comm.flashRecord(1000, neb.MotCmd_Quaternion)
            dataString = "Playing back 1000 Quaternion packets now..."
            print( dataString )
            thefile.write(dataString)
            thefile.write("\n")
            num = self.comm.flashPlayback(65535)
            if (num==1000):
                dataString = "Test#4 Passed!!!"
                print( dataString )
                thefile.write(dataString)
                thefile.write("\n\n")
                print(" ")
                dataString = "==============================================="
                print( dataString )
                thefile.write(dataString)
                thefile.write("\n")
                dataString = "Test#5: Flash Recorder Test on Euler Angle Data"
                print( dataString )
                thefile.write(dataString)
                thefile.write("\n")
                dataString = "==============================================="
                print( dataString )
                thefile.write(dataString)
                thefile.write("\n")
                dataString = "Recording 1000 Euler Angle now..."
                print( dataString )
                thefile.write(dataString)
                thefile.write("\n")
                self.comm.flashRecord(1000, neb.MotCmd_EulerAngle)
                dataString = "Playing back 1000 Euler Angle packets now..."
                print( dataString )
                thefile.write(dataString)
                thefile.write("\n")

                num = self.comm.flashPlayback(65535)
                if (num==1000):
                    dataString = "Test#5 Passed!!!"
                    print( dataString )
                    thefile.write(dataString)
                    thefile.write("\n\n")
                    print(" ")
                    dataString = "====================================================================================="
                    print( dataString )
                    thefile.write(dataString)
                    thefile.write("\n")
                    dataString = "Test#6: Checking the communication with the PMIC chip by getting the battery level..."
                    print( dataString )
                    thefile.write(dataString)
                    thefile.write("\n")
                    dataString = "====================================================================================="
                    print( dataString )
                    thefile.write(dataString)
                    thefile.write("\n")
                    batteryLevel = self.comm.getBatteryLevel()
                    dataString = 'Battery Level: {0}%'.format(batteryLevel)
                    print( dataString )
                    thefile.write(dataString)
                    thefile.write("\n\n")
                    print(" ")
                    dataString = "============================================"
                    print( dataString )
                    thefile.write(dataString)
                    thefile.write("\n")
                    dataString = "The ProMotion test routing was successful!!!"
                    print( dataString )
                    thefile.write(dataString)
                    thefile.write("\n")
                    dataString = "============================================"
                    print( dataString )
                    thefile.write(dataString)
                    thefile.write("\n")
                else:
                    dataString = "ERROR: Euler Angle data storage/playback failed!!!"
                    print( dataString )
                    thefile.write(dataString)
                    thefile.write("\n")
            else:
                dataString = "ERROR: Quaternion data storage/playback failed!!!"
                print( dataString )
                thefile.write(dataString)
                thefile.write("\n")
        else:
            dataString = "ERROR: EEPROM Read-Back Test Failed!!!"
            print( dataString )
            thefile.write(dataString)
            thefile.write("\n")

        self.comm.switchStreamingInterface(False)
        dataString = "Exiting..."
        print( dataString )
        thefile.write(dataString)
        thefile.write("\n")

        return


if __name__ == '__main__':
    TestProMotion()
