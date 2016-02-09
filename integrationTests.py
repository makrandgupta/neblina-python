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
import csv
import array


class ut_IntegrationTests(unittest.TestCase):
    setupHasAlreadyRun = False

    def csvVectorsToList(self, csvFileName):
        testVectorPacketList = []
        with open(csvFileName, newline='') as testVectorFile:
            testVectorReader = csv.reader(testVectorFile)
            # Remove the empty rows
            testVectors = [row for row in testVectorReader if len(row) != 0]
        for vector in testVectors:
            vectorInts = [int(packetByte) for packetByte in vector]
            vectorBytes = (array.array('B', vectorInts).tobytes())
            testVectorPacketList.append(vectorBytes)
        return testVectorPacketList

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
        time.sleep(1)

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
                sc = serial.Serial(port=comPortName,baudrate=500000)
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
        self.comm.sc.close()
        print('Closed COM Port')

    def testStreamEuler(self):
        self.comm.motionStream(neb.MotCmd_EulerAngle, 100)

    def testStreamIMU(self):
        self.comm.motionStream(neb.MotCmd_IMU_Data, 100)

    def testVersion(self):
        self.comm.debugFWVersions()

    def testMotionEngine(self):
        testInputVectorPacketList = self.csvVectorsToList('./SampleData/motEngineInputs.csv')
        testOutputVectorPacketList = self.csvVectorsToList('./SampleData/motEngineOutputs.csv')
        self.comm.debugUnitTestEnable(True)
        for idx,packetBytes in enumerate(testInputVectorPacketList):
            # print('Sending {0} to stream'.format(binascii.hexlify(packetBytes)))
            self.comm.comslip.sendPacketToStream(self.comm.sc, packetBytes)
            packet = self.comm.waitForPacket(neb.PacketType_RegularResponse, \
                neb.Subsys_Debug, neb.DebugCmd_UnitTestMotionData)
            self.assertEqual(testOutputVectorPacketList[idx], packet.stringEncode())
            print('Sent %d testVectors out of %d\r' % (idx,len(testInputVectorPacketList)) , end="", flush=True)
        self.comm.debugUnitTestEnable(False)

if __name__ == "__main__":
    unittest.main() # run all tests
    print (unittest.TextTestResult)
