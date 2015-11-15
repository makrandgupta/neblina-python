#!/usr/bin/env python
# Author: Alexandre Courtemanche (a.courtemanche@motsai.com)

import struct
import binascii

# Error Masks (applies to the subsystem code)
Subsys_ErrMask              =   0x80
# Subsystem codes
Subsys_MotionEngine         =   0x01
Subsys_PowerManagement      =   0x02

# Power Management commands
PowCmd_GetBatteryLevel      =   0x00

# Motion engine commands
MotCmd_Downsample           =   0x01 # Downsampling factor definition
MotCmd_MotionState          =   0x02 # streaming Motion State
MotCmd_IMU_Data             =   0x03 # streaming the 6-axis IMU data
MotCmd_Quaternion           =   0x04 # streaming the quaternion data
MotCmd_EulerAngle           =   0x05 # streaming the Euler angles
MotCmd_ExtForce             =   0x06 # streaming the external force
MotCmd_SetFusionType        =   0x07 # setting the Fusion type to either 6-axis or 9-axis
MotCmd_TrajectoryRecStart   =   0x08 # start recording orientation trajectory
MotCmd_TrajectoryRecStop    =   0x09 # stop recording orientation trajectory
MotCmd_TrajectoryDistance   =   0x0A # calculating the distance from a pre-recorded orientation trajectory
MotCmd_Pedometer            =   0x0B # streaming pedometer data
MotCmd_MAG_Data             =   0x0C # streaming magnetometer data

NeblinaCommandPacketData_fmt = "<B 15s"
class NebCommandData(object):
    """docstring for NebCommandData"""
    def __init__(self, enable):
        self.enable = enable

    def encode(self):
        garbage = ('\000'*15).encode('utf-8')
        commandDataString = struct.pack(NeblinaCommandPacketData_fmt,\
            self.enable, garbage)
        return commandDataString

    def __str__(self):
        return "enable: {0}".format(self.enable)

Neblina_BatteryLevel_fmt = "<h 14s" # Battery Level (%)
class BatteryLevelData(object):
    """docstring for BatteryLevelData"""
    def __init__(self, dataString):
        self.batteryLevel,\
        garbage = struct.unpack( Neblina_BatteryLevel_fmt, dataString )

    def __str__(self):
        return "batteryLevel: {0}%".format(self.batteryLevel)

Neblina_MotionState_fmt = "<I B 11s" # Timestamp, start/stop
class MotionStateData(object):
    """docstring for MotionStateData"""
    def __init__(self, dataString):
        self.timestamp,\
        startStopByte,\
        garbage = struct.unpack( Neblina_MotionState_fmt, dataString )
        self.startStop = (startStopByte == 0)
    def __str__(self):
        return "{0}us: startStop:{1})"\
        .format(self.timestamp,self.startStop)

Neblina_ExternalForce_fmt = "<I 3h 6s" # Timestamp, External force xyz
class ExternalForceData(object):
    """docstring for ExternalForceData"""
    def __init__(self, dataString):
        self.externalForces = [0]*3
        self.timestamp,\
        self.externalForces[0],\
        self.externalForces[1],\
        self.externalForces[2],\
        garbage = struct.unpack( Neblina_ExternalForce_fmt, dataString )

    def __str__(self):
        return "{0}us: externalForces(x,y,z):({1},{2},{3})"\
        .format(self.timestamp,self.externalForces[0],\
            self.externalForces[1], self.externalForces[2])

Neblina_TrajectoryDistance_fmt = "<I 3h 6s" # Timestamp, Euler angle errors
class TrajectoryDistanceData(object):
    """docstring for TrajectoryDistance"""
    def __init__(self, dataString):
        self.eulerAngleErrors = [0]*3

        self.timestamp,\
        self.eulerAngleErrors[0],\
        self.eulerAngleErrors[1],\
        self.eulerAngleErrors[2],\
        garbage = struct.unpack( Neblina_TrajectoryDistance_fmt, dataString )

    def __str__(self):
        return "{0}us: eulerAngleErrors(x,y,z):({1},{2},{3})"\
        .format(self.timestamp,self.eulerAngleErrors[0],\
            self.eulerAngleErrors[1], self.eulerAngleErrors[2])

