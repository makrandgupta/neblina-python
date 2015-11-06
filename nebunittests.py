#!/usr/bin/env python

import unittest
import slip
import binascii
import neblina as neb
import neblinasim as nebsim

# Unit testing class
class ut_NeblinaPackets(unittest.TestCase):
    
    def setUp(self):
        self.nebSlip = slip.slip()

    def getTestStream(self, filepath):
        self.testFile = open(filepath, "rb")

        # Bring the whole file into memory
        fileBytes = self.testFile.read()
        self.testFile.close()

        # Decode the slip packets
        self.nebSlip.append(fileBytes)
        testSlipPackets = self.nebSlip.decode()

        return testSlipPackets

    def buildPacketList(self, packetList):
        packets = []
        errorList = []
        for idx,packetString in enumerate(packetList):
            try:
                nebPacket = neb.NebResponsePacket(packetString)
                # print('Appending {0}'.format(nebPacket))
                packets.append(nebPacket)
            except KeyError as keyError:
                # print('Invalid Motion Engine Code')
                errorList.append(keyError)
            except NotImplementedError as notImplError:
                # print(binascii.hexlify(bytearray(packetString)))
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

    def buildPacketListFromSLIP(self, filename):
        testSlipPackets = self.getTestStream(filename)
        return self.buildPacketList(testSlipPackets)

    def printPackets(self, packetList):
        for packet in packetList:
            print packet

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


    def testDecodeEuler(self):
        print("\n*** Testing Euler Angle Stream Decoding ***")
        packets, errorList = self.buildPacketListFromSLIP("SampleData/EulerAngleStreamShort.bin")

        # Make sure the timestamps are well extracted
        self.assertEquals(packets[10].data.timestamp, 190483824)
        self.assertEquals(packets[20].data.timestamp, 190683824)
        # Make sure the first packet is recognized as garbage
        self.assertEquals(type(errorList[0]), NotImplementedError)
        # Check intentional CRC Errors
        self.assertEquals(type(errorList[1]), neb.CRCError)
        self.assertEquals(errorList[1].expected, 70)
        self.assertEquals(errorList[1].actual, 14)
        self.assertEquals(type(errorList[2]), neb.CRCError)
        self.assertEquals(errorList[2].expected, 112)
        self.assertEquals(errorList[2].actual, 34)
        # Check intentional CRC Errors
        self.assertEquals(type(errorList[1]), neb.CRCError)
        self.assertEquals(errorList[1].expected, 70)
        self.assertEquals(errorList[1].actual, 14)
        self.assertEquals(type(errorList[2]), neb.CRCError)
        self.assertEquals(errorList[2].expected, 112)
        self.assertEquals(errorList[2].actual, 34)
        # Check euler angle decoding
        self.assertEquals(packets[6].data.yaw, -51.6)
        self.assertEquals(packets[6].data.pitch, -60.9)
        self.assertEquals(packets[6].data.roll, 121.5)

    def testDecodePedometer(self):
        print("\n*** Testing Pedometer Decoding ***")
        packets, errorList = self.buildPacketListFromSLIP("SampleData/PedometerStream.bin")
        # Make sure the beginning garbage packet was not recorded
        self.assertEquals(len(packets), 6)
        self.assertEquals(type(errorList[0]), NotImplementedError)
        # Make sure the invalid subsystem error has been detected
        self.assertEquals(type(errorList[1]), neb.InvalidPacketFormatError)
        # Check pedometer data decoding
        self.assertEquals(packets[4].data.timestamp, 19057720)
        self.assertEquals(packets[4].data.stepCount, 4)
        self.assertEquals(packets[4].data.stepsPerMinute, 104)
        self.assertEquals(packets[4].data.walkingDirection, 24.8)

    def testDecodeQuat(self):
        print("\n*** Testing Quaternion Stream Decoding ***")
        packets, errorList = self.buildPacketListFromSLIP("SampleData/QuaternionStream.bin")
        # Make sure the error list is empty
        self.assertEquals(len(errorList), 0)
        # Check quaternion packet decoding
        self.assertEquals(packets[8].data.quaternions[0], 21949)
        self.assertEquals(packets[8].data.quaternions[1], 12649)
        self.assertEquals(packets[8].data.quaternions[2], -20696)
        self.assertEquals(packets[8].data.quaternions[3], -178)

    def testDecodeMAG(self):
        print("\n*** Testing MA Stream Decoding ***")
        packets, errorList = self.buildPacketListFromSLIP("SampleData/MAGStream.bin")
        # Make sure the error list is empty
        self.assertEquals(len(errorList), 0)
        # Check MAG packet decoding
        self.assertEquals(packets[12].data.accel[0], -7527)
        self.assertEquals(packets[12].data.accel[1], 1119)
        self.assertEquals(packets[12].data.accel[2], -15106)
        self.assertEquals(packets[12].data.mag[0], 1009)
        self.assertEquals(packets[12].data.mag[1], -1903)
        self.assertEquals(packets[12].data.mag[2], 3933)

    def testDecodeIMU(self):
        print("\n*** Testing IMU Stream Decoding ***")
        packets, errorList = self.buildPacketListFromSLIP("SampleData/IMUStream.bin")
        # Make sure the error list is empty
        self.assertEquals(len(errorList), 0)
        # Check MAG packet decoding
        self.assertEquals(packets[12].data.timestamp, 12377048)
        self.assertEquals(packets[12].data.accel[0], -12376)
        self.assertEquals(packets[12].data.accel[1], 6870)
        self.assertEquals(packets[12].data.accel[2], -8843)
        self.assertEquals(packets[12].data.gyro[0], -21)
        self.assertEquals(packets[12].data.gyro[1], -23)
        self.assertEquals(packets[12].data.gyro[2], 42)

    def testDecodeTrajectory(self):
        print("\n*** Testing Decode Trajectory Decoding ***")
        packets, errorList = self.buildPacketListFromSLIP("SampleData/TrajectoryDistanceStream.bin")
        # Make sure the error list is empty
        self.assertEquals(len(errorList), 0)
        # Check MAG packet decoding
        self.assertEquals(packets[15].data.timestamp, 36838400)
        self.assertEquals(packets[15].data.eulerAngleErrors[0], -22)
        self.assertEquals(packets[15].data.eulerAngleErrors[1], -1)
        self.assertEquals(packets[15].data.eulerAngleErrors[2], -8)

    def testDecodeExtForce(self):
        print("\n*** Testing External Force Decoding ***")
        packets, errorList = self.buildPacketListFromSLIP("SampleData/ForceStream.bin")
        # Make sure the error list is empty
        self.assertEquals(len(errorList), 0)
        # Check Ext packet decoding
        self.assertEquals(packets[3].data.timestamp, 3878480)
        self.assertEquals(packets[3].data.externalForces[0], 2559)
        self.assertEquals(packets[3].data.externalForces[1], -257)
        self.assertEquals(packets[3].data.externalForces[2], 597)

    def testDecodeMotionState(self):
        print("\n*** Testing Motion State Decoding ***")
        packets, errorList = self.buildPacketListFromSLIP("SampleData/MotionStateStream.bin")
        # Make sure the error list is empty
        self.assertEquals(len(errorList), 0)
        # Check Ext packet decoding
        self.assertEquals(packets[10].data.timestamp, 43738384)
        self.assertEquals(packets[10].data.startStop, True)

    def testEncodePackets(self):
        print("\n*** Testing Encoding of Packets ***")
        packetList = []
        downSampleFactor = 10
        downSampleCommandPacket = neb.NebCommandPacket(neb.Subsys_MotionEngine, neb.MotCmd_Downsample, downSampleFactor)
        packetString = downSampleCommandPacket.stringEncode()
        packetBytes = bytearray(packetString)
        self.assertEquals(len(packetBytes), 20)
        self.assertEquals(packetBytes[0], neb.Subsys_MotionEngine)
        self.assertEquals(packetBytes[1], 16)
        self.assertEquals(packetBytes[3], neb.MotCmd_Downsample)
        self.assertEquals(packetBytes[4], downSampleFactor)

        # Make sure these calls dont cause an exception
        responsePacket = neb.NebCommandPacket(neb.Subsys_MotionEngine, neb.MotCmd_MotionState, True)
        responsePacket = neb.NebCommandPacket(neb.Subsys_MotionEngine, neb.MotCmd_MotionState, False)
        responsePacket = neb.NebCommandPacket(neb.Subsys_MotionEngine, neb.MotCmd_IMU_Data, True)
        responsePacket = neb.NebCommandPacket(neb.Subsys_MotionEngine, neb.MotCmd_Quaternion, True)
        responsePacket = neb.NebCommandPacket(neb.Subsys_MotionEngine, neb.MotCmd_Quaternion, False)
        responsePacket = neb.NebCommandPacket(neb.Subsys_MotionEngine, neb.MotCmd_EulerAngle, True)
        responsePacket = neb.NebCommandPacket(neb.Subsys_MotionEngine, neb.MotCmd_ExtForce, True)
        responsePacket = neb.NebCommandPacket(neb.Subsys_MotionEngine, neb.MotCmd_TrajectoryDistance, True)
        responsePacket = neb.NebCommandPacket(neb.Subsys_MotionEngine, neb.MotCmd_Pedometer, True)
        responsePacket = neb.NebCommandPacket(neb.Subsys_MotionEngine, neb.MotCmd_MAG_Data, True)

    def testCreateEulerPackets(self):
        print("\n*** Testing Encoding and Decoding of Euler Angle Packets ***")
        responsePackets = []
        packets = nebsim.createSpinningObjectPacketList(50.0, 1.0, 2.0, 6.0)
        
        for packet in packets:
            packetString = packet.stringEncode()
            responsePackets.append(neb.NebResponsePacket(packetString))
        for idx,packet in enumerate(responsePackets):
            self.assertEquals(packets[idx].header.subSystem, neb.Subsys_MotionEngine)
            self.assertEquals(packets[idx].header.command, neb.MotCmd_EulerAngle)
            self.assertEquals(packets[idx].data.timestamp, packet.data.timestamp)
            self.assertEquals(packets[idx].data.yaw, packet.data.yaw)
            self.assertEquals(packets[idx].data.pitch, packet.data.pitch)
            self.assertEquals(packets[idx].data.roll, packet.data.roll)

    def testCreatePedometerPackets(self):
        print("\n*** Testing Encoding and Decoding of Pedometer Packets ***")
        responsePackets = []
        packets = nebsim.createWalkingPathPacketList(1000, 61.0, 5.0, 10)
        for packet in packets:
            packetString = packet.stringEncode()
            responsePackets.append(neb.NebResponsePacket(packetString))
        for idx,packet in enumerate(responsePackets):
            self.assertEquals(packets[idx].header.subSystem, neb.Subsys_MotionEngine)
            self.assertEquals(packets[idx].header.command, neb.MotCmd_Pedometer)
            self.assertEquals(packets[idx].data.timestamp, packet.data.timestamp)
            self.assertEquals(packets[idx].data.stepCount, packet.data.stepCount)
            self.assertEquals(packets[idx].data.stepsPerMinute, packet.data.stepsPerMinute)
            self.assertEquals(packets[idx].data.walkingDirection, packet.data.walkingDirection)

    def testCreateIMUPackets(self):
        print("\n*** Testing Encoding and Decoding of IMU Packets ***")
        responsePackets = []
        packets = nebsim.createRandomIMUDataPacketList(50.0, 300, 1.0)
        for packet in packets:
            packetString = packet.stringEncode()
            responsePackets.append(neb.NebResponsePacket(packetString))
        for idx,packet in enumerate(responsePackets):
            self.assertEquals( packets[idx].header.subSystem, neb.Subsys_MotionEngine)
            self.assertEquals( packets[idx].header.command, neb.MotCmd_IMU_Data)
            self.assertEquals( packets[idx].data.timestamp, packet.data.timestamp )
            self.assertEquals( packets[idx].data.accel[0], packet.data.accel[0] )
            self.assertEquals( packets[idx].data.accel[1], packet.data.accel[1] )
            self.assertEquals( packets[idx].data.accel[2], packet.data.accel[2] )
            self.assertEquals( packets[idx].data.gyro[0], packet.data.gyro[0] )
            self.assertEquals( packets[idx].data.gyro[1], packet.data.gyro[1] )
            self.assertEquals( packets[idx].data.gyro[2], packet.data.gyro[2] )





if __name__ == "__main__":
    unittest.main() # run all tests
    print unittest.TextTestResult