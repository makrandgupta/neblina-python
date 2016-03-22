#!/usr/bin/env python
###################################################################################
#
# Copyright (c)     2010-2016   Motsai
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
###################################################################################

from __future__ import print_function
import os
import cmd
import binascii
import serial
import serial.tools.list_ports
import time
import logging

from neblina import *
from neblinaAPI import NeblinaAPI

###################################################################################


class StreamMenu(cmd.Cmd):
    """docstring for StreamMenu"""

    def __init__(self):
        cmd.Cmd.__init__(self)

        self.bigLine = '-------------------------------------------------------------------\n'
        self.configFileName = 'streamconfig.txt'
        self.prompt = '>>'
        self.intro = "Welcome to the Neblina Streaming Menu!"

        # Check if config file exists
        if not os.path.exists(self.configFileName):
            self.setCOMPortName()

        # Read the config file to get the name
        with open(self.configFileName, 'r') as configFile:
                comPortName = configFile.readline()

        # Try to open the serial COM port
        sc = None
        while sc is None:
            try:
                sc = serial.Serial(port=comPortName, baudrate=500000, timeout=1.5)
            except serial.serialutil.SerialException as se:
                if 'Device or resource busy:' in se.__str__():
                    print('Opening COM port is taking a little while, please stand by...')
                else:
                    print('se: {0}'.format(se))
                time.sleep(1)

        self.comm = NeblinaAPI(sc)
        self.comm.sc.flushInput()
        print("Setting up the connection...")
        time.sleep(1)
        print('.')
        time.sleep(1)
        print('.')
        time.sleep(1)
        print('.')
        # Make the module stream towards the UART instead of the default BLE
        self.comm.setStreamingInterface(Interface.UART)
        self.comm.motionStopStreams()

    # If the user exits with Ctrl-C, try switching the interface back to BLE
    def cmdloop(self, intro=None):
        try:
            cmd.Cmd.cmdloop(self)
        except KeyboardInterrupt as e:
            self.comm.setStreamingInterface(Interface.BLE)

    ## Command definitions ##
    def do_hist(self, args):
        """Print a list of commands that have been entered"""
        print(self._hist)

    def do_exit(self, args):
        """Exits from the console"""
        # Make the module stream back towards its default interface (BLE)
        self.comm.setStreamingInterface(Interface.BLE)
        return -1

    ## Command definitions to support Cmd object functionality ##
    def do_EOF(self, args):
        """Exit on system end of file character"""
        return self.do_exit(args)

    def do_shell(self, args):
        """Pass command to a system shell when line begins with '!'"""
        os.system(args)

    def do_help(self, args):
        """Get help on commands
           'help' or '?' with no arguments prints a list of commands for which help is available
           'help <command>' or '? <command>' gives help on <command>
        """
        ## The only reason to define this method is for the help text in the doc string
        cmd.Cmd.do_help(self, args)

    def setCOMPortName(self):
        portList = [port[0] for port in serial.tools.list_ports.comports()]
        port = input('Select the COM port to use:' + '\n'.join(portList) + '\n' +  \
            self.bigLine + self.prompt)
        while(port not in portList):
            print('{0} not in the available COM ports'.format(port))
            port = input('Select the COM port to use:' + '\n'.join(portList[0]) + '\n' + \
                self.bigLine + self.prompt)

        # Write it to the config file
        configFile = open(self.configFileName, 'w')
        configFile.write(port)
        configFile.close()

    def do_EEPROMWrite(self, args):
        arguments = args.split(' ')

        if len(arguments) < 2:
            print('EEPROMWrite <pageNumber> <8-byte string>')
            return
        if len(arguments[1]) > 8:
            print('The data string must less than 8 bytes')
            return
        arguments[1] = arguments[1].rjust(8) # Pad the string to 8 bytes
        writeBytes = arguments[1].encode('utf-8')
        writePageNumber = int(arguments[0])
        if writePageNumber < 0 or writePageNumber > 255:
            print('Page number must be between 0 and 255 inclusively')
            return

        self.comm.EEPROMWrite(writePageNumber, writeBytes)

        print('Write to page #{0} of dataBytes {1} was successful.'\
            .format(writePageNumber, writeBytes))

    def do_EEPROMRead(self, args):
        arguments = args.split(' ')
        print(arguments)
        print(len(arguments))
        if (arguments[0]) == '' or len(arguments) != 1:
            print('EEPROMRead <pageNumber>')
            return

        readPageNumber = int(arguments[0])
        if readPageNumber < 0 or readPageNumber > 255:
            print('Page number must be between 0 and 255 inclusively')
            return

        dataBytes = self.comm.EEPROMRead(readPageNumber)

        try:
            print('Got \'{0}\' at page #{1}'.format(dataBytes.decode('utf-8'), readPageNumber))
        except UnicodeDecodeError as ude:
            print('Got {0} at page #{1}'.format(dataBytes, readPageNumber))

    def do_setCOMPort(self, args):
        self.setCOMPortName()

    def do_motionState(self, args):
        states = self.comm.motionGetStates()
        print("Distance: {0}\nForce:{1}\nEuler:{2}\nQuaternion:{3}\nIMUData:{4}\nMotion:{5}\nSteps:{6}\nMAGData:{7}\nSitStand:{8}"\
        .format(states[0], states[1], states[2], states[3],\
                states[4], states[5], states[6], states[7], states[8])\
        )

    def do_getBatteryLevel(self, args):
        batteryLevel = self.comm.getBatteryLevel()
        print('Battery Level: {0}%'.format(batteryLevel))

    def do_getTemperature(self, args):
        temp = self.comm.getTemperature()
        print('Board Temperature: {0} degrees (Celsius)'.format(temp))

    def do_streamEuler(self, args):
        self.comm.motionStream(Commands.Motion.EulerAngle)

    def do_streamIMU(self, args):
        self.comm.motionStream(Commands.Motion.IMU)

    def do_streamQuat(self, args):
        self.comm.motionStream(Commands.Motion.Quaternion)

    def do_streamMAG(self, args):
        self.comm.motionStream(Commands.Motion.MAG)

    def do_streamForce(self, args):
        self.comm.motionStream(Commands.Motion.ExtForce)

    def do_streamRotation(self, args):
        self.comm.motionStream(Commands.Motion.RotationInfo)

    def do_streamPedometer(self, args):
        self.comm.motionStream(Commands.Motion.Pedometer)

    def do_streamGesture(self, args):
        self.comm.motionStream(Commands.Motion.FingerGesture)

    def do_streamTrajectory(self, args):
        self.comm.sendCommand(SubSystem.Motion, Commands.Motion.TrajectoryRecStartStop, True) # start recording a reference orientation trajectory
        packet = self.comm.waitForAck(SubSystem.Motion, Commands.Motion.TrajectoryRecStartStop)
        print("Recording a reference trajectory...")
        self.comm.motionStream(Commands.Motion.TrajectoryInfo)

    def do_stopStreams(self, args):
        self.comm.motionStopStreams()

    def do_resetTimestamp(self, args):
        self.comm.motionResetTimestamp()

    def do_downsample(self, args):
        if(len(args) <= 0):
            print('The argument should be a multiplicand of 20, i.e., 20, 40, 60, etc!')
            return
        n = int(args)
        if ((n % 20)!=0):
            print('The argument should be a multiplicand of 20, i.e., 20, 40, 60, etc!')
            return
        self.comm.motionSetDownsample(n)

    def do_setAccFullScale(self, args):
        possibleFactors = [2,4,8,16]
        if(len(args) <= 0):
            print('The argument should be 2, 4, 8, or 16, representing the accelerometer range in g')
            return
        factor = int(args)
        if(factor not in possibleFactors):
            print('The argument should be 2, 4, 8, or 16, representing the accelerometer range in g')
            return
        self.comm.motionSetAccFullScale(factor)

    def do_setled(self, args):
        arguments = args.split(' ')
        if len(arguments) != 2:
            print('setled <ledNumber> <value>')
            return
        ledIndex = int(arguments[0])
        ledValue = int(arguments[1])
        if(ledIndex < 0 or ledIndex > 1):
            print('Only led indices 0 or 1 are valid')
            return
        self.comm.setLED(ledIndex, ledValue)

    def do_flashState(self, args):
        state = self.comm.flashGetState()
        print('State: {0}'.format(state))
        sessions = self.comm.flashGetSessions()
        print('Num of sessions: {0}'.format(sessions))

    def do_flashSessionInfo(self, args):
        if(len(args) <= 0):
            sessionID = 65535
        elif(len(args) > 0):
            sessionID = int(args)
        info = self.comm.flashGetSessionInfo(sessionID)
        if(info == None):
            print('Session {0} does not exist on the flash'\
                .format(sessionID))
        else:
            print( "Session %d: %d packets (%d bytes)"\
            %(info[0], info[1]/18, info[1]) )

    def do_flashErase(self, args):
        self.comm.flashErase()
        print('Flash erase has completed successfully!')

    def do_flashRecordIMU(self, args):
        if(len(args) <= 0):
            numSamples = 1000
        else:
            numSamples = int(args)
        self.comm.flashRecord(numSamples, Commands.Motion.IMU)

    def do_flashRecordEuler(self, args):
        if(len(args) <= 0):
            numSamples = 1000
        else:
            numSamples = int(args)
        self.comm.flashRecord(numSamples, Commands.Motion.EulerAngle)

    def do_flashRecordQuaternion(self, args):
        if(len(args) <= 0):
            numSamples = 1000
        else:
            numSamples = int(args)
        self.comm.flashRecord(numSamples, Commands.Motion.Quaternion)

    def do_flashPlayback(self, args):
        if(len(args) <= 0):
            mySessionID = 65535
        elif(len(args) > 0):
            mySessionID = int(args)
        self.comm.flashPlayback(mySessionID)

    def do_downloadSessionToFile(self, args):
        if(len(args) <= 0):
            mySessionID = 65535
        elif(len(args) > 0):
            mySessionID = int(args)
        fileName = 'flashSession'
        self.comm.flashPlayback(mySessionID, fileName)

    def do_versions(self, args):
        versions = self.comm.debugFWVersions()
        apiRelease = versions[0]
        mcuFWVersion = versions[1]
        bleFWVersion = versions[2]
        deviceID = versions[3]
        print( "API Release: {0}\n\
        MCU Version: {1}.{2}.{3}\n\
        BLE Version: {4}.{5}.{6}\n\
        Device ID: {7}".format(apiRelease,\
            mcuFWVersion[0], mcuFWVersion[1], mcuFWVersion[2],\
            bleFWVersion[0], bleFWVersion[1], bleFWVersion[2],\
            binascii.hexlify(deviceID))
        )

    ## Override methods in Cmd object ##
    def preloop(self):
        """Initialization before prompting user for commands.
           Despite the claims in the Cmd documentaion, Cmd.preloop() is not a stub.
        """
        cmd.Cmd.preloop(self)   ## sets up command completion
        self._hist    = []      ## No history yet
        self._locals  = {}      ## Initialize execution namespace for user
        self._globals = {}

    def postloop(self):
        """Take care of any unfinished business.
           Despite the claims in the Cmd documentaion, Cmd.postloop() is not a stub.
        """
        self.comm.sc.close()
        cmd.Cmd.postloop(self)   ## Clean up command completion
        print ("Exiting...")

    def precmd(self, line):
        """ This method is called after the line has been input but before
            it has been interpreted. If you want to modify the input line
            before execution (for example, variable substitution) do it here.
        """
        self.comm.sc.flushInput()
        # This is added to ensure that the pending bytes in the COM buffer are discarded for each new command.
        # This is crucial to avoid missing Acknowledge packets in the beginning, if Neblina is already streaming.
        self._hist += [ line.strip() ]
        return line

    def postcmd(self, stop, line):
        """If you want to stop the console, return something that evaluates to true.
           If you want to do some post command processing, do it here.
        """
        return stop

    def emptyline(self):
        """Do nothing on empty input line"""
        pass

    def default(self, line):
        """Called on an input line when the command prefix is not recognized.
           In that case we execute the line as Python code.
        """
        try:
            exec(line) in self._locals, self._globals
        except Exception as e:
            print (e.__class__, ":", e)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    console = StreamMenu()
    console . cmdloop()
