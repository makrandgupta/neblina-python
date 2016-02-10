#!/usr/bin/env python
# Neblina unit testing framework
# (C) 2015 Motsai Research Inc.

import unittest
import slip
import binascii
import struct
import neblina as neb
import neblinasim as nebsim

# Unit testing class
class ut_NeblinaPackets(unittest.TestCase):
    
    def setUp(self):
        self.nebSlip = slip.slip()

    def getTestStream(self, filepath):
        self.testFile = open(filepath, "rb")

        # Decode the slip packets
        testSlipPackets = self.nebSlip.decodePackets(self.testFile)
        self.testFile.close()

        return testSlipPackets

    def buildPacketList(self, packetList):
        packets = []
        errorList = []
        for idx,packetString in enumerate(packetList):
            try:
                # print(binascii.hexlify(bytearray(packetString)))
                nebPacket = neb.NebResponsePacket(packetString)
                # print('Appending {0}'.format(nebPacket))
                packets.append(nebPacket)
            except KeyError as keyError:
                # print('Invalid Subsystem or Command Code')
                errorList.append(keyError)
            except NotImplementedError as notImplError:
                # print('Got a non-standard packet at #{0}'\
                #     .format(idx))
                errorList.append(notImplError)
            except neb.CRCError as crcError:
                errorList.append(crcError)
                # print('Got a CRCError at packet #{0}'\
                #     .format(idx))
                # print(crcError)
            except neb.InvalidPacketFormatError as invPacketError:
                errorList.append(invPacketError)
        return (packets, errorList)

    def buildPacketListFromSLIP(self, filename):
        testSlipPackets = self.getTestStream(filename)
        return self.buildPacketList(testSlipPackets)

    def printPackets(self, packetList):
        for packet in packetList:
            print(packet)

    def checkTimestamps(self, packetList, expected, actual):
        currentTimestamp = packetList[0].data.timestamp - expected
        for packet in packetList:
            # print(packet.data.timestamp - currentTimestamp)
            if(packet.data.timestamp - currentTimestamp != 20000):
                print(packet.data.timestamp - currentTimestamp)
            currentTimestamp = packet.data.timestamp
    
    def printEulerPacketString(self, nebPacketString):
        hexlified = binascii.hexlify(nebPacketString)
        print('hexlified = {0}'.format(hexlified))
        print('header = {0}'.format(hexlified[0:8]))
        print('data = {0}'.format(hexlified[8:40]))
        subsys = hexlified[:2]
        length = hexlified[2:4]
        crc = hexlified[4:6]
        command = hexlified[6:8]
        timestamp = hexlified[8:16]
        yaw = hexlified[16:20]
        pitch = hexlified[20:24]
        roll = hexlified[24:28]
        garbage = hexlified[28:40]
        print('subsys = {0}'.format(subsys))
        print('len = {0}'.format(length))
        print('crc = {0}'.format(crc))
        print('command = {0}'.format(command))
        print('timestamp = {0}'.format( timestamp ))
        print('yaw = {0}'.format( yaw ))
        print('pitch = {0}'.format( pitch ))
        print('roll = {0}'.format( roll ))
        print('garbage = {0}'.format( garbage ))

    def testDecodeDebug(self):
        print("\n*** Testing Debug Command Decoding ***")
        commandHeaderBytes = b'\x00\x10\xbc\x02'
        commandDataBytes= b'\xde\xea\xbe\xef\xa5\x01\x11\x01\x02\xba\xbe\x00\x01\x02\x03\x04'
        commandBytes = commandHeaderBytes+commandDataBytes
        packet = neb.NebResponsePacket(commandBytes)
        self.assertEqual(packet.data.distance,   True )
        self.assertEqual(packet.data.force,      False)
        self.assertEqual(packet.data.euler,      True )
        self.assertEqual(packet.data.quaternion, False)
        self.assertEqual(packet.data.imuData,    False)
        self.assertEqual(packet.data.motion,     True )
        self.assertEqual(packet.data.steps,      False)
        self.assertEqual(packet.data.magData,    True )
        self.assertEqual(packet.data.sitStand,   True )
        self.assertEqual(packet.data.recorderStatus,   2)

    def testDecodeLED(self):
        print("\n*** Testing LED Command Decoding ***")
        commandHeaderBytes = b'\x04\x10\x1c\x02'
        commandDataBytes= b'\x03\x04\x23\x05\xfe\x08\xaa\x01\x02\xba\xbe\x00\x01\x02\x03\x04'
        commandBytes = commandHeaderBytes+commandDataBytes
        packet = neb.NebResponsePacket(commandBytes)
        self.assertEqual(len(packet.data.ledTupleList), 3)
        self.assertEqual(packet.data.ledTupleList[0][0], 4)
        self.assertEqual(packet.data.ledTupleList[0][1], 35)
        self.assertEqual(packet.data.ledTupleList[1][0], 5)
        self.assertEqual(packet.data.ledTupleList[1][1], 254)
        self.assertEqual(packet.data.ledTupleList[2][0], 8)
        self.assertEqual(packet.data.ledTupleList[2][1], 170)

    def testDecodeStorage(self):
        print("\n*** Testing Flash Storage Decoding ***")
        packets, errorList = self.buildPacketListFromSLIP("SampleData/FlashRecordPlayback.bin")
        # Make sure the first CRC Error is there
        self.assertEqual(len(errorList), 0)
        self.assertEqual(len(packets), 5)
        # Check response packet decoding
        self.assertEqual(packets[0].data.openClose, True)
        self.assertEqual(packets[0].data.sessionID, 0)
        self.assertEqual(packets[1].data.openClose, False)
        self.assertEqual(packets[1].data.sessionID, 258)
        self.assertEqual(packets[3].data.openClose, True)
        self.assertEqual(packets[3].data.sessionID, 4878)
        self.assertEqual(packets[4].data.openClose, False)
        self.assertEqual(packets[4].data.sessionID, 1)

    def testDecodeEuler(self):
        print("\n*** Testing Euler Angle Stream Decoding ***")
        packets, errorList = self.buildPacketListFromSLIP("SampleData/EulerAngleStream.bin")
        # Make sure the timestamps are well extracted
        self.assertEqual(packets[12].data.timestamp, 190503824)
        self.assertEqual(packets[19].data.timestamp, 190643824)
        # Make sure the first packet is recognized as garbage
        # self.assertEqual(type(errorList[0]), NotImplementedError)
        # Check intentional CRC Errors
        self.assertEqual(type(errorList[1]), neb.CRCError)
        self.assertEqual(errorList[1].expected, 134)
        self.assertEqual(errorList[1].actual, 182)
        self.assertEqual(type(errorList[2]), neb.CRCError)
        self.assertEqual(errorList[2].expected, 12)
        self.assertEqual(errorList[2].actual, 19)
        # Check euler angle decoding
        self.assertEqual(packets[6].data.yaw, -51.9)
        self.assertEqual(packets[6].data.pitch, -60.1)
        self.assertEqual(packets[6].data.roll, 121.8)

    def testDecodePedometer(self):
        print("\n*** Testing Pedometer Decoding ***")
        packets, errorList = self.buildPacketListFromSLIP("SampleData/PedometerStream.bin")
        # Make sure the beginning garbage packet was not recorded
        self.assertEqual(len(packets), 7)
        # self.assertEqual(type(errorList[0]), NotImplementedError)
        # Check pedometer data decoding
        self.assertEqual(packets[5].data.timestamp, 19057720)
        self.assertEqual(packets[5].data.stepCount, 4)
        self.assertEqual(packets[5].data.stepsPerMinute, 104)
        self.assertEqual(packets[5].data.walkingDirection, -180.0)

    def testDecodeQuat(self):
        print("\n*** Testing Quaternion Stream Decoding ***")
        packets, errorList = self.buildPacketListFromSLIP("SampleData/QuaternionStream.bin")
        # The first packet should result in an error since it is incomplete
        self.assertEqual(len(errorList), 1)
        # self.assertEqual(type(errorList[0]), NotImplementedError)
        # Check quaternion packet decoding
        self.assertEqual(packets[8].data.quaternions[0], 21947)
        self.assertEqual(packets[8].data.quaternions[1], 12650)
        self.assertEqual(packets[8].data.quaternions[2], -20698)
        self.assertEqual(packets[8].data.quaternions[3], -177)

    def testDecodeMAG(self):
        print("\n*** Testing MAG Stream Decoding ***")
        packets, errorList = self.buildPacketListFromSLIP("SampleData/MAGStream.bin")
        # Make sure the first CRC Error is there
        self.assertEqual(len(errorList), 1)
        # Check MAG packet decoding
        self.assertEqual(packets[11].data.accel[0], -7527)
        self.assertEqual(packets[11].data.accel[1], 1119)
        self.assertEqual(packets[11].data.accel[2], -15106)
        self.assertEqual(packets[11].data.mag[0], 1009)
        self.assertEqual(packets[11].data.mag[1], -1903)
        self.assertEqual(packets[11].data.mag[2], 3933)

    def testDecodeIMU(self):
        print("\n*** Testing IMU Stream Decoding ***")
        packets, errorList = self.buildPacketListFromSLIP("SampleData/IMUStream.bin")
        # Make sure the first CRC Error is there
        self.assertEqual(len(errorList), 1)
        # Check MAG packet decoding
        self.assertEqual(packets[11].data.timestamp, 12377048)
        self.assertEqual(packets[11].data.accel[0], -12376)
        self.assertEqual(packets[11].data.accel[1], 6870)
        self.assertEqual(packets[11].data.accel[2], -8843)
        self.assertEqual(packets[11].data.gyro[0], -21)
        self.assertEqual(packets[11].data.gyro[1], -23)
        self.assertEqual(packets[11].data.gyro[2], 42)

    def testDecodeTrajectory(self):
        print("\n*** Testing Decode Trajectory Decoding ***")
        packets, errorList = self.buildPacketListFromSLIP("SampleData/TrajectoryDistanceStream.bin")
        # Make sure the first CRC Error is there
        self.assertEqual(len(errorList), 1)
        # Check MAG packet decoding
        self.assertEqual(packets[14].data.timestamp, 36838400)
        self.assertEqual(packets[14].data.eulerAngleErrors[0], -22)
        self.assertEqual(packets[14].data.eulerAngleErrors[1], -1)
        self.assertEqual(packets[14].data.eulerAngleErrors[2], -8)

    def testDecodeExtForce(self):
        print("\n*** Testing External Force Decoding ***")
        packets, errorList = self.buildPacketListFromSLIP("SampleData/ForceStream.bin")
        # Make sure the first CRC Error is there
        self.assertEqual(len(errorList), 1)
        # Check Ext packet decoding
        self.assertEqual(packets[2].data.timestamp, 3878480)
        self.assertEqual(packets[2].data.externalForces[0], 2559)
        self.assertEqual(packets[2].data.externalForces[1], -257)
        self.assertEqual(packets[2].data.externalForces[2], 597)

    def testDecodeMotionState(self):
        print("\n*** Testing Motion State Decoding ***")
        packets, errorList = self.buildPacketListFromSLIP("SampleData/MotionStateStream.bin")
        # Make sure the first CRC Error is there
        self.assertEqual(len(errorList), 1)
        # Check Ext packet decoding
        self.assertEqual(packets[9].data.timestamp, 43738384)
        self.assertEqual(packets[9].data.startStop, True)

    def testEncodeCommandPackets(self):
        print("\n*** Testing Encoding of Packets ***")
        packetList = []
        # Testing downsample command
        # Downsample to 1Hz example
        downSampleFactor = 1000
        downSampleCommandPacket = neb.NebCommandPacket(neb.Subsys_MotionEngine, neb.MotCmd_Downsample, downSampleFactor)
        packetString = downSampleCommandPacket.stringEncode()
        packetBytes = bytearray(packetString)
        self.assertEqual(len(packetBytes), 20)
        self.assertEqual(packetBytes[0], (neb.PacketType_Command << 5)| neb.Subsys_MotionEngine)
        self.assertEqual(packetBytes[1], 16)
        self.assertEqual(packetBytes[3], neb.MotCmd_Downsample)
        self.assertEqual(packetBytes[8], struct.pack('<H', downSampleFactor)[0])
        self.assertEqual(packetBytes[9], struct.pack('<H', downSampleFactor)[1])

        # Make sure these calls dont cause an exception
        commandPacket = neb.NebCommandPacket(neb.Subsys_MotionEngine, neb.MotCmd_MotionState, True)
        commandPacket = neb.NebCommandPacket(neb.Subsys_MotionEngine, neb.MotCmd_MotionState, False)
        commandPacket = neb.NebCommandPacket(neb.Subsys_MotionEngine, neb.MotCmd_IMU_Data, True)
        commandPacket = neb.NebCommandPacket(neb.Subsys_MotionEngine, neb.MotCmd_IMU_Data, False)
        commandPacket = neb.NebCommandPacket(neb.Subsys_MotionEngine, neb.MotCmd_Quaternion, True)
        commandPacket = neb.NebCommandPacket(neb.Subsys_MotionEngine, neb.MotCmd_Quaternion, False)
        commandPacket = neb.NebCommandPacket(neb.Subsys_MotionEngine, neb.MotCmd_EulerAngle, True)
        commandPacket = neb.NebCommandPacket(neb.Subsys_MotionEngine, neb.MotCmd_EulerAngle, False)
        commandPacket = neb.NebCommandPacket(neb.Subsys_MotionEngine, neb.MotCmd_ExtForce, True)
        commandPacket = neb.NebCommandPacket(neb.Subsys_MotionEngine, neb.MotCmd_ExtForce, False)
        commandPacket = neb.NebCommandPacket(neb.Subsys_MotionEngine, neb.MotCmd_TrajectoryInfo, True)
        commandPacket = neb.NebCommandPacket(neb.Subsys_MotionEngine, neb.MotCmd_TrajectoryInfo, False)
        commandPacket = neb.NebCommandPacket(neb.Subsys_MotionEngine, neb.MotCmd_Pedometer, True)
        commandPacket = neb.NebCommandPacket(neb.Subsys_MotionEngine, neb.MotCmd_Pedometer, False)
        commandPacket = neb.NebCommandPacket(neb.Subsys_MotionEngine, neb.MotCmd_MAG_Data, True)
        commandPacket = neb.NebCommandPacket(neb.Subsys_MotionEngine, neb.MotCmd_MAG_Data, False)

        # Test encoding of recording packets
        recordCommandPacket = neb.NebCommandPacket(neb.Subsys_Storage, neb.StorageCmd_EraseAll)
        packetBytes = bytearray(recordCommandPacket.stringEncode())
        self.assertEqual(packetBytes[0], (neb.PacketType_Command << 5)| neb.Subsys_Storage)
        self.assertEqual(packetBytes[1], 16)
        self.assertEqual(packetBytes[3], neb.StorageCmd_EraseAll)

        recordCommandPacket = neb.NebCommandPacket(neb.Subsys_Storage, neb.StorageCmd_Record, True)
        packetBytes = bytearray(recordCommandPacket.stringEncode())
        self.assertEqual(packetBytes[0], (neb.PacketType_Command << 5)| neb.Subsys_Storage)
        self.assertEqual(packetBytes[3], neb.StorageCmd_Record)
        self.assertEqual(packetBytes[8], 0x01)
        recordCommandPacket = neb.NebCommandPacket(neb.Subsys_Storage, neb.StorageCmd_Record, False)
        packetBytes = bytearray(recordCommandPacket.stringEncode())
        self.assertEqual(packetBytes[0], (neb.PacketType_Command << 5)| neb.Subsys_Storage)
        self.assertEqual(packetBytes[3], neb.StorageCmd_Record)
        self.assertEqual(packetBytes[8], 0x00)

        recordCommandPacket = neb.NebCommandPacket(neb.Subsys_Storage, neb.StorageCmd_Playback, True, sessionID=42)
        packetBytes = bytearray(recordCommandPacket.stringEncode())
        self.assertEqual(packetBytes[0], (neb.PacketType_Command << 5)| neb.Subsys_Storage)
        self.assertEqual(packetBytes[3], neb.StorageCmd_Playback)
        self.assertEqual(packetBytes[8], 0x01)
        recordCommandPacket = neb.NebCommandPacket(neb.Subsys_Storage, neb.StorageCmd_Playback, False,  sessionID=42)
        packetBytes = bytearray(recordCommandPacket.stringEncode())
        self.assertEqual(packetBytes[0], (neb.PacketType_Command << 5)| neb.Subsys_Storage)
        self.assertEqual(packetBytes[3], neb.StorageCmd_Playback)
        self.assertEqual(packetBytes[8], 0x00)

        readCommandPacket = neb.NebCommandPacket(neb.Subsys_EEPROM, neb.EEPROMCmd_Read, pageNumber=5)
        packetBytes = bytearray(readCommandPacket.stringEncode())
        self.assertEqual(packetBytes[0], (neb.PacketType_Command << 5)| neb.Subsys_EEPROM)
        self.assertEqual(packetBytes[3], neb.EEPROMCmd_Read)
        self.assertEqual(packetBytes[4], 0x05)
        
        # EEPROM Command packet testing
        writeCommandPacket = neb.NebCommandPacket(neb.Subsys_EEPROM, neb.EEPROMCmd_Write,\
          pageNumber=11, dataBytes=b'\xde\xad\xbe\xef\xba\xbe\x92\x74')
        packetBytes = bytearray(writeCommandPacket.stringEncode())
        self.assertEqual(packetBytes[0], (neb.PacketType_Command << 5)| neb.Subsys_EEPROM)
        self.assertEqual(packetBytes[3], neb.EEPROMCmd_Write)
        self.assertEqual(packetBytes[4], 0x0B)
        self.assertEqual(packetBytes[5], 0x00)
        self.assertEqual(packetBytes[6], 0xde)
        self.assertEqual(packetBytes[7], 0xad)
        self.assertEqual(packetBytes[8], 0xbe)
        self.assertEqual(packetBytes[9], 0xef)
        self.assertEqual(packetBytes[10], 0xba)
        self.assertEqual(packetBytes[11], 0xbe)
        self.assertEqual(packetBytes[12], 0x92)
        self.assertEqual(packetBytes[13], 0x74)

        # Debug packet set interface
        switchInterfaceCommandPacket = neb.NebCommandPacket(neb.Subsys_Debug,\
            neb.DebugCmd_SetInterface,\
            True)
        packetBytes = bytearray(switchInterfaceCommandPacket.stringEncode())
        self.assertEqual(packetBytes[0], (neb.PacketType_Command << 5)| neb.Subsys_Debug)
        self.assertEqual(packetBytes[3], neb.DebugCmd_SetInterface)
        self.assertEqual(packetBytes[8], 0x01)
        switchInterfaceCommandPacket = neb.NebCommandPacket(neb.Subsys_Debug,\
            neb.DebugCmd_SetInterface,\
            False)
        packetBytes = bytearray(switchInterfaceCommandPacket.stringEncode())
        self.assertEqual(packetBytes[0], (neb.PacketType_Command << 5)| neb.Subsys_Debug)
        self.assertEqual(packetBytes[3], neb.DebugCmd_SetInterface)
        self.assertEqual(packetBytes[8], 0x00)

        flashAndRecorderStateCommandPacket = neb.NebCommandPacket(neb.Subsys_Debug,\
            neb.DebugCmd_MotAndFlashRecState)
        packetBytes = bytearray(flashAndRecorderStateCommandPacket.stringEncode())
        self.assertEqual(packetBytes[0], (neb.PacketType_Command << 5)| neb.Subsys_Debug)
        self.assertEqual(packetBytes[3], neb.DebugCmd_MotAndFlashRecState)

        # Unit test start command packet
        unitTestStartCommandPacket = neb.NebCommandPacket(neb.Subsys_Debug,\
            neb.DebugCmd_StartUnitTestMotion, True)
        packetBytes = bytearray(unitTestStartCommandPacket.stringEncode())
        self.assertEqual(packetBytes[0], (neb.PacketType_Command << 5)| neb.Subsys_Debug)
        self.assertEqual(packetBytes[3], neb.DebugCmd_StartUnitTestMotion)
        self.assertEqual(packetBytes[8], 0x01)
        unitTestStartCommandPacket = neb.NebCommandPacket(neb.Subsys_Debug,\
            neb.DebugCmd_StartUnitTestMotion, False)
        packetBytes = bytearray(unitTestStartCommandPacket.stringEncode())
        self.assertEqual(packetBytes[0], (neb.PacketType_Command << 5)| neb.Subsys_Debug)
        self.assertEqual(packetBytes[3], neb.DebugCmd_StartUnitTestMotion)
        self.assertEqual(packetBytes[8], 0x00)

        # Unit test data command packet
        imuPackets = nebsim.createRandomIMUDataPacketList(50.0, 10, 1.0)
        magPackets = nebsim.createRandomMAGDataPacketList(50.0, 10, 1.0)
        for idx,imuPacket in enumerate(imuPackets):
            magPacket = magPackets[idx]
            imuPacketString = imuPacket.stringEncode()
            magPacketString = magPacket.stringEncode()
            unitTestDataPacket = neb.NebCommandPacket(neb.Subsys_Debug,\
                neb.DebugCmd_UnitTestMotionData, timestamp=imuPacket.data.timestamp,\
                accel=imuPacket.data.accel, gyro=imuPacket.data.gyro, mag=magPacket.data.mag)
            testPacketBytes = bytearray(unitTestDataPacket.stringEncode())
            self.assertEqual(testPacketBytes[0], (neb.PacketType_Command << 5)| neb.Subsys_Debug)
            self.assertEqual(testPacketBytes[3], neb.DebugCmd_UnitTestMotionData)
            self.assertEqual(testPacketBytes[8], imuPacketString[8])
            self.assertEqual(testPacketBytes[9], imuPacketString[9])
            self.assertEqual(testPacketBytes[10], imuPacketString[10])
            self.assertEqual(testPacketBytes[11], imuPacketString[11])
            self.assertEqual(testPacketBytes[12], imuPacketString[12])
            self.assertEqual(testPacketBytes[13], imuPacketString[13])
            self.assertEqual(testPacketBytes[14], imuPacketString[14])
            self.assertEqual(testPacketBytes[15], imuPacketString[15])
            self.assertEqual(testPacketBytes[16], imuPacketString[16])
            self.assertEqual(testPacketBytes[17], imuPacketString[17])
            self.assertEqual(testPacketBytes[18], imuPacketString[18])
            self.assertEqual(testPacketBytes[19], imuPacketString[19])
            self.assertEqual(testPacketBytes[20], magPacketString[8])
            self.assertEqual(testPacketBytes[21], magPacketString[9])
            self.assertEqual(testPacketBytes[22], magPacketString[10])
            self.assertEqual(testPacketBytes[23], magPacketString[11])
            self.assertEqual(testPacketBytes[24], magPacketString[12])
            self.assertEqual(testPacketBytes[25], magPacketString[13])

        # LED Command Packets
        ledValues = [(0,1),(1,34),(3,0),(4,254),(5,128),(12,11)]
        setLEDValuesPacket = neb.NebCommandPacket(\
            neb.Subsys_LED, neb.LEDCmd_SetVal, ledValueTupleList=ledValues)
        packetBytes = bytearray(setLEDValuesPacket.stringEncode())
        self.assertEqual(packetBytes[0], (neb.PacketType_Command << 5)| neb.Subsys_LED)
        self.assertEqual(packetBytes[3], neb.LEDCmd_SetVal)
        self.assertEqual(packetBytes[4], 6)
        self.assertEqual(packetBytes[5], 0x00)
        self.assertEqual(packetBytes[6], 0x01)
        self.assertEqual(packetBytes[7], 0x01)
        self.assertEqual(packetBytes[8], 34)
        self.assertEqual(packetBytes[9], 3)
        self.assertEqual(packetBytes[10], 0)
        self.assertEqual(packetBytes[11], 4)
        self.assertEqual(packetBytes[12], 254)
        self.assertEqual(packetBytes[13], 5)
        self.assertEqual(packetBytes[14], 128)
        self.assertEqual(packetBytes[15], 12)
        self.assertEqual(packetBytes[16], 11)

        leds = [3,5,1,6,7,2,4]
        getLEDValuesPacket = neb.NebCommandPacket(\
            neb.Subsys_LED, neb.LEDCmd_GetVal,\
            ledIndices=leds)
        packetBytes = bytearray(getLEDValuesPacket.stringEncode())
        self.assertEqual(packetBytes[0], (neb.PacketType_Command << 5)| neb.Subsys_LED)
        self.assertEqual(packetBytes[3], neb.LEDCmd_GetVal)
        self.assertEqual(packetBytes[4], 7)
        self.assertEqual(packetBytes[5], 3)
        self.assertEqual(packetBytes[6], 5)
        self.assertEqual(packetBytes[7], 1)
        self.assertEqual(packetBytes[8], 6)
        self.assertEqual(packetBytes[9], 7)
        self.assertEqual(packetBytes[10], 2)
        self.assertEqual(packetBytes[11], 4)

        # Flash Session Info
        sessionInfoCommandPacket = neb.NebCommandPacket(neb.Subsys_Storage,\
            neb.StorageCmd_SessionInfo, sessionID = 10)
        packetBytes = bytearray(sessionInfoCommandPacket.stringEncode())
        self.assertEqual(packetBytes[0], (neb.PacketType_Command << 5)| neb.Subsys_Storage)
        self.assertEqual(packetBytes[3], neb.StorageCmd_SessionInfo)
        self.assertEqual(packetBytes[8], 0x0A)
        self.assertEqual(packetBytes[9], 0x00)

    def testCreateEulerPackets(self):
        print("\n*** Testing Encoding and Decoding of Euler Angle Packets ***")
        responsePackets = []
        packets = nebsim.createSpinningObjectPacketList(50.0, 1.0, 2.0, 6.0)
        
        for packet in packets:
            packetString = packet.stringEncode()
            responsePackets.append(neb.NebResponsePacket(packetString))
        for idx,packet in enumerate(responsePackets):
            self.assertEqual(packets[idx].header.subSystem, neb.Subsys_MotionEngine)
            self.assertEqual(packets[idx].header.command, neb.MotCmd_EulerAngle)
            self.assertEqual(packets[idx].data.timestamp, packet.data.timestamp)
            self.assertEqual(packets[idx].data.yaw, packet.data.yaw)
            self.assertEqual(packets[idx].data.pitch, packet.data.pitch)
            self.assertEqual(packets[idx].data.roll, packet.data.roll)
            self.assertEqual(packets[idx].data.demoHeading, packet.data.demoHeading)

    def testCreatePedometerPackets(self):
        print("\n*** Testing Encoding and Decoding of Pedometer Packets ***")
        responsePackets = []
        packets = nebsim.createWalkingPathPacketList(1000, 61.0, 5.0, 10)
        for packet in packets:
            packetString = packet.stringEncode()
            responsePackets.append(neb.NebResponsePacket(packetString))
        for idx,packet in enumerate(responsePackets):
            self.assertEqual(packets[idx].header.subSystem, neb.Subsys_MotionEngine)
            self.assertEqual(packets[idx].header.command, neb.MotCmd_Pedometer)
            self.assertEqual(packets[idx].data.timestamp, packet.data.timestamp)
            self.assertEqual(packets[idx].data.stepCount, packet.data.stepCount)
            self.assertEqual(packets[idx].data.stepsPerMinute, packet.data.stepsPerMinute)
            self.assertEqual(packets[idx].data.walkingDirection, packet.data.walkingDirection)
            self.assertGreaterEqual(packets[idx].data.walkingDirection, -180.0)
            self.assertLessEqual(packets[idx].data.walkingDirection, 180.0)

    def testCreateIMUPackets(self):
        print("\n*** Testing Encoding and Decoding of IMU Packets ***")
        responsePackets = []
        packets = nebsim.createRandomIMUDataPacketList(50.0, 300, 1.0)
        for packet in packets:
            packetString = packet.stringEncode()
            responsePackets.append(neb.NebResponsePacket(packetString))
        for idx,packet in enumerate(responsePackets):
            self.assertEqual( packets[idx].header.subSystem, neb.Subsys_MotionEngine)
            self.assertEqual( packets[idx].header.command, neb.MotCmd_IMU_Data)
            self.assertEqual( packets[idx].data.timestamp, packet.data.timestamp )
            self.assertEqual( packets[idx].data.accel[0], packet.data.accel[0] )
            self.assertEqual( packets[idx].data.accel[1], packet.data.accel[1] )
            self.assertEqual( packets[idx].data.accel[2], packet.data.accel[2] )
            self.assertEqual( packets[idx].data.gyro[0], packet.data.gyro[0] )
            self.assertEqual( packets[idx].data.gyro[1], packet.data.gyro[1] )
            self.assertEqual( packets[idx].data.gyro[2], packet.data.gyro[2] )

    def testCreateMAGPackets(self):
        print("\n*** Testing Encoding and Decoding of MAG Packets ***")
        responsePackets = []
        packets = nebsim.createRandomMAGDataPacketList(50.0, 300, 1.0)
        for packet in packets:
            packetString = packet.stringEncode()
            responsePackets.append(neb.NebResponsePacket(packetString))
        for idx,packet in enumerate(responsePackets):
            self.assertEqual( packets[idx].header.subSystem, neb.Subsys_MotionEngine)
            self.assertEqual( packets[idx].header.command, neb.MotCmd_MAG_Data)
            self.assertEqual( packets[idx].data.timestamp, packet.data.timestamp )
            self.assertEqual( packets[idx].data.mag[0], packet.data.mag[0] )
            self.assertEqual( packets[idx].data.mag[1], packet.data.mag[1] )
            self.assertEqual( packets[idx].data.mag[2], packet.data.mag[2] )
            self.assertEqual( packets[idx].data.accel[0], packet.data.accel[0] )
            self.assertEqual( packets[idx].data.accel[1], packet.data.accel[1] )
            self.assertEqual( packets[idx].data.accel[2], packet.data.accel[2] )

if __name__ == "__main__":
    unittest.main() # run all tests
    print (unittest.TextTestResult)