Neblina_Pedometer_fmt = "<I H B h 7s" # Timestamp, stepCount, stepsPerMinute, walking direction 
class PedometerData(object):
    """docstring for PedometerData"""
    def __init__(self, dataString):
        self.timestamp,self.stepCount,\
        self.stepsPerMinute,\
        self.walkingDirection,\
        garbage = struct.unpack( Neblina_Pedometer_fmt, dataString )
        self.walkingDirection /= 10.0

    def encode(self):
        garbage = ('\000'*7).encode('utf-8')
        packetString = struct.pack(Neblina_Pedometer_fmt, self.timestamp,\
        self.stepCount, self.stepsPerMinute, int(self.walkingDirection*10), garbage)
        return packetString

    def __str__(self):
        return "{0}us: stepCount:{1}, stepsPerMinute:{2}, walkingDirection:{3}"\
        .format(self.timestamp, self.stepCount,\
        self.stepsPerMinute, self.walkingDirection)

Neblina_Quat_t_fmt = "<I 4h 4s"
class QuaternionData(object):
    """docstring for QuaternionData"""
    def __init__(self, dataString):
        self.quaternions = [0]*4
        
        self.timestamp,\
        self.quaternions[0],\
        self.quaternions[1],\
        self.quaternions[2],\
        self.quaternions[3],\
        garbage = struct.unpack( Neblina_Quat_t_fmt, dataString )
        
    def __str__(self):
        return "{0}us: quat0:{1} quat1:{2} quat2:{3} quat3:{4}".format(\
            self.timestamp, self.quaternions[0], self.quaternions[1],\
            self.quaternions[2], self.quaternions[3])

Neblina_IMU_fmt = "<I 3h 3h" # timestamp xyz xyz
class IMUData(object):
    """docstring for IMUData"""
    def __init__(self, dataString):
        self.accel = [0]*3
        self.gyro = [0]*3
        
        self.timestamp, \
        self.accel[0], self.accel[1], self.accel[2],\
        self.gyro[0], self.gyro[1], self.gyro[2]\
         = struct.unpack( Neblina_IMU_fmt, dataString )

    def encode(self):
        packetString = struct.pack( Neblina_IMU_fmt, \
        self.timestamp, self.accel[0], self.accel[1], self.accel[2],\
        self.gyro[0], self.gyro[1], self.gyro[2])
        return packetString

    def __str__(self):
        return "{0}us: accelxyz:({1},{2},{3}) gyroxyz:({4},{5},{6})"\
        .format(self.timestamp,
                self.accel[0], self.accel[1], self.accel[2],
                self.gyro[0], self.gyro[1], self.gyro[2])

Neblina_MAG_fmt = "<I 3h 3h" # timestamp xyz xyz
class MAGData(object):
    """docstring for MAGData"""
    def __init__(self, dataString):
        self.mag = [0]*3
        self.accel = [0]*3
        self.timestamp, \
        self.mag[0], self.mag[1], self.mag[2],\
        self.accel[0], self.accel[1], self.accel[2]\
         = struct.unpack( Neblina_MAG_fmt, dataString )

    def encode(self):
        packetString = struct.pack( Neblina_MAG_fmt, \
        self.timestamp, self.mag[0], self.mag[1], self.mag[2],\
        self.accel[0], self.accel[1], self.accel[2])
        return packetString
    
    def __str__(self):
        return "{0}us: accelxyz:({1},{2},{3}) magxyz:({4},{5},{6})"\
        .format(self.timestamp,
                self.accel[0], self.accel[1], self.accel[2],
                self.mag[0], self.mag[1], self.mag[2])

Neblina_Euler_fmt = "<I 4h 4s" # timestamp yaw, pitch, roll, demo heading
class EulerAngleData(object):
    """docstring for EulerAngleData"""
    def __init__(self, dataString):
        self.timestamp, self.yaw, self.pitch, self.roll, self.demoHeading,\
            garbage = struct.unpack( Neblina_Euler_fmt, dataString )
        self.yaw = self.yaw/10.0
        self.pitch = self.pitch/10.0
        self.roll = self.roll/10.0
        self.demoHeading = self.demoHeading/10.0

    def encode(self):
        garbage = ('\000'*4).encode('utf-8')
        packetString = struct.pack(Neblina_Euler_fmt, self.timestamp,\
         int(self.yaw*10), int(self.pitch*10), int(self.roll*10), int(self.demoHeading*10), garbage)
        return packetString
        
    def __str__(self):
        return "{0}us: yaw/pitch/roll:({1},{2},{3}))"\
        .format(self.timestamp,self.yaw, self.pitch, self.roll)

