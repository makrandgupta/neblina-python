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
    
    def setUp(d):
        d.nebSlip = slip.slip()

    def getTestStream(d, filepath):
        d.testFile = open(filepath, "rb")

        # Decode the slip packets
        testSlipPackets = d.nebSlip.decodePackets(d.testFile)
        d.testFile.close()

        return testSlipPackets

    def buildPacketList(d, packetList):
        packets = []
        errorList = []
        for idx,packetString in enumerate(packetList):
            try:
                # print(binascii.hexlify(bytearray(packetString)))
                nebPacket = neb.NebResponsePacket(packetString)
                # print('Appending {0}'.format(nebPacket))
                packets.append(nebPacket)
            except KeyError as keyError:
                # print('Invalid Motion Engine Code')
                errorList.append(keyError)
            except NotImplementedError as notImplError:
                # print('Got a non-standard packet at #{0}'\
                    # .format(idx))
                errorList.append(notImplError)
            except neb.CRCError as crcError:
                errorList.append(crcError)
                # print('Got a CRCError at packet #{0}'\
                    # .format(idx))
            except neb.InvalidPacketFormatError as invPacketError:
                errorList.append(invPacketError)
        return (packets, errorList)

    def buildPacketListFromSLIP(d, filename):
        testSlipPackets = d.getTestStream(filename)
        return d.buildPacketList(testSlipPackets)

    def printPackets(d, packetList):
        for packet in packetList:
            print(packet)

    def checkTimestamps(d, packetList, expected, actual):
        currentTimestamp = packetList[0].data.timestamp - expected
        for packet in packetList:
            # print(packet.data.timestamp - currentTimestamp)
            if(packet.data.timestamp - currentTimestamp != 20000):
                print(packet.data.timestamp - currentTimestamp)
            currentTimestamp = packet.data.timestamp
    
    def printEulerPacketString(d, nebPacketString):
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


    def testDecodeEuler(d):
        print("\n*** Testing Euler Angle Stream Decoding ***")
        packets, errorList = d.buildPacketListFromSLIP("SampleData/EulerAngleStream.bin")
        # Make sure the timestamps are well extracted
        d.assertEqual(packets[12].data.timestamp, 190503824)
        d.assertEqual(packets[19].data.timestamp, 190643824)
        # Make sure the first packet is recognized as garbage
        d.assertEqual(type(errorList[0]), NotImplementedError)
        # Check intentional CRC Errors
        d.assertEqual(type(errorList[1]), neb.CRCError)
        d.assertEqual(errorList[1].expected, 134)
        d.assertEqual(errorList[1].actual, 182)
        d.assertEqual(type(errorList[2]), neb.CRCError)
        d.assertEqual(errorList[2].expected, 12)
        d.assertEqual(errorList[2].actual, 19)
        # Check euler angle decoding
        d.assertEqual(packets[6].data.yaw, -51.9)
        d.assertEqual(packets[6].data.pitch, -60.1)
        d.assertEqual(packets[6].data.roll, 121.8)

    def testDecodePedometer(d):
        print("\n*** Testing Pedometer Decoding ***")
        packets, errorList = d.buildPacketListFromSLIP("SampleData/PedometerStream.bin")
        # Make sure the beginning garbage packet was not recorded
        d.assertEqual(len(packets), 6)
        d.assertEqual(type(errorList[0]), NotImplementedError)
        # Make sure the invalid subsystem error has been detected
        d.assertEqual(type(errorList[1]), neb.InvalidPacketFormatError)
        # Check pedometer data decoding
        d.assertEqual(packets[4].data.timestamp, 19057720)
        d.assertEqual(packets[4].data.stepCount, 4)
        d.assertEqual(packets[4].data.stepsPerMinute, 104)
        d.assertEqual(packets[4].data.walkingDirection, -180.0)

    def testDecodeQuat(d):
        print("\n*** Testing Quaternion Stream Decoding ***")
        packets, errorList = d.buildPacketListFromSLIP("SampleData/QuaternionStream.bin")
        # The first packet should result in an error since it is incomplete
        d.assertEqual(len(errorList), 1)
        d.assertEqual(type(errorList[0]), NotImplementedError)
        # Check quaternion packet decoding
        d.assertEqual(packets[8].data.quaternions[0], 21947)
        d.assertEqual(packets[8].data.quaternions[1], 12650)
        d.assertEqual(packets[8].data.quaternions[2], -20698)
        d.assertEqual(packets[8].data.quaternions[3], -177)

    def testDecodeMAG(d):
        print("\n*** Testing MAG Stream Decoding ***")
        packets, errorList = d.buildPacketListFromSLIP("SampleData/MAGStream.bin")
        # Make sure the first CRC Error is there
        d.assertEqual(len(errorList), 1)
        # Check MAG packet decoding
        d.assertEqual(packets[11].data.accel[0], -7527)
        d.assertEqual(packets[11].data.accel[1], 1119)
        d.assertEqual(packets[11].data.accel[2], -15106)
        d.assertEqual(packets[11].data.mag[0], 1009)
        d.assertEqual(packets[11].data.mag[1], -1903)
        d.assertEqual(packets[11].data.mag[2], 3933)

    def testDecodeIMU(d):
        print("\n*** Testing IMU Stream Decoding ***")
        packets, errorList = d.buildPacketListFromSLIP("SampleData/IMUStream.bin")
        # Make sure the first CRC Error is there
        d.assertEqual(len(errorList), 1)
        # Check MAG packet decoding
        d.assertEqual(packets[11].data.timestamp, 12377048)
        d.assertEqual(packets[11].data.accel[0], -12376)
        d.assertEqual(packets[11].data.accel[1], 6870)
        d.assertEqual(packets[11].data.accel[2], -8843)
        d.assertEqual(packets[11].data.gyro[0], -21)
        d.assertEqual(packets[11].data.gyro[1], -23)
        d.assertEqual(packets[11].data.gyro[2], 42)

    def testDecodeTrajectory(d):
        print("\n*** Testing Decode Trajectory Decoding ***")
        packets, errorList = d.buildPacketListFromSLIP("SampleData/TrajectoryDistanceStream.bin")
        # Make sure the first CRC Error is there
        d.assertEqual(len(errorList), 1)
        # Check MAG packet decoding
        d.assertEqual(packets[14].data.timestamp, 36838400)
        d.assertEqual(packets[14].data.eulerAngleErrors[0], -22)
        d.assertEqual(packets[14].data.eulerAngleErrors[1], -1)
        d.assertEqual(packets[14].data.eulerAngleErrors[2], -8)

    def testDecodeExtForce(d):
        print("\n*** Testing External Force Decoding ***")
        packets, errorList = d.buildPacketListFromSLIP("SampleData/ForceStream.bin")
        # Make sure the first CRC Error is there
        d.assertEqual(len(errorList), 1)
        # Check Ext packet decoding
        d.assertEqual(packets[2].data.timestamp, 3878480)
        d.assertEqual(packets[2].data.externalForces[0], 2559)
        d.assertEqual(packets[2].data.externalForces[1], -257)
        d.assertEqual(packets[2].data.externalForces[2], 597)

    def testDecodeMotionState(d):
        print("\n*** Testing Motion State Decoding ***")
        packets, errorList = d.buildPacketListFromSLIP("SampleData/MotionStateStream.bin")
        # Make sure the first CRC Error is there
        d.assertEqual(len(errorList), 1)
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
        self.assertEqual(packetBytes[0], neb.Subsys_MotionEngine | neb.Subsys_CmdOrRespMask)
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
            d.assertEqual( packets[idx].header.subSystem, neb.Subsys_MotionEngine)
            d.assertEqual( packets[idx].header.command, neb.MotCmd_IMU_Data)
            d.assertEqual( packets[idx].data.timestamp, packet.data.timestamp )
            d.assertEqual( packets[idx].data.accel[0], packet.data.accel[0] )
            d.assertEqual( packets[idx].data.accel[1], packet.data.accel[1] )
            d.assertEqual( packets[idx].data.accel[2], packet.data.accel[2] )
            d.assertEqual( packets[idx].data.gyro[0], packet.data.gyro[0] )
            d.assertEqual( packets[idx].data.gyro[1], packet.data.gyro[1] )
            d.assertEqual( packets[idx].data.gyro[2], packet.data.gyro[2] )

    def testCreateMAGPackets(d):
        print("\n*** Testing Encoding and Decoding of MAG Packets ***")
        responsePackets = []
        packets = nebsim.createRandomMAGDataPacketList(50.0, 300, 1.0)
        for packet in packets:
            packetString = packet.stringEncode()
            responsePackets.append(neb.NebResponsePacket(packetString))
        for idx,packet in enumerate(responsePackets):
            d.assertEqual( packets[idx].header.subSystem, neb.Subsys_MotionEngine)
            d.assertEqual( packets[idx].header.command, neb.MotCmd_MAG_Data)
            d.assertEqual( packets[idx].data.timestamp, packet.data.timestamp )
            d.assertEqual( packets[idx].data.mag[0], packet.data.mag[0] )
            d.assertEqual( packets[idx].data.mag[1], packet.data.mag[1] )
            d.assertEqual( packets[idx].data.mag[2], packet.data.mag[2] )
            d.assertEqual( packets[idx].data.accel[0], packet.data.accel[0] )
            d.assertEqual( packets[idx].data.accel[1], packet.data.accel[1] )
            d.assertEqual( packets[idx].data.accel[2], packet.data.accel[2] )

if __name__ == "__main__":
    unittest.main() # run all tests
    print (unittest.TextTestResult)
