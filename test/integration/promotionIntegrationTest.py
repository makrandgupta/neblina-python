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

import serial
import serial.tools.list_ports
import time
import logging
import unittest

from neblina import *
from neblinaAPI import NeblinaAPI

###################################################################################


def getSuite(comPort):
    ProMotionIntegrationTest.comPort = comPort
    return unittest.TestLoader().loadTestsFromTestCase(ProMotionIntegrationTest)

###################################################################################


class ProMotionIntegrationTest(unittest.TestCase):
    comPort = None

    def setUp(self):
        # Give it a break between each test
        time.sleep(1)

        # Try to open the serial COM port
        sc = None
        while sc is None:
            try:
                sc = serial.Serial(port=self.comPort,baudrate=500000, timeout=1.5)
            except serial.serialutil.SerialException as se:
                if 'Device or resource busy:' in se.__str__():
                    logging.info('Opening COM port is taking a little while, please stand by...')
                else:
                    logging.info('se: {0}'.format(se))
                time.sleep(1)

        self.api = NeblinaAPI(sc)
        self.api.sc.flushInput()
        # Make the module stream towards the UART instead of the default BLE
        self.api.setStreamingInterface(Interface.UART)
        self.api.motionStopStreams()

    def tearDown(self):
        self.api.sc.close()
        logging.info('Closed COM Port')

    def testEEPROM(self):
        logging.debug('"Checking the EEPROM by issuing a write command followed by a read"')
        dataString = "UnitTest"
        dataString = dataString.encode()
        self.api.EEPROMWrite(0, dataString)
        dataBytes = self.api.EEPROMRead(0)
        self.assertEqual(dataBytes, dataString)

    def testFlashRecord(self):
        logging.info('Flash Recorder Test on Euler Angle Data')
        self.api.flashRecord(1000, Commands.Motion.Quaternion)
        dataString = "Playing back 1000 Quaternion packets now..."
        logging.info( dataString )
        num = self.api.flashPlayback(65535)
        self.assertEqual(num, 1000)

        self.api.flashRecord(1000, Commands.Motion.EulerAngle)
        dataString = "Playing back 1000 Euler Angle packets now..."
        logging.info( dataString )
        num = self.api.flashPlayback(65535)
        self.assertEqual(num, 1000)

    def testBattery(self):
        batteryLevel = self.api.getBatteryLevel()
        dataString = 'Battery Level: {0}%'.format(batteryLevel)
