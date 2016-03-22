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
        if not self.comPort:
            raise unittest.SkipTest("No COM port specified.")

        # Give it a break between each test
        time.sleep(1)

        self.api = NeblinaAPI(Interface.UART, self.comPort)

    def tearDown(self):
        self.api.close()

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
