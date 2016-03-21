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

#from neblina import *
from neblinaData import *
from neblinaError import *
from neblinaHeader import NebHeader
from neblinaUtilities import NebUtilities as nebUtilities

###################################################################################

# Dictionaries containing the data constructors for response packets
# BlankData means a response data object does not need to be implemented
# -------------------------------------------------------------------
PlaceholderDataConstructors = {
    0: BlankData,
    1: BlankData,
    2: BlankData,
    3: BlankData,
    4: BlankData,
    5: BlankData,
    6: BlankData,
    7: BlankData,
    8: BlankData,
    9: BlankData,
    10: BlankData,
}

DebugResponses = {
    0: BlankData,
    Commands.Debug.SetInterface: BlankData,
    Commands.Debug.MotAndFlashRecState: MotAndFlashRecStateData,
    Commands.Debug.StartUnitTestMotion: BlankData,
    Commands.Debug.UnitTestMotionData: UnitTestMotionData,
    Commands.Debug.FWVersions: FWVersionsData

}

StorageResponses = {
    Commands.Storage.EraseAll: BlankData,
    Commands.Storage.Record: FlashSessionData,
    Commands.Storage.Playback: FlashSessionData,
    Commands.Storage.NumSessions: FlashNumSessionsData,
    Commands.Storage.SessionInfo: FlashSessionInfoData,
}

PowerManagementResponses = {
    Commands.Power.GetBatteryLevel: BatteryLevelData,
    Commands.Power.GetTemperature: TemperatureData,
}

MotionResponses = {
    Commands.Motion.Downsample: BlankData,  # Downsampling factor definition
    Commands.Motion.MotionState: MotionStateData,  # streaming Motion State
    Commands.Motion.IMU: IMUData.decode,  # streaming the 6-axis IMU data
    Commands.Motion.Quaternion: QuaternionData,  # streaming the quaternion data
    Commands.Motion.EulerAngle: EulerAngleData,  # streaming the Euler angles
    Commands.Motion.ExtForce: ExternalForceData,  # streaming the external force
    Commands.Motion.SetFusionType: BlankData,  # setting the Fusion type to either 6-axis or 9-axis
    Commands.Motion.TrajectoryRecStartStop: TrajectoryDistanceData,  # start recording orientation trajectory
    Commands.Motion.TrajectoryInfo: TrajectoryDistanceData,  # calculating the distance from an orientation trajectory
    Commands.Motion.Pedometer: PedometerData,  # streaming pedometer data
    Commands.Motion.MAG: MAGData.decode,  # streaming magnetometer data
    Commands.Motion.SittingStanding: BlankData,  # streaming sitting standing
    Commands.Motion.AccRange: BlankData,  # set accelerometer range
    Commands.Motion.DisableStreaming: BlankData,  # disable everything that is currently being streamed
    Commands.Motion.ResetTimeStamp: BlankData,
    Commands.Motion.FingerGesture: FingerGestureData,  # streaming finger gesture data
    Commands.Motion.RotationInfo: RotationData  # streaming rotation info data
}

EEPROMResponses = {
    Commands.EEPROM.Read: EEPROMReadData,
    Commands.EEPROM.Write: EEPROMReadData,
}

LEDResponses = {
    Commands.LED.SetVal: BlankData,
    Commands.LED.GetVal: LEDGetValData,
}

# Dictionary containing the dictionary of data object constructors
ResponsePacketDataConstructors = {
    SubSystem.Debug: DebugResponses,
    SubSystem.Motion: MotionResponses,
    SubSystem.Power: PowerManagementResponses,
    SubSystem.DigitalIO: PlaceholderDataConstructors,
    SubSystem.LED: LEDResponses,
    SubSystem.ADC: PlaceholderDataConstructors,
    SubSystem.DAC: PlaceholderDataConstructors,
    SubSystem.I2C: PlaceholderDataConstructors,
    SubSystem.SPI: PlaceholderDataConstructors,
    SubSystem.Firmware: PlaceholderDataConstructors,
    SubSystem.Crypto: PlaceholderDataConstructors,
    SubSystem.Storage: StorageResponses,
    SubSystem.EEPROM: EEPROMResponses,
}


###################################################################################


