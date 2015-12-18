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
        
        # Check if config file exitst
        if(not os.path.exists(self.configFileName)):
            self.setCOMPortName()

        # Read the config file to get the name
        with open(self.configFileName, 'r') as configFile:
                comPortName = configFile.readline()

        sc = serial.Serial(port=comPortName,baudrate=230400)
        self.comm = nebcomm.NeblinaComm(sc)

    ## Command definitions ##
    def do_hist(self, args):
        """Print a list of commands that have been entered"""
        print(self._hist)

    def do_exit(self, args):
        """Exits from the console"""
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

    def do_setCOMPort(self, args):
        self.setCOMPortName()

    def do_getBatteryLevel(self, args):
        errorList = []
        self.comm.sendCommand(neb.Subsys_PowerManagement,\
            neb.PowCmd_GetBatteryLevel, True)
        
        # Drop all packets until you get an ack
        packet = self.comm.waitForAck(neb.Subsys_PowerManagement,\
            neb.PowCmd_GetBatteryLevel)
        print('ack: {0}'.format(packet))
        packet = self.comm.receivePacket()
        print('Battery Level: {0}%'.format(packet.data.batteryLevel))

    def do_streamEuler(self, args):
        self.comm.motionStream(neb.MotCmd_EulerAngle)

    def do_streamIMU(self, args):
        self.comm.motionStream(neb.MotCmd_IMU_Data)

    def do_stopStreams(self, args):
        self.comm.sendCommand(neb.Subsys_MotionEngine,\
            neb.MotCmd_DisableStreaming, True)

    def do_flasherase(self, args):
        # Step 1 - Initialization
        self.comm.sendCommand(neb.Subsys_MotionEngine,neb.MotCmd_IMU_Data, True)
        self.comm.sendCommand(neb.Subsys_MotionEngine,neb.MotCmd_DisableStreaming, True)
        print('Sending the DisableAllStreaming command, and waiting for a response...')

        # Step 2 - wait for ack
        self.comm.waitForAck(neb.Subsys_MotionEngine,neb.MotCmd_DisableStreaming)
        print('Acknowledge packet was received!')

        # Step 3 - erase the flash command
        self.comm.sendCommand(neb.Subsys_Storage, neb.StorageCmd_EraseAll, True)
        print('Sent the EraseAll command, and waiting for a response...')

        # Step 4 - wait for ack
        self.comm.waitForAck(neb.Subsys_Storage,neb.StorageCmd_EraseAll)
        print('Acknowledge packet was received! Started erasing... This takes a couple of minutes...')

        # Step 5 - wait for the completion notice
        self.comm.waitForPacket(neb.PacketType_RegularResponse,\
            neb.Subsys_Storage, neb.StorageCmd_EraseAll)

        print('Flash recorder is completely erased!')

    def do_flashRecord(self, args):

        # Step 1 - Initialization
        self.comm.sendCommand(neb.Subsys_MotionEngine,neb.MotCmd_DisableStreaming, True)
        print('Sending the DisableAllStreaming command, and waiting for a response...')

        # Step 2 - wait for ack
        self.comm.waitForAck(neb.Subsys_MotionEngine,neb.MotCmd_DisableStreaming)
        print('Acknowledge packet was received!')

        # Step 3 - Start recording
        self.comm.sendCommand(neb.Subsys_Storage, neb.StorageCmd_Record, True)
        print('Sending the command to start the flash recorder, and waiting for a response...')
        # Step 4 - wait for ack and the session number
        self.comm.waitForAck(neb.Subsys_Storage, neb.StorageCmd_Record)
        packet = self.comm.waitForPacket(neb.PacketType_RegularResponse,\
            neb.Subsys_Storage, neb.StorageCmd_Record)
        print('Acknowledge packet was received with the session number %d!' % packet.data.sessionID)
        sessionID = packet.data.sessionID

        #print(packet)
        #print('sessionID = {0}'.format(sessionID))

        # Step 5 - enable IMU streaming
        self.comm.sendCommand(neb.Subsys_MotionEngine,neb.MotCmd_IMU_Data, True)
        print('Sending the enable IMU streaming command, and waiting for a response...')

        # Step 6 - wait for ack
        self.comm.waitForAck(neb.Subsys_MotionEngine,neb.MotCmd_IMU_Data)
        print('Acknowledge packet was received!')
        
        # Step 7 - continue recording for n samples
        if(len(args) <= 0):
            n = 1000
        else:
            n = int(args)
        # print ('Recording %d packets takes about %d seconds' % (n,n/50))
        for x in range(1, n+1):
            self.comm.receivePacket()
            print('Recording %d packets, current packet: %d\r' % (n, x), end="", flush=True)

        print('\n')
        # Step 8 - Stop the streaming
        self.comm.sendCommand(neb.Subsys_MotionEngine,neb.MotCmd_IMU_Data, False)
        print('Sending the stop streaming command, and waiting for a response...')

        # Step 9 - wait for ack
        self.comm.waitForAck(neb.Subsys_MotionEngine,neb.MotCmd_IMU_Data)
        print('Acknowledge packet was received!')

        # Step 10 - Stop the recording
        self.comm.sendCommand(neb.Subsys_Storage,neb.StorageCmd_Record, False)
        print('Sending the command to stop the flash recorder, and waiting for a response...')

        # Step 11 - wait for ack and the closed session confirmation
        self.comm.waitForAck(neb.Subsys_Storage,neb.StorageCmd_Record)
        packet = self.comm.waitForPacket(neb.PacketType_RegularResponse,\
            neb.Subsys_Storage, neb.StorageCmd_Record)
        print('The acknowledge packet is received, and session %d is closed successfully' % sessionID)

    def do_flashPlayback(self, args):
        # Step 1 - Initialization
        #self.comm.sendCommand(neb.Subsys_MotionEngine,neb.MotCmd_IMU_Data, True)
        # Step 2 - wait for ack
        #self.comm.waitForAck(neb.Subsys_MotionEngine,neb.MotCmd_IMU_Data)

        #print(args[0])
        if(len(args) <= 0):
            mySessionID = 65535
        elif(len(args) > 0):
            mySessionID = int(args)
        self.comm.sendCommand(neb.Subsys_Storage, neb.StorageCmd_Playback, True, sessionID=mySessionID)
        print('Sent the start playback command, waiting for response...')
        #wait for confirmation
        packet = self.comm.waitForPacket(neb.PacketType_RegularResponse,\
            neb.Subsys_Storage, neb.StorageCmd_Playback)
        mySessionID = packet.data.sessionID
        print('Playback routine started from session number %d' % mySessionID);
        packetList = self.comm.storePacketsUntil(neb.PacketType_RegularResponse, neb.Subsys_Storage, neb.StorageCmd_Playback)
        print('Finished playback from session number %d!' % mySessionID)
        #for packet in packetList:
            #print(packet.data)

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