PowerManagementCommands = {
    PowCmd_GetBatteryLevel      : BatteryLevelData,
}

PowerManagementCommandStrings = {
    PowCmd_GetBatteryLevel      : "BatteryLevelData",
}

MotionCommands = {
    MotCmd_EulerAngle           : EulerAngleData,
    MotCmd_IMU_Data             : IMUData,
    MotCmd_Pedometer            : PedometerData,
    MotCmd_MAG_Data             : MAGData,
    MotCmd_Quaternion           : QuaternionData,
    MotCmd_TrajectoryDistance   : TrajectoryDistanceData,
    MotCmd_ExtForce             : ExternalForceData,
    MotCmd_MotionState          : MotionStateData,
}

MotionCommandsStrings = {
    MotCmd_Downsample           : "Downsample",
    MotCmd_EulerAngle           : "EulerAngle",
    MotCmd_IMU_Data             : "IMU",
    MotCmd_Pedometer            : "Pedometer",
    MotCmd_MAG_Data             : "MAG",
    MotCmd_Quaternion           : "Quaternion",
    MotCmd_TrajectoryDistance   : "TrajectoryDistance",
    MotCmd_ExtForce             : "ExternalForce",
    MotCmd_MotionState          : "MotionState",
}


# Header = 4 bytes
NeblinaPacketHeader_fmt = "<4B"
class NebHeader(object):
    """docstring for NebHeader"""
    def __init__(self, subSystem, commandType, crc, length = 16):
        self.subSystem = subSystem
        self.length = length
        self.crc = crc
        self.command = commandType

    def encode(self):
        headerStringCode = struct.pack(NeblinaPacketHeader_fmt,\
        self.subSystem, self.length, self.crc, self.command)
        return headerStringCode

    def __str__(self):
        stringFormat = "subSystem = {0}, packetLength = {1}, crc = {2}, command = {3}"
        stringDescriptor = stringFormat.format(self.subSystem, self.length,self.crc, \
            MotionCommandsStrings[self.command])
        return stringDescriptor

# Data = 16 bytes
NeblinaPacket_fmt = "<4s 16s"
class NebCommandPacket(object):
    """docstring for NebCommandPacket"""
    def __init__(self, subSystem, commandType, enable, length = 16):
        self.data = NebCommandData(enable)
        # Perform CRC calculation
        crc = crc8(bytearray(self.data.encode()))
        self.header = NebHeader(subSystem, commandType, crc)

    def stringEncode(self):
        headerStringCode = self.header.encode()
        dataStringCode = self.data.encode()
        return headerStringCode+dataStringCode

    def __str__(self):
        stringFormat = "header = [{0}] data = [{1}]"
        stringDescriptor = stringFormat.format(self.header, self.data)
        return stringDescriptor

