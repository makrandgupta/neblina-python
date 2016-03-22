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

try:
    from bluepy.btle import *
except ImportError:
    print("Unable to locate bluepy. It is a required module to use neblinaBLE API.")

from neblina import *
from neblinaCommandPacket import NebCommandPacket

###################################################################################

NeblinaServiceUUID = "0DF9F021-1532-11E5-8960-0002A5D5C51B"
NeblinaCtrlServiceUUID = "0DF9F023-1532-11E5-8960-0002A5D5C51B"
NeblinaDataServiceUUID = "0DF9F022-1532-11E5-8960-0002A5D5C51B"

###################################################################################


class NeblinaDelegate(DefaultDelegate):

    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        pass

###################################################################################


class NeblinaDevice(object):

    def __init__(self, address):
        self.address = address
        self.connected = False

        try:
            self.peripheral = Peripheral(self.address, "random")
            self.peripheral.setDelegate(NeblinaDelegate())
            self.connected = True
        except BTLEException as e:
            logging.warning("BTLEException : " + str(e))


###################################################################################


class NeblinaBLE(object):
    """
        NeblinaBLE is the Neblina Bluetooth Low Energy (BLE) Application Program Interface (API)
    """

    def __init__(self):
        self.devices = []

    def connect(self, deviceAddress):
        device = NeblinaDevice(deviceAddress)
        if device.connected:
            self.devices.append(device)
        else:
            logging.warning("Unable to connect to BLE Device : " + deviceAddress)

    def getDevice(self, deviceAddress=None):
        if deviceAddress:
            for device in self.devices:
                if device.address == deviceAddress:
                    return device
            logging.warning("Device not found : " + deviceAddress)
            return None
        else:
            for device in self.devices:
                if device.connected:
                    return device
            logging.warning("No device is connected.")
            return None

    def getEulerAngle(self, device=None):
        if device:
            command = NebCommandPacket(SubSystem.Motion, Commands.Motion.EulerAngle, True)
            device.write(command.stringEncode())
