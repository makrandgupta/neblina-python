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

import unittest
import os
import serial
import serial.tools.list_ports
import time
import csv
import array
import logging

from neblina import *
from neblinaAPI import NeblinaAPI
import neblinaTestUtilities

###################################################################################


def getSuite():
    return unittest.TestLoader().loadTestsFromTestCase(apiIntegrationTest)

###################################################################################


class apiIntegrationTest(unittest.TestCase):
    setupHasAlreadyRun = False

    def csvVectorsToList(self, csvFileName):
        testVectorPacketList = []
        filepath = neblinaTestUtilities.getDataFilepath(csvFileName)
        with open(filepath, newline='') as testVectorFile:
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
            logging.warning('{0} not in the available COM ports'.format(port))
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
                    logging.info('Opening COM port is taking a little while, please stand by...')
                else:
                    logging.error('se: {0}'.format(se))
                time.sleep(1)

        self.api = NeblinaAPI(sc)
        self.api.sc.flushInput()

        self.api.setStreamingInterface(Interface.UART)
        self.api.stopAllStreams()

    def tearDown(self):
        self.api.setStreamingInterface(Interface.BLE)
        self.api.sc.close()
        logging.info('Closed COM Port')

    def testStreamEuler(self):
        self.api.motionStream(Commands.Motion.EulerAngle, 100)

    def testStreamIMU(self):
        self.api.motionStream(Commands.Motion.IMU, 100)

    def testVersion(self):
        versions = self.api.debugFWVersions()
        logging.info(versions)
        self.assertNotEqual(versions[2][0], 255)

    def testMEMSComm(self):
        logging.debug('Checking communication with the LSM9DS1 chip by getting the temperature...')
        temp = self.api.getTemperature()
        dataString = 'Board Temperature: {0} degrees (Celsius)'.format(temp)

    def testPMICComm(self):
        batteryLevel = self.api.getBatteryLevel()

    def testUARTPCLoopbackComm(self):
        #dataString = "Test#1: Loopback test with KL26 by sending 1000 empty packets..."
        for x in range(1, 1001):
            logging.debug('Loopback test packet %d\r' % (x), end="", flush=True)
            self.api.sendCommand(SubSystem.Debug, Commands.Debug.SetInterface, True)
            self.api.waitForAck(SubSystem.Debug, Commands.Debug.SetInterface)

    def testMotionEngine(self):
        testInputVectorPacketList = self.csvVectorsToList('motEngineInputs.csv')
        testOutputVectorPacketList = self.csvVectorsToList('motEngineOutputs.csv')
        self.api.debugUnitTestEnable(True)
        for idx,packetBytes in enumerate(testInputVectorPacketList):
            # logging.debug('Sending {0} to stream'.format(binascii.hexlify(packetBytes)))
            self.api.comslip.sendPacketToStream(self.api.sc, packetBytes)
            packet = self.api.waitForPacket(PacketType.RegularResponse, \
                                            SubSystem.Debug, Commands.Debug.UnitTestMotionData)
            self.assertEqual(testOutputVectorPacketList[idx], packet.stringEncode())
            logging.debug('Sent %d testVectors out of %d\r' % (idx,len(testInputVectorPacketList)) , end="", flush=True)
        self.api.debugUnitTestEnable(False)

