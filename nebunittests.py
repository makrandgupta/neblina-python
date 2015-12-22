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
        self.assertEqual(type(errorList[0]), NotImplementedError)
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
        self.assertEqual(len(packets), 6)
        self.assertEqual(type(errorList[0]), NotImplementedError)
        # Make sure the invalid subsystem error has been detected
        self.assertEqual(type(errorList[1]), neb.InvalidPacketFormatError)
        # Check pedometer data decoding
        self.assertEqual(packets[4].data.timestamp, 19057720)
        self.assertEqual(packets[4].data.stepCount, 4)
        self.assertEqual(packets[4].data.stepsPerMinute, 104)
        self.assertEqual(packets[4].data.walkingDirection, -180.0)

    def testDecodeQuat(self):
        print("\n*** Testing Quaternion Stream Decoding ***")
        packets, errorList = self.buildPacketListFromSLIP("SampleData/QuaternionStream.bin")
        # The first packet should result in an error since it is incomplete
        self.assertEqual(len(errorList), 1)
        self.assertEqual(type(errorList[0]), NotImplementedError)
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
        self.assertEqual(packetBytes[8], struct.pack('>H', downSampleFactor)[0])
        self.assertEqual(packetBytes[9], struct.pack('>H', downSampleFactor)[1])

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
        commandPacket = neb.NebCommandPacket(neb.Subsys_MotionEngine, neb.MotCmd_TrajectoryDistance, True)
        commandPacket = neb.NebCommandPacket(neb.Subsys_MotionEngine, neb.MotCmd_TrajectoryDistance, False)
        commandPacket = neb.NebCommandPacket(neb.Subsys_MotionEngine, neb.MotCmd_Pedometer, True)
        commandPacket = neb.NebCommandPacket(neb.Subsys_MotionEngine, neb.MotCmd_Pedometer, False)
        commandPacket = neb.NebCommandPacket(neb.Subsys_MotionEngine, neb.MotCmd_MAG_Data, True)
        commandPacket = neb.NebCommandPacket(neb.Subsys_MotionEngine, neb.MotCmd_MAG_Data, False)

        # Test encoding of recording packets
        recordCommandPacket = neb.NebCommandPacket(neb.Subsys_Storage, neb.StorageCmd_EraseAll, True)
        packetBytes = bytearray(recordCommandPacket.stringEncode())
        self.assertEqual(packetBytes[0], (neb.PacketType_Command << 5)| neb.Subsys_Storage)
        self.assertEqual(packetBytes[3], neb.StorageCmd_EraseAll)
        self.assertEqual(packetBytes[8], 0x01)
        recordCommandPacket = neb.NebCommandPacket(neb.Subsys_Storage, neb.StorageCmd_EraseAll, False)
        packetBytes = bytearray(recordCommandPacket.stringEncode())
        self.assertEqual(packetBytes[0], (neb.PacketType_Command << 5)| neb.Subsys_Storage)
        self.assertEqual(packetBytes[3], neb.StorageCmd_EraseAll)
        self.assertEqual(packetBytes[8], 0x00)

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

        readCommandPacket = neb.NebCommandPacket(neb.Subsys_EEPROM, neb.EEPROMCmd_Read, True, pageNumber=5)
        packetBytes = bytearray(readCommandPacket.stringEncode())
        self.assertEqual(packetBytes[0], (neb.PacketType_Command << 5)| neb.Subsys_EEPROM)
        self.assertEqual(packetBytes[3], neb.EEPROMCmd_Read)
        self.assertEqual(packetBytes[4], 0x05)
        
        writeCommandPacket = neb.NebCommandPacket(neb.Subsys_EEPROM, neb.EEPROMCmd_Write, False,\
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
