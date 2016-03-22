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

import sys
import os
import cmd
import binascii
import serial
import slip
import logging

from neblina import *
from neblinaCommandPacket import NebCommandPacket
from neblinaError import *
from neblinaResponsePacket import NebResponsePacket

###################################################################################


class NeblinaAPI(object):
    """docstring for NeblinaComm"""
    def __init__(self, serialcom):
        self.comslip = slip.slip()
        self.sc = serialcom

    def sendCommand(self, subsystem, command, enable=True, **kwargs):
        commandPacket = NebCommandPacket(subsystem, command, enable, **kwargs)
        self.comslip.sendPacketToStream(self.sc, commandPacket.stringEncode())

    def receivePacket(self):
        consoleBytes = self.comslip.receivePacketFromStream(self.sc)
        packet = NebResponsePacket(consoleBytes)
        return packet

    # Store all packets until a particular packet and discard that packet
    def storePacketsUntil(self, packetType, subSystem, command):
        packetList = []
        packetCounter = 0
        packet = None
        #logging.debug('waiting and got: {0}'.format(packet))
        while(packet == None or \
              packet.header.packetType != packetType or \
              packet.header.subSystem != subSystem or \
              packet.header.command != command):
            try:
                if (packet != None and packet.header.subSystem != SubSystem.Debug):
                    packetList.append(packet)
                    logging.debug('Received {0} packets \r'.format(len(packetList)) , end="", flush=True)
                packet = self.receivePacket()
                # logging.debug('waiting and got: {0}'.format(packet.data))
            except NotImplementedError as e:
                packet = None
                logging.error("Dropped bad packet : " + str(e))
                continue
            except KeyError as e:
                packet = None
                logging.error("Tried creating a packet with an invalid subsystem or command : " + str(e))
                continue
            except CRCError as e:
                packet = None
                logging.error("CRCError : " + str(e))
                continue
            except Exception as e:
                packet = None
                logging.error("Exception : " + str(e))
                continue
            except:
                packet = None
                logging.error("Unexpected error : ", sys.exc_info()[0])
                continue

        logging.info('\nTotal IMU Packets Read: {0}'.format(len(packetList)))
        return packetList

    # Store all packets until a particular packet and keep that packet at the end of the list
    def storePacketsUntilInclusive(self, packetType, subSystem, command):
        packetList = []
        packetCounter = 0
        packet = None
        #print('waiting and got: {0}'.format(packet))
        while( packet == None or \
                packet.header.packetType != packetType or \
                packet.header.subSystem != subSystem or \
                packet.header.command != command):
            try:
                if (packet != None and \
                    packet.header.subSystem != neb.Subsys_Debug):
                    packetList.append(packet)
                    print('Received {0} packets \r'.format(len(packetList)) , end="", flush=True)
                packet = self.receivePacket()
                # print('waiting and got: {0}'.format(packet.data))
            except NotImplementedError as nie:
                packet = None
                print('Dropped bad packet')
                print(nie)
                continue
            except KeyError as ke:
                packet = None
                print("Tried creating a packet with an invalid subsystem or command")
                print(ke)
            except neb.CRCError as crce:
                packet = None
                print('CRCError')
                print(crce)
                continue
            except Exception as e:
                packet = None
                print(type(e))
                continue
        print('\nTotal IMU Packets Read: {0}'.format(len(packetList)))
        packetList.append(packet)
        print('Last packet: {0}'.format(packet))
        return packetList

    # Helper Functions
    def waitForAck(self, subSystem, command):
        ackPacket = self.waitForPacket(PacketType.Ack, subSystem, command)
        return ackPacket

    def waitForPacket(self, packetType, subSystem, command):
        packet = None
        while( (packet == None) or \
            ( (packet.header.packetType != packetType) and (packet.header.packetType != PacketType.ErrorLogResp) ) or \
            packet.header.subSystem != subSystem or \
            packet.header.command != command):
            try:
                packet = self.receivePacket()
            except NotImplementedError as e:
                logging.error("Dropped bad packet.")
                packet = None
                continue
            except InvalidPacketFormatError as e:
                logging.error("InvalidPacketFormatError.")
                packet = None
                continue
            except CRCError as e:
                logging.error("CRCError : " + str(e))
                packet = None
                continue
            except KeyError as e:
                logging.error("Tried creating a packet with an invalid subsystem or command : " + str(e))
                packet = None
                continue
            except TimeoutError as e:
                logging.error('Read timed out.')
                return None
            except KeyboardInterrupt as e:
                logging.error("KeyboardInterrupt.")
                exit()
            except:
                packet = None
                logging.error("Unexpected error : ", sys.exc_info()[0])
                continue
        return packet

    def setStreamingInterface(self, interface=Interface.BLE):
        self.sendCommand(SubSystem.Debug, Commands.Debug.SetInterface, interface)
        logging.debug('Waiting for the module to switch its interface...')
        packet = self.waitForAck(SubSystem.Debug, Commands.Debug.SetInterface)
        numTries = 0
        while(packet == None):
            numTries += 1
            if numTries > 5:
                logging.error('The unit is not responding. Exiting...')
                exit()
            logging.warning('Trying again...')
            self.sendCommand(SubSystem.Debug, Commands.Debug.SetInterface, interface)
            packet = self.waitForAck(SubSystem.Debug, Commands.Debug.SetInterface)

    def stopAllStreams(self):
        """
            Stop all streams.
            For now, calls motionStopStreams which stop all motion streams.
            In the future, this function will stop all streams which are not associated with motion.
            This could be done with a single new commands or multiple separate commands.
        """
        self.motionStopStreams()

    # Debug Commands
    def motionGetStates(self):
        self.sendCommand(SubSystem.Debug, Commands.Debug.MotAndFlashRecState)
        self.waitForAck(SubSystem.Debug, Commands.Debug.MotAndFlashRecState)
        packet = self.waitForPacket(PacketType.RegularResponse,\
            SubSystem.Debug, Commands.Debug.MotAndFlashRecState)
        return (packet.data.distance, packet.data.force, packet.data.euler, packet.data.quaternion,\
            packet.data.imuData, packet.data.motion, packet.data.steps,packet.data.magData, packet.data.sitStand)

    def flashGetState(self):
        self.sendCommand(SubSystem.Debug, Commands.Debug.MotAndFlashRecState)
        self.waitForAck(SubSystem.Debug, Commands.Debug.MotAndFlashRecState)
        packet = self.waitForPacket(PacketType.RegularResponse,\
            SubSystem.Debug, Commands.Debug.MotAndFlashRecState)
        return MotAndFlashRecStateData.recorderStatusStrings[packet.data.recorderStatus]

    # Motine Engine commands
    def motionStream(self, streamingType, numPackets=None):
        errorList = []
        # Send command to start streaming
        self.sendCommand(SubSystem.Motion, streamingType, True)
        packet = self.waitForAck(SubSystem.Motion, streamingType)

        # Timeout mechanism.
        numTries = 0
        while (packet == None):
            logging.warning('Timed out. Trying again.')
            self.sendCommand(SubSystem.Motion, streamingType, True)
            packet = self.waitForAck(SubSystem.Motion, streamingType)
            numTries += 1
            if numTries > 5:
                logging.error('Tried {0} times and it doesn\'t respond. Exiting.'.format(numTries))
                exit()
        numTries = 0

        # Stream forever if the number of packets is unspecified (None)
        keepStreaming = (numPackets == None or numPackets > 0)
        while(keepStreaming):
            try:
                packet = self.receivePacket()
                if(packet.header.subSystem == SubSystem.Motion and \
                    packet.header.command == streamingType):
                    logging.info(packet.data)
                elif(packet.header.subSystem!=SubSystem.Debug):
                    logging.warning('Unexpected packet: {0}'.format(packet))
                if(numPackets != None):
                    numPackets -= 1
                keepStreaming = (numPackets == None or numPackets > 0)
            except NotImplementedError as nie:
                logging.error("NotImplementedError : " + str(nie))
            # In the event of Ctrl-C
            except KeyboardInterrupt as ki:
                break
            except CRCError as e:
                logging.error("CRCError : " + str(e))
            except TimeoutError as te:
                if (streamingType!=Commands.Motion.RotationInfo and streamingType!=Commands.Motion.Pedometer and streamingType!=Commands.Motion.FingerGesture and streamingType!=Commands.Motion.TrajectoryInfo):
                    logging.warning('Timed out, sending command again.')
                    numTries += 1
                    self.sendCommand(SubSystem.Motion, streamingType, True)
                    if numTries > 3:
                        logging.error('Tried {0} times and it doesn\'t respond. Exiting.'.format(numTries))
                        exit()
            except Exception as e:
                logging.error("Exception : " + str(e))
        # Stop whatever it was streaming
        self.sendCommand(SubSystem.Motion, streamingType, False)

    def motionSetDownsample(self, factor):
        self.sendCommand(SubSystem.Motion,\
            Commands.Motion.Downsample, factor)
        self.waitForAck(SubSystem.Motion,\
            Commands.Motion.Downsample)

    def motionSetAccFullScale(self, factor):
        self.sendCommand(SubSystem.Motion,\
            Commands.Motion.AccRange, factor)
        self.waitForAck(SubSystem.Motion,\
            Commands.Motion.AccRange)

    def motionStopStreams(self):
        self.sendCommand(SubSystem.Motion,\
            Commands.Motion.DisableStreaming, True)
        self.waitForAck(SubSystem.Motion,\
            Commands.Motion.DisableStreaming)

    def motionResetTimestamp(self):
        self.sendCommand(SubSystem.Motion,\
            Commands.Motion.ResetTimeStamp, True)
        self.waitForAck(SubSystem.Motion,\
            Commands.Motion.ResetTimeStamp)

    def EEPROMRead(self, readPageNumber):
        self.sendCommand(SubSystem.EEPROM, Commands.EEPROM.Read, pageNumber=readPageNumber)
        packet = self.waitForAck(SubSystem.EEPROM, Commands.EEPROM.Read)
        packet = self.waitForPacket(PacketType.RegularResponse, SubSystem.EEPROM, Commands.EEPROM.Read)
        return packet.data.dataBytes

    def EEPROMWrite(self, writePageNumber, dataString):
        self.sendCommand(SubSystem.EEPROM, Commands.EEPROM.Write,\
            pageNumber=writePageNumber, dataBytes=dataString)
        packet = self.waitForAck(SubSystem.EEPROM, Commands.EEPROM.Write)

    def getBatteryLevel(self):
        self.sendCommand(SubSystem.Power,\
            Commands.Power.GetBatteryLevel, True)

        # Drop all packets until you get an ack
        packet = self.waitForAck(SubSystem.Power,\
            Commands.Power.GetBatteryLevel)
        packet = self.waitForPacket(PacketType.RegularResponse,\
            SubSystem.Power,\
            Commands.Power.GetBatteryLevel)
        return packet.data.batteryLevel

    def getTemperature(self):
        self.sendCommand(SubSystem.Power,\
            Commands.Power.GetTemperature, True)

        # Drop all packets until you get an ack
        packet = self.waitForAck(SubSystem.Power,\
            Commands.Power.GetTemperature)
        packet = self.waitForPacket(PacketType.RegularResponse,\
            SubSystem.Power,\
            Commands.Power.GetTemperature)
        return packet.data.temperature

    def flashErase(self):
        # Step 1 - Initialization
        self.sendCommand(SubSystem.Motion,Commands.Motion.IMU_Data, True)
        self.sendCommand(SubSystem.Motion,Commands.Motion.DisableStreaming, True)
        logging.debug('Sending the DisableAllStreaming command, and waiting for a response...')

        # Step 2 - wait for ack
        self.waitForAck(SubSystem.Motion,Commands.Motion.DisableStreaming)
        logging.debug('Acknowledge packet was received!')

        # Step 3 - erase the flash command
        self.sendCommand(SubSystem.Storage, Commands.Storage.EraseAll, True)
        logging.debug('Sent the EraseAll command, and waiting for a response...')

        # Step 4 - wait for ack
        self.waitForAck(SubSystem.Storage,Commands.Storage.EraseAll)
        logging.debug("Acknowledge packet was received!")
        logging.info("Started erasing... This takes about 3 minutes...")

        # Step 5 - wait for the completion notice
        self.waitForPacket(PacketType.RegularResponse,\
            SubSystem.Storage, Commands.Storage.EraseAll)

    def flashRecord(self, numSamples, dataType):

        # Step 1 - Initialization
        self.sendCommand(SubSystem.Motion,Commands.Motion.DisableStreaming, True)
        logging.debug('Sending the DisableAllStreaming command, and waiting for a response...')

        # Step 2 - wait for ack
        self.waitForAck(SubSystem.Motion,Commands.Motion.DisableStreaming)
        logging.debug('Acknowledge packet was received!')

        # Step 3 - Start recording
        self.sendCommand(SubSystem.Storage, Commands.Storage.Record, True)
        logging.debug('Sending the command to start the flash recorder, and waiting for a response...')
        # Step 4 - wait for ack and the session number
        self.waitForAck(SubSystem.Storage, Commands.Storage.Record)
        packet = self.waitForPacket(PacketType.RegularResponse,\
            SubSystem.Storage, Commands.Storage.Record)
        logging.debug('Acknowledge packet was received with the session number %d!' % packet.data.sessionID)
        sessionID = packet.data.sessionID

        # Step 5 - enable IMU streaming
        self.sendCommand(SubSystem.Motion,dataType, True)
        logging.debug('Sending the enable IMU streaming command, and waiting for a response...')

        # Step 6 - wait for ack
        self.waitForAck(SubSystem.Motion,dataType)
        logging.debug('Acknowledge packet was received!')

        # Step 7 Receive Packets
        for x in range(1, numSamples+1):
            packet = self.waitForPacket(PacketType.RegularResponse, SubSystem.Motion, dataType)
            logging.info('Recording %d packets, current packet: %d\r' % (numSamples, x), end="", flush=True)
        logging.info('\n')

        # Step 8 - Stop the streaming
        self.sendCommand(SubSystem.Motion, dataType, False)
        logging.debug('Sending the stop streaming command, and waiting for a response...')

        # Step 9 - wait for ack
        self.waitForAck(SubSystem.Motion, dataType)
        logging.debug('Acknowledge packet was received!')

        # Step 10 - Stop the recording
        self.sendCommand(SubSystem.Storage,Commands.Storage.Record, False)
        logging.debug('Sending the command to stop the flash recorder, and waiting for a response...')

        # Step 11 - wait for ack and the closed session confirmation
        self.waitForAck(SubSystem.Storage,Commands.Storage.Record)
        packet = self.waitForPacket(PacketType.RegularResponse,\
            SubSystem.Storage, Commands.Storage.Record)
        logging.debug("The acknowledge packet is received")
        logging.info("Session {0} is closed successfully".format(sessionID))

    def flashPlayback(self, pbSessionID, destinationFileName=None):
        self.sendCommand(SubSystem.Storage, Commands.Storage.Playback, True, sessionID=pbSessionID)
        logging.debug('Sent the start playback command, waiting for response...')
        #wait for confirmation
        packet = self.waitForPacket(PacketType.RegularResponse,\
            SubSystem.Storage, Commands.Storage.Playback)
        if(packet.header.packetType==PacketType.ErrorLogResp):
            logging.error('Playback failed due to an invalid session number request!')
            return 0
        else:
            pbSessionID = packet.data.sessionID
            logging.info('Playback routine started from session number %d' % pbSessionID);
            packetList = self.storePacketsUntil(PacketType.RegularResponse, SubSystem.Storage, Commands.Storage.Playback)
            logging.info('Finished playback from session number %d!' % pbSessionID)
            if(destinationFileName != None):
                destinationFileName += '{0}.bin'.format(pbSessionID)
                print(pbSessionID)
                thefile = open(destinationFileName, 'wb')
                for item in packetList:
                    packetEncoding = item.stringEncode()
                    thefile.write(packetEncoding)
                thefile.close()
            return len(packetList)

    def flashGetSessions(self):
        self.sendCommand(SubSystem.Storage, Commands.Storage.NumSessions)
        packet = self.waitForPacket(PacketType.RegularResponse,\
            SubSystem.Storage, Commands.Storage.NumSessions)
        return packet.data.numSessions

    def flashGetSessionInfo(self, sessionID):
        self.sendCommand(SubSystem.Storage, Commands.Storage.SessionInfo, sessionID=sessionID)
        packet = self.waitForPacket(PacketType.RegularResponse,\
            SubSystem.Storage, Commands.Storage.SessionInfo)
        if(packet.data.sessionLength == 0xFFFFFFFF):
            return None
        else:
            return (packet.data.sessionID, packet.data.sessionLength)

    def getLEDs(self, ledIndicesList):
        if type(ledIndicesList) != list:
            logging.warning("Use this function with a list of leds you want to know the value as an argument.")
            return
        self.sendCommand(SubSystem.LED, Commands.LED.GetVal, ledIndicesList)
        packet = self.waitForPacket(PacketType.RegularResponse,\
            SubSystem.LED, Commands.LED.GetVal)
        return packet.data.ledTupleList

    def getLED(self, index):
        self.sendCommand(SubSystem.LED, Commands.LED.GetVal, [index])
        packet = self.waitForPacket(PacketType.RegularResponse,\
            SubSystem.LED, Commands.LED.GetVal)
        return packet.data.ledTupleList[0]

    def setLEDs(self, ledValues):
        if type(ledValues) != list and type(ledValues[0]) == tuple:
            logging.warning("Use this function with a list of tuples as an argument.")
            return
        self.sendCommand(SubSystem.LED, Commands.LED.SetVal, ledValueTupleList=ledValues)

    def setLED(self, ledIndex, ledValue):
        ledValues = [(ledIndex,ledValue)]
        self.sendCommand(SubSystem.LED, Commands.LED.SetVal, ledValueTupleList=ledValues )

    def debugFWVersions(self):
        self.sendCommand(SubSystem.Debug, Commands.Debug.FWVersions)
        versionPacket = self.waitForPacket(PacketType.RegularResponse,
            SubSystem.Debug, Commands.Debug.FWVersions)
        return (versionPacket.data.apiRelease,
                versionPacket.data.mcuFWVersion,
                versionPacket.data.bleFWVersion,
                versionPacket.data.deviceID)

    def debugAPIRelease(self):
        versionTuple = self.debugFWVersions()
        return versionTuple[0]

    def debugMCUfwVersion(self):
        versionTuple = self.debugFWVersions()
        return versionTuple[1]

    def debugBLEfwVersion(self):
        versionTuple = self.debugFWVersions()
        return versionTuple[2]

    def debugDeviceID(self):
        versionTuple = self.debugFWVersions()
        return versionTuple[3]

    def debugUnitTestEnable(self, enable=True):
        self.sendCommand(SubSystem.Debug, Commands.Debug.StartUnitTestMotion, enable)
        self.waitForAck(SubSystem.Debug, Commands.Debug.StartUnitTestMotion)

    def debugUnitTestSendVector(self, vectorTimestamp, accelVector, gyroVector, magVector):
        self.sendCommand(SubSystem.Debug, Commands.Debug.UnitTestMotionData,\
            timestamp=vectorTimestamp,\
            accel=accelVector, gyro=gyroVector,\
            mag=magVector)
        self.waitForPacket(PacketType.RegularResponse, SubSystem.Debug, Commands.Debug.UnitTestMotionData)





