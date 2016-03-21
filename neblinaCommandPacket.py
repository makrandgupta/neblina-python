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

from neblina import *
from neblinaCommandData import *
from neblinaHeader import NebHeader
from neblinaUtilities import NebUtilities as nebUtilities

###################################################################################


class NebCommandPacket(object):
    """docstring for NebCommandPacket"""
    def __init__(self, subSystem, commandType, enable=True, **kwargs):
        # Logic for determining which type of command packet it is based on the header
        if subSystem == SubSystem.Debug and commandType == Commands.Debug.UnitTestMotionData:
            self.data = NebUnitTestMotionDataCommandData(kwargs['timestamp'], kwargs['accel'],\
                                                         kwargs['gyro'], kwargs['mag'])
        elif subSystem == SubSystem.Motion and commandType == Commands.Motion.Downsample:
            self.data = NebDownsampleCommandData(enable)
        elif subSystem == SubSystem.Motion and commandType == Commands.Motion.AccRange:
            self.data = NebAccRangeCommandData(enable)
        elif subSystem == SubSystem.Storage and commandType == Commands.Storage.Playback :
            self.data = NebFlashPlaybackCommandData(enable, kwargs['sessionID'])
        elif subSystem == SubSystem.Storage and commandType == Commands.Storage.SessionInfo:
            self.data = NebFlashSessionInfoCommandData(kwargs['sessionID'])
        elif subSystem == SubSystem.EEPROM:
            if commandType == Commands.EEPROM.Read:
                self.data = NebEEPROMCommandData(False, kwargs['pageNumber'])
            elif commandType == Commands.EEPROM.Write :
                self.data = NebEEPROMCommandData(True, kwargs['pageNumber'], kwargs['dataBytes'])
        elif subSystem == SubSystem.LED and commandType == Commands.LED.SetVal:
            self.data = NebSetLEDCommandData(kwargs['ledValueTupleList'])
        elif subSystem == SubSystem.LED and commandType == Commands.LED.GetVal:
            self.data = NebGetLEDCommandData(kwargs['ledIndices'])
        else:
            self.data = NebCommandData(enable)
        self.header = NebHeader(subSystem, PacketType.Command, commandType, length=len(self.data.encode()))
        # Perform CRC calculation
        self.header.crc = nebUtilities.crc8(bytearray(self.header.encode() + self.data.encode()))

    def stringEncode(self):
        headerStringCode = self.header.encode()
        dataStringCode = self.data.encode()
        return headerStringCode+dataStringCode

    def __str__(self):
        stringFormat = "header = [{0}] data = [{1}]"
        stringDescriptor = stringFormat.format(self.header, self.data)
        return stringDescriptor

###################################################################################
