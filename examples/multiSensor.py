import os
import cmd
import binascii
import serial
import serial.tools.list_ports
import slip
import sys
import time

from neblina import *
import neblinaAPI as nebapi

def main():

    devicePortNames = ['/dev/ttyACM0', '/dev/ttyACM1']
    nebBoards = []
    for portName in devicePortNames:
        try:
            sc = serial.Serial(port=portName, baudrate=230400)
            comm = nebapi.NeblinaComm(sc)
            comm.setStreamingInterface(Interface.UART)
            nebBoards.append(comm)
        except serial.serialutil.SerialException as se:
            if 'Device or resource busy:' in se.__str__():
                print('Opening COM port is taking a little while, please stand by...')
            else:
                print('se: {0}'.format(se))

    # Perform a start recording command to each board
    for comm in nebBoards:
        comm.motionResetTimestamp()

    # Switch back to BLE interface
    for comm in nebBoards:
        comm.setStreamingInterface(Interface.BLE)
        comm.sc.close()

if __name__ == '__main__':
    main()