class NebResponsePacket(object):
    """docstring for NebResponsePacket"""

    @classmethod
    def createMAGResponsePacket(cls, timestamp, mag, accel):
        dataString = struct.pack( Neblina_MAG_fmt, \
        timestamp, int(mag[0]), int(mag[1]), int(mag[2]),\
        int(accel[0]), int(accel[1]), int(accel[2]))
        data = MAGData(dataString)
        # Perform CRC of data bytes
        crc = crc8(bytearray(dataString))
        header = NebHeader(Subsys_MotionEngine, MotCmd_MAG_Data, crc, len(dataString))
        responsePacket = NebResponsePacket(packetString=None, header=header, data=data)
        return responsePacket

    @classmethod
    def createIMUResponsePacket(cls, timestamp, accel, gyro):
        dataString = struct.pack( Neblina_IMU_fmt, \
        timestamp, int(accel[0]), int(accel[1]), int(accel[2]),\
        int(gyro[0]), int(gyro[1]), int(gyro[2]))
        data = IMUData(dataString)
        # Perform CRC of data bytes
        crc = crc8(bytearray(dataString))
        header = NebHeader(Subsys_MotionEngine, MotCmd_IMU_Data, crc, len(dataString))
        responsePacket = NebResponsePacket(packetString=None, header=header, data=data)
        return responsePacket

    @classmethod
    def createEulerAngleResponsePacket(cls, timestamp, yaw, pitch, roll, demoHeading = 0.0):
        # Multiply the euler angle values by 10 to emulate the firmware behavior
        yaw = int(yaw*10)
        pitch = int(pitch*10)
        roll = int(roll*10)
        demoHeading = int(demoHeading*10)
        garbage = '\000\000\000\000'.encode('utf-8')
        dataString = struct.pack( Neblina_Euler_fmt, int(timestamp), yaw, pitch, roll, demoHeading, garbage )
        data = EulerAngleData(dataString)
        # Perform CRC of data bytes
        crc = crc8(bytearray(dataString))
        header = NebHeader(Subsys_MotionEngine, MotCmd_EulerAngle, crc, len(dataString))
        responsePacket = NebResponsePacket(packetString=None, header=header, data=data)
        return responsePacket

    @classmethod
    def createPedometerResponsePacket(cls, timestamp, stepCount, stepsPerMinute, walkingDirection):
        # Multiply the walking direction value by 10 to emulate the firmware behavior
        walkingDirection = int(walkingDirection*10)
        garbage = ('\000'*7).encode('utf-8')
        dataString = struct.pack( Neblina_Pedometer_fmt, timestamp, stepCount,\
         stepsPerMinute, walkingDirection, garbage )
        data = PedometerData(dataString)
        # Perform CRC of data bytes
        crc = crc8(bytearray(dataString))
        header = NebHeader(Subsys_MotionEngine, MotCmd_Pedometer, crc, len(dataString))
        responsePacket = NebResponsePacket(packetString=None, header=header, data=data)
        return responsePacket


    def __init__(self, packetString=None, header=None, data=None):
        if (packetString != None):
            # Sanity check
            packetStringLength = len(packetString)
            if(packetStringLength < 5):
                raise InvalidPacketFormatError(\
                    'Impossible packet, must have a data payload of at least 1 byte but got {0}')\
                    .format(packetStringLength)
            elif(packetStringLength != 20):
                raise NotImplementedError(\
                    'Packets are not supposed to be anything other than 20 bytes for now but got {0}'\
                    .format(packetStringLength))

            # The string can either be bytes or an actual string
            # Force it to a string if that is the case.
#            if (type(packetString) == str):
#		print str
#                packetString = packetString.encode('iso-8859-1')

            # Extract the header information
            self.headerLength = 4
            headerString = packetString[:self.headerLength]
            subSystem, packetLength, crc, command \
            =  struct.unpack(NeblinaPacketHeader_fmt, headerString)
            
            self.header = NebHeader( subSystem, command, crc, packetLength )

            # Extract the data substring
            dataString = packetString[self.headerLength:self.headerLength+packetLength]

            # Perform CRC of data bytes
            calculatedCRC = crc8(bytearray(dataString))
            if (calculatedCRC != self.header.crc):
                raise CRCError(calculatedCRC, self.header.crc)
                # raise Exception('Invalid CRC. expected '+str(self.crc)+ 'but got '+crc8(bytearray(dataString)) )

            # Build the data object based on the subsystem and command.
            if subSystem == Subsys_PowerManagement:
                self.data = PowerManagementCommands[self.header.command](dataString)
            elif subSystem == Subsys_MotionEngine:
                self.data = MotionCommands[self.header.command](dataString)
            else:
                raise InvalidPacketFormatError('Invalid subsystem.')
        elif(header != None and data != None):
            self.header = header
            self.data = data

    def stringEncode(self):
        headerStringCode = self.header.encode()
        dataStringCode = self.data.encode()
        return headerStringCode+dataStringCode

    def __str__(self):
        stringFormat = "header = [{0}] data = [{1}]"
        stringDescriptor = stringFormat.format(self.header, self.data)
        return stringDescriptor

class CRCError(Exception):
    """docstring for CRCError"""
    def __init__(self, expected, actual):
        self.expected = expected
        self.actual = actual
        # super(CRCError, self).__init__(self, 'Invalid CRC. expected {0} but got {1}'\
        #     .format(expected, actual))

class InvalidPacketFormatError(Exception):
    """docstring for InvalidPacketFormatError"""
    def __init__(self, errorString):
        super(InvalidPacketFormatError, self).__init__(errorString)

def crc8(bytes):
    crc = 0
    for byte in bytes:
        ee = (crc) ^ (byte)
        ff = (ee) ^ (ee>>4) ^ (ee>>7)
        crc = ((ff<<1)%256) ^ ((ff<<4) % 256)
    return crc
