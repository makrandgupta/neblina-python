#!/usr/bin/env python
# Neblina Data Structures
# (C) 2015 Motsai Research Inc.
# Author: Alexandre Courtemanche (a.courtemanche@motsai.com)

import struct
import binascii

# Control Byte Masks
Subsys_BitMask              =   0x1F
PacketType_BitMask          =   0xE0
PacketType_BitPosition      =   5

# Packet Type codes
PacketType_RegularResponse  =   0x00
PacketType_Ack              =   0x01
PacketType_Command          =   0x02
PacketType_ErrorLogResp     =   0x04
PacketType_ErrorLogCmd      =   0x06

# Subsystem codes
Subsys_Debug                =   0x00
Subsys_MotionEngine         =   0x01
Subsys_PowerManagement      =   0x02
Subsys_DigitalIO            =   0x03
Subsys_LED                  =   0x04
Subsys_ADC                  =   0x05
Subsys_DAC                  =   0x06
Subsys_I2C                  =   0x07
Subsys_SPI                  =   0x08
Subsys_FirmwareManagement   =   0x09
Subsys_Crypto               =   0x0A
Subsys_Storage              =   0x0B
Subsys_EEPROM               =   0x0C

PacketTypeStrings = {
    PacketType_RegularResponse      : "RegularResponse",
    PacketType_Ack                  : "Acknowledge",
    PacketType_Command              : "Command",
    PacketType_ErrorLogResp         : "Error Response",
    PacketType_ErrorLogCmd          : "Error Command"
}

# Debug Commands
DebugCmd_SetInterface           =   0x01
DebugCmd_MotAndFlashRecState    =   0x02
DebugCmd_StartUnitTestMotion    =   0x03
DebugCmd_UnitTestMotionData     =   0x04

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
MotCmd_SittingStanding      =   0x0D # streaming sitting standing
MotCmd_AccRange             =   0x0E # set accelerometer range
MotCmd_DisableStreaming     =   0x0F # disable everything that is currently being streamed
MotCmd_ResetTimeStamp       =   0x10 # Reset timestamp

# Storage commands
StorageCmd_EraseAll         =   0x01 # Full-erase for the on-chip NOR flash memory
StorageCmd_Record           =   0x02 # Either start a new recording session, or close the currently open one
StorageCmd_Playback         =   0x03 # Either open a previously recorded session for playback or close the one that is currently open and being played

# EEPROM Command
EEPROMCmd_Read              =   0x01 # Read a page
EEPROMCmd_Write             =   0x02 # Write to a page

# Digital IO Commands
DigitalIOCmd_SetConfig      =   0x01
DigitalIOCmd_GetConfig      =   0x02
DigitalIOCmd_SetValue       =   0x03
DigitalIOCmd_GetValue       =   0x04
DigitalIOCmd_NotifySet      =   0x05
DigitalIOCmd_NotifyEvent    =   0x06

# Firmware Information Commands
FirmwareManagementCmd_Main  =   0x01
FirmwareManagementCmd_BLE   =   0x02

# LED Information Commands
LEDCmd_Write                =   0x01
LEDCmd_Read                 =   0x02
LEDCmd_Config               =   0x03