class NebResponsePacket(object):
    """docstring for NebResponsePacket"""

    @staticmethod
    def createResponsePacket(self, subSystem, commands, data, dataString):
        crc = nebUtilities.crc8(bytearray(dataString))
        header = NebHeader(subSystem, False, commands, crc, len(dataString))
        responsePacket = NebResponsePacket(packetString=None, header=header, data=data, checkCRC=False)
        responsePacket.header.crc = nebUtilities.genNebCRC8(bytearray(responsePacket.stringEncode()))
        return responsePacket

    @classmethod
    def createMAGResponsePacket(cls, timestamp, mag, accel):
        data = MAGData(timestamp, mag, accel)
        dataString = data.encode()
        return cls.createResponsePacket(cls, SubSystem.Motion, Commands.Motion.MAG, data, dataString)

    @classmethod
    def createIMUResponsePacket(cls, timestamp, accel, gyro):
        data = IMUData(timestamp, accel, gyro)
        dataString = data.encode()
        return cls.createResponsePacket(cls, SubSystem.Motion, Commands.Motion.IMU, data, dataString)

    @classmethod
    def createEulerAngleResponsePacket(cls, timestamp, yaw, pitch, roll, demoHeading=0.0):
        # Multiply the euler angle values by 10 to emulate the firmware behavior
        yaw = int(yaw * 10)
        pitch = int(pitch * 10)
        roll = int(roll * 10)
        demoHeading = int(demoHeading * 10)
        garbage = '\000\000\000\000'.encode('utf-8')
        dataString = struct.pack(Formatting.Data.Euler, int(timestamp), yaw, pitch, roll, demoHeading, garbage)
        data = EulerAngleData(dataString)
        return cls.createResponsePacket(cls, SubSystem.Motion, Commands.Motion.EulerAngle, data, dataString)

    @classmethod
    def createPedometerResponsePacket(cls, timestamp, stepCount, stepsPerMinute, walkingDirection):
        # Multiply the walking direction value by 10 to emulate the firmware behavior
        walkingDirection = int(walkingDirection * 10)
        garbage = ('\000' * 7).encode('utf-8')
        dataString = struct.pack(Formatting.Data.Pedometer, timestamp, stepCount, \
                                 stepsPerMinute, walkingDirection, garbage)
        data = PedometerData(dataString)
        return cls.createResponsePacket(cls, SubSystem.Motion, Commands.Motion.Pedometer, data, dataString)

    @classmethod
    def createRotationResponsePacket(cls, timestamp, rotationCount, rpm):
        garbage = ('\000' * 6).encode('utf-8')
        dataString = struct.pack(Formatting.Data.RotationInfo, timestamp, rotationCount, \
                                 rpm, garbage)
        data = RotationData(dataString)
        return cls.createResponsePacket(cls, SubSystem.Motion, Commands.Motion.RotationInfo, data, dataString)

    def __init__(self, packetString=None, header=None, data=None, checkCRC=True):
        if (packetString != None):
            # Sanity check
            packetStringLength = len(packetString)
            if (packetStringLength < 5):
                raise InvalidPacketFormatError( \
                    'Impossible packet, must have a packet of at least 5 bytes but got {0}' \
                        .format(packetStringLength))

            # The string can either be bytes or an actual string
            # Force it to a string if that is the case.
            if (type(packetString) == str):
                packetString = packetString.encode('iso-8859-1')

            # Extract the header information
            self.headerLength = 4
            headerString = packetString[:self.headerLength]
            ctrlByte, packetLength, crc, command \
                = struct.unpack(Formatting.CommandData.Header, headerString)

            # Extract the value from the subsystem byte
            subSystem = ctrlByte & BitMask.SubSystem

            # Check if the response byte is an acknowledge
            packetTypeCode = ctrlByte & BitMask.PacketType
            packetType = packetTypeCode >> BitPosition.PacketType

            # See if the packet is a response or a command packet
            if (packetType == PacketType.Command):
                raise InvalidPacketFormatError('Cannot create a response packet with the string of a command packet.')

            self.header = NebHeader(subSystem, packetType, command, crc, packetLength)

            # Extract the data substring
            dataString = packetString[self.headerLength:self.headerLength + packetLength]

            # Perform CRC of data bytes
            if (checkCRC):
                calculatedCRC = nebUtilities.genNebCRC8(bytearray(packetString))
                if calculatedCRC != self.header.crc:
                    raise CRCError(calculatedCRC, self.header.crc)

            # Build the data object based on the subsystem and command.
            self.data = ResponsePacketDataConstructors[subSystem][self.header.command](dataString)

        elif (header != None and data != None):
            self.header = header
            self.data = data

    def stringEncode(self):
        headerStringCode = self.header.encode()
        dataStringCode = self.data.encode()
        return headerStringCode + dataStringCode

    def __str__(self):
        stringFormat = "header = [{0}] data = [{1}]"
        stringDescriptor = stringFormat.format(self.header, self.data)
        return stringDescriptor

        ###################################################################################
