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

import struct

from neblina import *

###################################################################################


class NebHeader(object):
    """ The header section consists of four bytes.
        Byte 0: Control Byte (PKT_TYPE/SUB)
        Byte 1: Data length
        Byte 2: CRC
        Byte 3: Command type

        The Control Byte contains the Packet type code and the subsystem code
        CtrlByte(7:5) = PacketType
        CtrlByte(4:0) = Subsytem Code
    """
    def __init__(self, subSystem, packetType, commandType, crc=255, length=16 ):
        self.subSystem = subSystem
        self.length = length
        self.crc = crc
        self.command = commandType
        self.packetType = packetType

    def __str__(self):
        stringFormat = "packetType = {0}, subSystem = {1}, packetLength = {2}, crc = {3}, command = {4}"
        commandString = CommandStrings[(self.subSystem, self.command)]
        stringDescriptor = stringFormat.format(PacketType.String[self.packetType], \
             self.subSystem, self.length,self.crc, commandString)
        return stringDescriptor

    def encode(self):
        packedCtrlByte = self.subSystem
        if self.packetType:
            packedCtrlByte |= (self.packetType << BitPosition.PacketType)
        headerStringCode = struct.pack(Formatting.CommandData.Header,\
        packedCtrlByte, self.length, self.crc, self.command)
        return headerStringCode

###################################################################################