# Dictionary containing the string descriptors of each command
CommandStrings = {
    (Subsys_Debug, DebugCmd_SetInterface)                   :   'Set Interface',
    (Subsys_Debug, DebugCmd_MotAndFlashRecState)            :   'Check Motion and Flash Recorder States',
    (Subsys_Debug, DebugCmd_StartUnitTestMotion)            :   'Enable/Disable Unit Test Motion',
    (Subsys_Debug, DebugCmd_UnitTestMotionData)             :   'Unit Test Data',
    (Subsys_MotionEngine, MotCmd_Downsample)                :   'Downsample',
    (Subsys_MotionEngine, MotCmd_MotionState)               :   'MotionState',
    (Subsys_MotionEngine, MotCmd_IMU_Data)                  :   'IMU Data',
    (Subsys_MotionEngine, MotCmd_Quaternion)                :   'Quaternion',
    (Subsys_MotionEngine, MotCmd_EulerAngle)                :   'Euler Angle',
    (Subsys_MotionEngine, MotCmd_ExtForce)                  :   'ExtForce',
    (Subsys_MotionEngine, MotCmd_SetFusionType)             :   'SetFusionType',
    (Subsys_MotionEngine, MotCmd_TrajectoryRecStart)        :   'Trajectory Record Start',
    (Subsys_MotionEngine, MotCmd_TrajectoryRecStop)         :   'Trajectory Record Stop',
    (Subsys_MotionEngine, MotCmd_TrajectoryDistance)        :   'Trajectory Distance',
    (Subsys_MotionEngine, MotCmd_Pedometer)                 :   'Pedometer',
    (Subsys_MotionEngine, MotCmd_MAG_Data)                  :   'MAG Data',
    (Subsys_MotionEngine, MotCmd_SittingStanding)           :   'Sitting-Standing',
    (Subsys_MotionEngine, MotCmd_AccRange)                  :   'AccRange',
    (Subsys_MotionEngine, MotCmd_DisableStreaming)          :   'Disable Streaming',
    (Subsys_MotionEngine, MotCmd_ResetTimeStamp)            :   'Reset Timestamp',
    (Subsys_PowerManagement, PowCmd_GetBatteryLevel)        :   'Battery Level',
    (Subsys_DigitalIO, DigitalIOCmd_SetConfig)              :   'Set Config',
    (Subsys_DigitalIO, DigitalIOCmd_GetConfig)              :   'Get Config',
    (Subsys_DigitalIO, DigitalIOCmd_SetValue)               :   'Set Value',
    (Subsys_DigitalIO, DigitalIOCmd_GetValue)               :   'Get Value',
    (Subsys_DigitalIO, DigitalIOCmd_NotifySet)              :   'Notify Set',
    (Subsys_DigitalIO, DigitalIOCmd_NotifyEvent)            :   'Notify Event',
    (Subsys_LED, LEDCmd_Write)                              :   'LED Write',
    (Subsys_LED, LEDCmd_Read)                               :   'LED Read',
    (Subsys_LED, LEDCmd_Config)                             :   'LED Config',
    (Subsys_ADC, 0)                                         :   'ADC Command',
    (Subsys_DAC, 0)                                         :   'DAC Command',
    (Subsys_I2C, 0)                                         :   'I2C Command',
    (Subsys_SPI, 0)                                         :   'SPI Command',
    (Subsys_FirmwareManagement, FirmwareManagementCmd_Main) :   'Main Firmware',
    (Subsys_FirmwareManagement, FirmwareManagementCmd_BLE)  :   'Nordic Firmware',
    (Subsys_Crypto, 0)                                      :   'Crypto Command',
    (Subsys_Storage, StorageCmd_EraseAll)                   :   'Erase All',
    (Subsys_Storage, StorageCmd_Record)                     :   'Record',
    (Subsys_Storage, StorageCmd_Playback)                   :   'Playback',
    (Subsys_EEPROM, EEPROMCmd_Read)                         :   'Read',
    (Subsys_EEPROM, EEPROMCmd_Write)                        :   'Write',
}

Neblina_CommandPacketData_fmt = "<I B 11s" # Timestamp (unused for now), enable/disable
class NebCommandData(object):
    """docstring for NebCommandData"""
    def __init__(self, enable):
        self.enable = enable
        self.timestamp = 0 # Not really used for now

    def encode(self):
        garbage = ('\000'*11).encode('utf-8')
        commandDataString = struct.pack(Neblina_CommandPacketData_fmt,\
            self.timestamp, self.enable, garbage)
        return commandDataString

    def __str__(self):
        return "enable: {0}".format(self.enable)

class BlankData(object):
    """docstring for BlankData
        This object is for packet data 
        containing no meaningful info in it.
    """
    def __init__(self, dataString):
        self.blankBytes = struct.unpack( "16s", dataString )
    def __str__(self):
        return '{0}'.format(self.blankBytes)

