
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

        print(" ")
        print( "Started the test routine for the ProMotion board..." )
        print( "==================================================================================" )
        print( "Test#1: Checking communication with the LSM9DS1 chip by getting the temperature..." )
        print( "==================================================================================" )
        temp = self.comm.getTemperature()
        print('Board Temperature: {0} degrees (Celsius)'.format(temp))
        print( "Test#1 Passed!!!" )
        print(" ")
        print( "=================================================================================================" )
        print ( "Test#2: Checking communication between Nordic and KL26 chips by getting the firmware versions..." )
        print( "=================================================================================================" )
        versionPacket = self.comm.debugFWVersions()
        print(versionPacket.data)
        if (versionPacket.data.bleFWVersion[0]==255):
            print ( "The Nordic firmware is still unknown. ")
            print ( "Try running the script again after 20 seconds to make sure that Nordic sends its firmware version!" )
            print ( "If the problem persists, there is a communication problem between Nordic and KL26 chips..." )
            self.comm.switchStreamingInterface(False)
            return -1
        print( "Test#2 Passed!!!" )
        print(" ")
        print( "==========================================================================" )
        print ( "Test#3: Checking the EEPROM by issuing a write command followed by a read" )
        print( "==========================================================================" )
        dataString = "UnitTest"
        dataString = dataString.encode('utf-8')
        self.comm.EEPROMWrite(0, dataString)
        dataBytes = self.comm.EEPROMRead(0)
        if (dataBytes==dataString):
            print( "Test#3 Passed!!!" )
            print(" ")
            print( "==============================================" )
            print( "Test#4: Flash Recorder Test on Quaternion Data" )
            print( "==============================================" )
            print( "Recording 1000 Quaternion packets now..." )
            self.comm.flashRecord(1000, neb.MotCmd_Quaternion)
            print( "Playing back 1000 Quaternion packets now..." )
            num = self.comm.flashPlayback(65535)
            if (num==1000):
                print( "Test#4 Passed!!!" )
                print(" ")
                print( "===============================================" )
                print( "Test#5: Flash Recorder Test on Euler Angle Data" )
                print( "===============================================" )
                print( "Recording 1000 Euler Angle now..." )
                self.comm.flashRecord(1000, neb.MotCmd_EulerAngle)
                print( "Playing back 1000 Euler Angle packets now..." )
                num = self.comm.flashPlayback(65535)
                if (num==1000):
                    print( "Test#5 Passed!!!" )
                    print(" ")
                    print( "=====================================================================================" )
                    print( "Test#6: Checking the communication with the PMIC chip by getting the battery level..." )
                    print( "=====================================================================================" )
                    batteryLevel = self.comm.getBatteryLevel()
                    print('Battery Level: {0}%'.format(batteryLevel))
                    print(" ")
                    print( "============================================" )
                    print( "The ProMotion test routing was successful!!!" )
                    print( "============================================" )
                else:
                    print( "ERROR: Euler Angle data storage/playback failed!!!" )
            else:
                print( "ERROR: Quaternion data storage/playback failed!!!" )
        else:
            print( "ERROR: EEPROM Read-Back Test Failed!!!" )


        self.comm.switchStreamingInterface(False)
        print( "Exiting..." )
        return


if __name__ == '__main__':
    TestProMotion()
