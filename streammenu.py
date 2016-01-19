# Neblina streaming data utility
# (C) 2015 Motsai Research Inc.
# Author: Alexandre Courtemanche (a.courtemanche@motsai.com)

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


class StreamMenu(cmd.Cmd):
    """docstring for StreamMenu"""
    
    def __init__(self):
        cmd.Cmd.__init__(self)

        self.bigLine = '-------------------------------------------------------------------\n'
        self.configFileName = 'streamconfig.txt'
        self.prompt = '>>'
        self.intro = "Welcome to the Neblina Streaming Menu!"
        
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
                sc = serial.Serial(port=comPortName,baudrate=115200)
            except serial.serialutil.SerialException as se:
                if 'Device or resource busy:' in se.__str__():
                    print('Opening COM port is taking a little while, please stand by...')
                else:
                    print('se: {0}'.format(se))
                time.sleep(1)
        
        self.comm = nebcomm.NeblinaComm(sc)
        # Make the module stream towards the UART instead of the default BLE
        self.comm.switchStreamingInterface(True)

    # If the user exits with Ctrl-C, try switching the interface back to BLE
    def cmdloop(self):
        try:
            cmd.Cmd.cmdloop(self)
        except KeyboardInterrupt as e:
            self.comm.switchStreamingInterface(False)

    ## Command definitions ##
    def do_hist(self, args):
        """Print a list of commands that have been entered"""
        print(self._hist)

    def do_exit(self, args):
        """Exits from the console"""
        # Make the module stream back towards its default interface (BLE)
        self.comm.switchStreamingInterface(False)
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

    def do_streamEuler(self, args):
        self.comm.motionStream(neb.MotCmd_EulerAngle)

    def do_streamIMU(self, args):
        self.comm.motionStream(neb.MotCmd_IMU_Data)

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

    def do_flashState(self, args):
        state = self.comm.flashGetState()
        print(state)

    def do_flashErase(self, args):
        self.comm.flashErase()
        print('Flash erase has completed successfully!')

    def do_flashRecordIMU(self, args):
        if(len(args) <= 0):
            numSamples = 1000
        else:
            numSamples = int(args)
        self.comm.flashRecord(numSamples, neb.MotCmd_IMU_Data)

    def do_flashRecordEuler(self, args):
        if(len(args) <= 0):
            numSamples = 1000
        else:
            numSamples = int(args)
        self.comm.flashRecord(numSamples, neb.MotCmd_EulerAngle)

    def do_flashRecordQuaternion(self, args):
        if(len(args) <= 0):
            numSamples = 1000
        else:
            numSamples = int(args)
        self.comm.flashRecord(numSamples, neb.MotCmd_Quaternion)

    def do_flashPlayback(self, args):
        if(len(args) <= 0):
            mySessionID = 65535
        elif(len(args) > 0):
            mySessionID = int(args)
        self.comm.flashPlayback(mySessionID)

    def do_versions(self, args):
        versionPacket = self.comm.debugFWVersions()
        print(versionPacket.data)

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
    console = StreamMenu()
    console . cmdloop() 