Neblina_FlashSession_fmt = "<I B H 9s" # Timestamp, open/close, session ID
class NebFlashPlaybackCommandData(object):
    """docstring for MotionStateData"""
    def __init__(self, openClose, sessionID):
        self.openClose = openClose
        self.sessionID = sessionID
    def encode(self):
        garbage = ('\000'*9).encode('utf-8')
        timestamp = 0
        if self.openClose == 1:
            pass
        openCloseVal = 1 if self.openClose else 0
        commandDataString = struct.pack(Neblina_FlashSession_fmt,\
            timestamp, openCloseVal, self.sessionID, garbage)
        return commandDataString
    def __str__(self):
        openCloseString = 'open' if self.openClose else 'close'
        return "Flash Command Session {0}: {1}"\
        .format(self.sessionID, openCloseString)

# Special 26 byte packet
Neblina_UnitTestMotionCommandData_fmt = "<I 3h 3h 3h" # Timestamp, accel, gyro, mag
class NebUnitTestMotionDataCommandData(object):
    """docstring for NebUnitTestMotionDataCommandData"""
    def __init__(self, timestamp, accel, gyro, mag):
        self.timestamp = timestamp
        self.accel = accel
        self.gyro = gyro
        self.mag = mag
    def encode(self):
        commandDataString = struct.pack(Neblina_UnitTestMotionCommandData_fmt,\
            self.timestamp, self.accel[0], self.accel[1], self.accel[2],\
            self.gyro[0], self.gyro[1], self.gyro[2],\
            self.mag[0], self.mag[1], self.mag[2])
        return commandDataString

Neblina_AccRangeCommandPacketData_fmt = "<I H 10s" # Timestamp (unused for now), downsample factor
class NebAccRangeCommandData(NebCommandData):
    """docstring for NebAccRangeCommandData"""
    rangeCodes = {2:0x00, 4:0x01, 8:0x02, 16:0x03}

    def encode(self):
        garbage = ('\000'*10).encode('utf-8')
        rangeCode = NebAccRangeCommandData.rangeCodes[self.enable]
        commandDataString = struct.pack(Neblina_AccRangeCommandPacketData_fmt,\
            self.timestamp, rangeCode, garbage)
        return commandDataString

Neblina_DownsampleCommandPacketData_fmt = "<I H 10s" # Timestamp (unused for now), downsample factor
class NebDownsampleCommandData(NebCommandData):
    """docstring for NebDownsampleCommandData"""

    def encode(self):
        garbage = ('\000'*10).encode('utf-8')
        commandDataString = struct.pack(Neblina_DownsampleCommandPacketData_fmt,\
            self.timestamp, self.enable, garbage)
        return commandDataString

Neblina_EEPROMCommandPacketData_fmt = "<H 8s 6s" # Page number, 8 bytes R/W Data
class NebEEPROMCommandData(object):
    """docstring for NebEEPROMCommandData"""
    def __init__(self, readWrite, pageNumber, dataBytes=b'00'*8):
        self.readWrite = readWrite # read = False, write = True
        self.pageNumber = pageNumber
        self.dataBytes = dataBytes

    def encode(self):
        garbage = b'00'*6
        commandDataString = struct.pack(Neblina_EEPROMCommandPacketData_fmt,\
            self.pageNumber, self.dataBytes, garbage)
        return commandDataString

Neblina_MotionAndFlash_fmt = "<I 4s B 7s" # Timestamp (unused for now), downsample factor
class MotAndFlashRecStateData(object):
    """docstring for NebMotAndFlashRecStateData"""

    recorderStatusStrings = {
        0:"Off",
        1:"Recording",
        2:"Playback",
    }

    def __init__(self, dataString):
        self.timestamp, \
        motionEngineStatusBytes,\
        self.recorderStatus,\
        garbage = struct.unpack( Neblina_MotionAndFlash_fmt, dataString )

        # Extract motion engine state
        self.distance = ((motionEngineStatusBytes[0]  & 0x01) == 1)
        self.force = (((motionEngineStatusBytes[0] & 0x02 ) >> 1) == 1)
        self.euler = (((motionEngineStatusBytes[0] & 0x04 ) >> 2) == 1)
        self.quaternion = (((motionEngineStatusBytes[0] & 0x08 ) >> 3) == 1)
        self.imuData = (((motionEngineStatusBytes[0] & 0x10 ) >> 4) == 1)
        self.motion = (((motionEngineStatusBytes[0] & 0x20 ) >> 5) == 1)
        self.steps = (((motionEngineStatusBytes[0] & 0x40 ) >> 6) == 1)
        self.magData = (((motionEngineStatusBytes[0] & 0x80 ) >> 7) == 1)
        self.sitStand = ((motionEngineStatusBytes[1] & 0x01) == 1)

    def __str__(self):
        return "Distance: {0}, Force:{1}, Euler:{2}, Quaternion:{3}, IMUData:{4}, Motion:{5}, Steps:{6}, MAGData:{7}, SitStand:{8}, RecorderStatus:{9}"\
        .format(self.distance, self.force, self.euler, self.quaternion,\
                            self.imuData, self.motion, self.steps, self.magData,\
                            self.sitStand,\
                            MotAndFlashRecStateData.recorderStatusStrings[self.recorderStatus])

