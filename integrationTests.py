import unittest
import neblina as neb
import neblinacomm as nebcomm
import slip
import binascii
import struct
import os
import serial
import serial.tools.list_ports
import time


class ut_IntegrationTests(unittest.TestCase):
    setupHasAlreadyRun = False

    def setCOMPortName(self):
        self.bigLine = '-------------------------------------------------------------------\n'
        self.prompt = '>>'
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
    
    def setUp(self):
        # Give it a break between each test
        time.sleep(0.5)

        # if(self.setupHasAlreadyRun == False):
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
                sc = serial.Serial(port=comPortName,baudrate=230400)
            except serial.serialutil.SerialException as se:
                if 'Device or resource busy:' in se.__str__():
                    print('Opening COM port is taking a little while, please stand by...')
                else:
                    print('se: {0}'.format(se))
                time.sleep(1)
        
        self.comm = nebcomm.NeblinaComm(sc)
        # Make the module stream towards the UART instead of the default BLE
        self.comm.switchStreamingInterface(True)
        # self.setupHasAlreadyRun = True

    def tearDown(self):
        self.comm.switchStreamingInterface(False)
        self.comm.sc.close()
        print('Bye')

    def testStreamEuler(self):
        # self.comm.switchStreamingInterface(False)
        self.comm.motionStream(neb.MotCmd_EulerAngle, 100)

    def testStreamIMU(self):
        # self.comm.switchStreamingInterface(False)
        self.comm.motionStream(neb.MotCmd_IMU_Data, 100)

if __name__ == "__main__":
    unittest.main() # run all tests
    print (unittest.TextTestResult)
