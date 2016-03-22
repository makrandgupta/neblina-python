import unittest
import neblina as neb
import neblinaAPI as nebapi
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
        
        self.comm = nebapi.NeblinaComm(sc)
        self.comm.sc.flushInput()

        # Make the module stream towards the UART instead of the default BLE
        self.comm.switchStreamingInterface(True)
        self.comm.motionStopStreams()

    def tearDown(self):
        self.comm.sc.close()
        print('Closed COM Port')

    def testStreamEuler(self):
        self.comm.motionStream(neb.MotCmd_EulerAngle, 100)

    def testStreamIMU(self):
        self.comm.motionStream(neb.MotCmd_IMU_Data, 100)
        self.comm.switchStreamingInterface(True) # switch the interface back to BLE when all the tests have been completed!

    def testVersion(self):
        versions = self.comm.debugFWVersions()
        print(versions)
        self.assertNotEqual(versions[2][0], 255)

    def testMEMSComm(self):
        print('Checking communication with the LSM9DS1 chip by getting the temperature...')
        temp = self.comm.getTemperature()
        dataString = 'Board Temperature: {0} degrees (Celsius)'.format(temp)

    def testPMICComm(self):
        batteryLevel = self.comm.getBatteryLevel()

    def testUARTPCLoopbackComm(self):
        #dataString = "Test#1: Loopback test with KL26 by sending 1000 empty packets..."
        for x in range(1, 1001):
            print('Loopback test packet %d\r' % (x), end="", flush=True)
            self.comm.sendCommand(neb.Subsys_Debug, neb.DebugCmd_SetInterface, True)
            self.comm.waitForAck(neb.Subsys_Debug, neb.DebugCmd_SetInterface)

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
    print('Initializing...')
    time.sleep(1)
    print('.')
    time.sleep(1)
    print('.')
    time.sleep(1)
    print('.')
    unittest.main(verbosity=2) # run all tests
    print (unittest.TextTestResult)
    thefile = open('ProMotionTestLog.txt', 'w')
    thefile.write(unittest.TextTestResult)
    thefile.close()