Neblina_EEPROMRead_fmt = "<H 8s 6s" # Page number, 8 bytes Read Data
class EEPROMReadData(object):
    """docstring for EEPROMData"""
    def __init__(self, dataString):
        self.pageNumber, \
        self.dataBytes,\
        garbage = struct.unpack( Neblina_EEPROMRead_fmt, dataString )

    def __str__(self):
        return "Page# {0} Data Bytes:{1} ".format(self.pageNumber, self.dataBytes)

Neblina_BatteryLevel_fmt = "<I H 10s" # Battery Level (%)
class BatteryLevelData(object):
    """docstring for BatteryLevelData"""
    def __init__(self, dataString):
        # timestamp = 0
        timestamp, \
        self.batteryLevel,\
        garbage = struct.unpack( Neblina_BatteryLevel_fmt, dataString )
        self.batteryLevel = self.batteryLevel/10

    def __str__(self):
        return "batteryLevel: {0}%".format(self.batteryLevel)

# Neblina_FlashSession_fmt = "<I B H 9s" # Timestamp, open/close, session ID
class FlashSessionData(object):
    """docstring for MotionStateData"""
    def __init__(self, dataString):
        timestamp,\
        openCloseByte,\
        self.sessionID,\
        garbage = struct.unpack( Neblina_FlashSession_fmt, dataString )
        # open = True, close = False
        self.openClose = (openCloseByte == 1)
    def __str__(self):
        openCloseString = 'open' if self.openClose else 'close'
        return "Session {0}: {1}"\
        .format(self.sessionID, openCloseString)

# Special 70 byte packet
Neblina_UnitTestMotionData_fmt = "<B 3h 3h 3h 4h 3h 3h 3h H B I I h B I I"
# motion, imu+mag, quaternion, euler, force, error, motion track, motion track progress, timestamp, stepCount, walkingDirection, sitStand
class UnitTestMotionData(object):
    motionStrings = {
        0: "No Change",
        1: "Stops Moving",
        2: "Starts Moving",
    }
    """docstring for NebUnitTestMotionDataCommandData"""
    def __init__(self, dataString):
        self.accel = [0]*3
        self.gyro = [0]*3
        self.mag = [0]*3
        self.quaternions = [0]*4
        self.eulerAngleErrors = [0]*3
        self.externalForces = [0]*3
        self.startStop,\
        self.accel[0], self.accel[1], self.accel[2],\
        self.gyro[0], self.gyro[1], self.gyro[2],\
        self.mag[0], self.mag[1], self.mag[2],\
        self.quaternions[0], self.quaternions[1],\
        self.quaternions[2], self.quaternions[3],\
        self.yaw, self.pitch, self.roll,\
        self.externalForces[0],\
        self.externalForces[1],\
        self.externalForces[2],\
        self.eulerAngleErrors[0],\
        self.eulerAngleErrors[1],\
        self.eulerAngleErrors[2],\
        self.motionTrack, self.motionTrackProgress,\
        self.timestamp, self.stepCount,\
        self.walkingDirection,\
        self.sitStand, self.sitTime, self.standTime,\
        = struct.unpack(Neblina_UnitTestMotionData_fmt, dataString)
        

    def __str__(self):
        return "Motion: {0} \n\
        accelxyz:({1},{2},{3}) gyroxyz:({4},{5},{6}) \
        magxyz: ({7}, {8}, {9}),\n\
        quat0:{10} quat1:{11} quat2:{12} quat3:{13} \n\
        yaw/pitch/roll:({14},{15},{16})) \n\
        externalForces(x,y,z):({17},{18},{19}) \n\
        eulerAngleErrors(x,y,z):({20},{21},{22}) \n\
        motionTrackCounter: {24} \
        motionTrackProgress: {25} \n\
        timestamp: {26} \n\
        steps: {27} \
        direction: {28} \n\
        sitStand: {29}, sitTime:{30}, standTime:{31}"\
        .format(Neblina_UnitTestMotionData_fmt,\
        UnitTestMotionData.motionStrings[self.startStop],\
        self.startStop,\
        self.accel[0], self.accel[1], self.accel[2],\
        self.gyro[0], self.gyro[1], self.gyro[2],\
        self.mag[0], self.mag[1], self.mag[2],\
        self.quaternions[0], self.quaternions[1],\
        self.quaternions[2], self.quaternions[3],\
        self.yaw, self.pitch, self.roll,\
        self.externalForces[0],\
        self.externalForces[1],\
        self.externalForces[2],\
        self.eulerAngleErrors[0],\
        self.eulerAngleErrors[1],\
        self.eulerAngleErrors[2],\
        self.motionTrack, self.motionTrackProgress,\
        self.timestamp, self.stepCount,\
        self.walkingDirection,\
        self.sitStand, self.sitTime, self.standTime)

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

    def encode(self):
        garbage = ('\000'*4).encode('utf-8')
        packetString = struct.pack(Neblina_Quat_t_fmt, self.timestamp,\
        self.quaternions[0], self.quaternions[1],\
        self.quaternions[2], self.quaternions[3], garbage)
        return packetString
    
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


