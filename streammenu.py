# Neblina streaming data utility
# (C) 2015 Motsai Research Inc.
# Author: Alexandre Courtemanche (a.courtemanche@motsai.com)

import os
import cmd
import readline
import binascii
import curses
import serial
import slip
import neblina as neb
import sys
import select
import tty
import termios

class StreamMenu(cmd.Cmd):
    """docstring for StreamMenu"""
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.sc = serial.Serial(port='/dev/ttyACM0',baudrate=230400)
        self.prompt = '>>'
        self.intro = "Welcome to the Neblina Streaming Menu!"

    # Helper Functions
    def waitForAck(self, myslip):
        consoleBytes = myslip.receivePacketFromStream(self.sc)
        packet = neb.NebResponsePacket(consoleBytes)
        while(packet.header.packetType != neb.PacketType_Ack):
            consoleBytes = myslip.receivePacketFromStream(self.sc)
            packet = neb.NebResponsePacket(consoleBytes)
        return packet


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

    def do_getBatteryLevel(self, args):
        errorList = []
        myslip = slip.slip()
        commandPacket = neb.NebCommandPacket(neb.Subsys_PowerManagement,
            neb.PowCmd_GetBatteryLevel, True)
        myslip.sendPacketToStream(self.sc, commandPacket.stringEncode())
        
        # Drop all packets until you get an ack
        packet = self.waitForAck(myslip)
        print('Battery Level: {0}%'.format(packet.data.batteryLevel))

    def do_streamEulerAngles(self, args):
        errorList = []
        myslip = slip.slip()
        commandPacket = neb.NebCommandPacket(neb.Subsys_MotionEngine,
            neb.MotCmd_EulerAngle, True)
        myslip.sendPacketToStream(self.sc, commandPacket.stringEncode())

        packet = self.waitForAck(myslip)

        while(True):
            try:
                consoleBytes = myslip.receivePacketFromStream(self.sc)
                packet = neb.NebResponsePacket(consoleBytes)
                print('yaw:{0},pitch:{1},roll:{2}'.format(packet.data.yaw,
                    packet.data.pitch, packet.data.roll))
            except NotImplementedError as nie:
                print(nie)
            except KeyboardInterrupt as ki:
                commandPacket = neb.NebCommandPacket(neb.Subsys_MotionEngine,
                    neb.MotCmd_EulerAngle, False)
                myslip.sendPacketToStream(self.sc, commandPacket.stringEncode())
                return

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
        self.sc.close()
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
