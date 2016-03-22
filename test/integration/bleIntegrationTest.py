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

import logging
import time
import unittest

from neblina import *
from neblinaAPI import NeblinaAPI

###################################################################################


def getSuite(deviceAddress):
    BLEIntegrationTest.deviceAddress = deviceAddress
    return unittest.TestLoader().loadTestsFromTestCase(BLEIntegrationTest)

###################################################################################


class BLEIntegrationTest(unittest.TestCase):
    setupHasAlreadyRun = False
    deviceAddress = None

    def setUp(self):
        if not self.deviceAddress:
            logging.warn("No Device Address specified. Skipping.")
            raise unittest.SkipTest

        # Give it a break between each test
        time.sleep(1)

        self.api = NeblinaAPI(Interface.BLE)
        self.api.open(self.deviceAddress)
        if not self.api.isOpened():
            self.fail("Unable to connect to BLE device.")

    def tearDown(self):
        self.api.close(self.deviceAddress)

    # def testStreamEuler(self):
    #     self.api.motionStream(Commands.Motion.EulerAngle, 100)
    #
    # def testStreamIMU(self):
    #     self.api.motionStream(Commands.Motion.IMU, 100)

    def testMEMSComm(self):
        logging.debug('Checking communication with the LSM9DS1 chip by getting the temperature...')
        temp = self.api.getTemperature()
        logging.info("Board Temperature: {0} degrees (Celsius)".format(temp))
    #
    # def testPMICComm(self):
    #     batteryLevel = self.api.getBatteryLevel()
    #
    # def testUARTPCLoopbackComm(self):
    #     #dataString = "Test#1: Loopback test with KL26 by sending 1000 empty packets..."
    #     for x in range(1, 1001):
    #         logging.debug('Loopback test packet %d\r' % (x), end="", flush=True)
    #         self.api.sendCommand(SubSystem.Debug, Commands.Debug.SetInterface, True)
    #         self.api.waitForAck(SubSystem.Debug, Commands.Debug.SetInterface)
    #
    # def testMotionEngine(self):
    #     testInputVectorPacketList = self.csvVectorsToList('motEngineInputs.csv')
    #     testOutputVectorPacketList = self.csvVectorsToList('motEngineOutputs.csv')
    #     self.api.debugUnitTestEnable(True)
    #     for idx,packetBytes in enumerate(testInputVectorPacketList):
    #         # logging.debug('Sending {0} to stream'.format(binascii.hexlify(packetBytes)))
    #         self.api.comslip.sendPacketToStream(self.api.sc, packetBytes)
    #         packet = self.api.waitForPacket(PacketType.RegularResponse, \
    #                                         SubSystem.Debug, Commands.Debug.UnitTestMotionData)
    #         self.assertEqual(testOutputVectorPacketList[idx], packet.stringEncode())
    #         logging.debug('Sent %d testVectors out of %d\r' % (idx,len(testInputVectorPacketList)) , end="", flush=True)
    #     self.api.debugUnitTestEnable(False)