# Dictionaries containing the data constructors for response packets
# BlankData means a response data object does not need to be implemented
# -------------------------------------------------------------------
PlaceholderDataConstructors = {
    0   :   BlankData,
    1   :   BlankData,
    2   :   BlankData,
    3   :   BlankData,
    4   :   BlankData,
    5   :   BlankData,
    6   :   BlankData,
    7   :   BlankData,
    8   :   BlankData,
    9   :   BlankData,
    10   :   BlankData,
}

DebugResponses = {
    0                               : BlankData,
    DebugCmd_SetInterface           : BlankData,
    DebugCmd_MotAndFlashRecState    : MotAndFlashRecStateData,
    DebugCmd_StartUnitTestMotion    : BlankData,
    DebugCmd_UnitTestMotionData     : UnitTestMotionData

}

StorageResponses = {
    StorageCmd_EraseAll         : BlankData,
    StorageCmd_Record           : FlashSessionData,
    StorageCmd_Playback         : FlashSessionData
}

PowerManagementResponses = {
    PowCmd_GetBatteryLevel      : BatteryLevelData,
}

MotionResponses = {
    MotCmd_Downsample           : BlankData,              # Downsampling factor definition
    MotCmd_MotionState          : MotionStateData,        # streaming Motion State
    MotCmd_IMU_Data             : IMUData,                # streaming the 6-axis IMU data
    MotCmd_Quaternion           : QuaternionData,         # streaming the quaternion data
    MotCmd_EulerAngle           : EulerAngleData,         # streaming the Euler angles
    MotCmd_ExtForce             : ExternalForceData,      # streaming the external force
    MotCmd_SetFusionType        : BlankData,              # setting the Fusion type to either 6-axis or 9-axis
    MotCmd_TrajectoryRecStart   : TrajectoryDistanceData, # start recording orientation trajectory
    MotCmd_TrajectoryRecStop    : TrajectoryDistanceData, # stop recording orientation trajectory
    MotCmd_TrajectoryDistance   : TrajectoryDistanceData, # calculating the distance from a pre-recorded orientation trajectory
    MotCmd_Pedometer            : PedometerData,          # streaming pedometer data
    MotCmd_MAG_Data             : MAGData,                # streaming magnetometer data
    MotCmd_SittingStanding      : BlankData,              # streaming sitting standing
    MotCmd_AccRange             : BlankData,              # set accelerometer range
    MotCmd_DisableStreaming     : BlankData,              # disable everything that is currently being streamed
    MotCmd_ResetTimeStamp       : BlankData
}

EEPROMResponses = {
    EEPROMCmd_Read              : EEPROMReadData,
    EEPROMCmd_Write             : EEPROMReadData,
}

# Dictionary containing the dictionary of data object constructors
ResponsePacketDataConstructors = {
    Subsys_Debug                :   DebugResponses,
    Subsys_MotionEngine         :   MotionResponses,
    Subsys_PowerManagement      :   PowerManagementResponses,
    Subsys_DigitalIO            :   PlaceholderDataConstructors,
    Subsys_LED                  :   PlaceholderDataConstructors,
    Subsys_ADC                  :   PlaceholderDataConstructors,
    Subsys_DAC                  :   PlaceholderDataConstructors,
    Subsys_I2C                  :   PlaceholderDataConstructors,
    Subsys_SPI                  :   PlaceholderDataConstructors,
    Subsys_FirmwareManagement   :   PlaceholderDataConstructors,
    Subsys_Crypto               :   PlaceholderDataConstructors,
    Subsys_Storage              :   StorageResponses,
    Subsys_EEPROM               :   EEPROMResponses,
}
# -------------------------------------------------------------------


# Header = 4 bytes
Neblina_PacketHeader_fmt = "<4B"
class NebHeader(object):
    """ docstring for NebHeader
        The header section consists of four bytes.
        Byte 0: Control Byte (PKT_TYPE/SUB)
        Byte 1: Data length
        Byte 2: CRC
        Byte 3: Command type

        The Control Byte contains the Packet type code and the subsystem code
        CtrlByte(7:5) = PacketType
        CtrlByte(4:0) = Subsytem Code
    """
    def __init__(self, subSystem, packetType, commandType, crc=255, length = 16 ):
        self.subSystem = subSystem
        self.length = length
        self.crc = crc
        self.command = commandType
        self.packetType = packetType

    def encode(self):
        packedCtrlByte = self.subSystem
        if self.packetType:
            packedCtrlByte |= (self.packetType << PacketType_BitPosition)
        headerStringCode = struct.pack(Neblina_PacketHeader_fmt,\
        packedCtrlByte, self.length, self.crc, self.command)
        return headerStringCode

    def __str__(self):
        stringFormat = "packetType = {0}, subSystem = {1}, packetLength = {2}, crc = {3}, command = {4}"
        commandString = CommandStrings[(self.subSystem, self.command)]
        stringDescriptor = stringFormat.format(PacketTypeStrings[self.packetType], \
             self.subSystem, self.length,self.crc, commandString)
        return stringDescriptor

# Data = 16 bytes
NeblinaPacket_fmt = "<4s 16s"
class NebCommandPacket(object):
    """docstring for NebCommandPacket"""
    def __init__(self, subSystem, commandType, enable=True, **kwargs):
        # Logic for determining which type of command packet it is based on the header
        if(subSystem == Subsys_Debug and commandType == DebugCmd_UnitTestMotionData):
            self.data = NebUnitTestMotionDataCommandData(kwargs['timestamp'],\
             kwargs['accel'], kwargs['gyro'], kwargs['mag'])
        elif(subSystem == Subsys_MotionEngine and commandType == MotCmd_Downsample):
            self.data = NebDownsampleCommandData(enable)
        elif(subSystem == Subsys_MotionEngine and commandType == MotCmd_AccRange):
            self.data = NebAccRangeCommandData(enable)
        elif(subSystem == Subsys_Storage and commandType == StorageCmd_Playback ):
            self.data = NebFlashPlaybackCommandData(enable, kwargs['sessionID'])
        elif(subSystem == Subsys_EEPROM):
            if( commandType == EEPROMCmd_Read):
                self.data = NebEEPROMCommandData(False, kwargs['pageNumber'])
            elif( commandType == EEPROMCmd_Write ):
                self.data = NebEEPROMCommandData(True, kwargs['pageNumber'], kwargs['dataBytes'])
        else:
            self.data = NebCommandData(enable)
        self.header = NebHeader(subSystem, PacketType_Command, commandType, length=len(self.data.encode()))
        # Perform CRC calculation
        self.header.crc = crc8(bytearray(self.header.encode() + self.data.encode()))

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
        header = NebHeader(Subsys_MotionEngine, False, MotCmd_MAG_Data, len(dataString))
        responsePacket = NebResponsePacket(packetString=None, header=header, data=data, checkCRC=False)
        responsePacket.header.crc = genNebCRC8(bytearray(responsePacket.stringEncode()))
        return responsePacket

    @classmethod
    def createIMUResponsePacket(cls, timestamp, accel, gyro):
        dataString = struct.pack( Neblina_IMU_fmt, \
        timestamp, int(accel[0]), int(accel[1]), int(accel[2]),\
        int(gyro[0]), int(gyro[1]), int(gyro[2]))
        data = IMUData(dataString)
        # Perform CRC of data bytes
        header = NebHeader(Subsys_MotionEngine, False, MotCmd_IMU_Data, len(dataString))
        responsePacket = NebResponsePacket(packetString=None, header=header, data=data, checkCRC=False)
        responsePacket.header.crc = genNebCRC8(bytearray(responsePacket.stringEncode()))
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
        header = NebHeader(Subsys_MotionEngine, False, MotCmd_EulerAngle, len(dataString))
        responsePacket = NebResponsePacket(packetString=None, header=header, data=data, checkCRC=False)
        responsePacket.header.crc = genNebCRC8(bytearray(responsePacket.stringEncode()))
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
        header = NebHeader(Subsys_MotionEngine, False, MotCmd_Pedometer, crc, len(dataString))
        responsePacket = NebResponsePacket(packetString=None, header=header, data=data, checkCRC=False)
        responsePacket.header.crc = genNebCRC8(bytearray(responsePacket.stringEncode()))
        return responsePacket


    def __init__(self, packetString=None, header=None, data=None, checkCRC=True):
        if (packetString != None):
            # Sanity check
            packetStringLength = len(packetString)
            if(packetStringLength < 5):
                raise InvalidPacketFormatError(\
                    'Impossible packet, must have a data payload of at least 1 byte but got {0}')\
                    .format(packetStringLength)

            # The string can either be bytes or an actual string
            # Force it to a string if that is the case.
            if (type(packetString) == str):
                packetString = packetString.encode('iso-8859-1')

            # Extract the header information
            self.headerLength = 4
            headerString = packetString[:self.headerLength]
            ctrlByte, packetLength, crc, command \
            =  struct.unpack(Neblina_PacketHeader_fmt, headerString)
            
            # Extract the value from the subsystem byte            
            subSystem = ctrlByte & Subsys_BitMask

            # Check if the response byte is an acknowledge
            packetTypeCode = ctrlByte & PacketType_BitMask
            packetType = packetTypeCode >> PacketType_BitPosition

            # See if the packet is a response or a command packet
            if(packetType == PacketType_Command):
                raise InvalidPacketFormatError('Cannot create a response packet with the string of a command packet.')

            self.header = NebHeader( subSystem, packetType, command, crc, packetLength )

            # Extract the data substring
            dataString = packetString[self.headerLength:self.headerLength+packetLength]

            # Perform CRC of data bytes
            if(checkCRC):
                calculatedCRC = genNebCRC8(bytearray(packetString))
                if (calculatedCRC != self.header.crc):
                    raise CRCError(calculatedCRC, self.header.crc)

            # Build the data object based on the subsystem and command.
            self.data = ResponsePacketDataConstructors[subSystem][self.header.command](dataString)

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
    def __str__(self):
        return 'Invalid CRC. expected {0} but got {1}'\
            .format(hex(self.expected), hex(self.actual))

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

# Special CRC routine that skips the expected position of the CRC calculation
# in a Neblina packet
def genNebCRC8(packetBytes):
    crc = 0
    # The CRC should be placed as the third byte in the packet
    crc_backup = packetBytes[2]
    packetBytes[2] = 255
    ii = 0
    while ii < len(packetBytes):
       ee = (crc) ^ (packetBytes[ii])
       ff = (ee) ^ (ee>>4) ^ (ee>>7)
       crc = ((ff<<1)%256) ^ ((ff<<4) % 256)
       ii += 1
    packetBytes[2] = crc_backup
    return crc


