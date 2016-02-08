import os
import cmd
import binascii
import serial
import slip
import neblina as neb

class NeblinaComm(object):
    """docstring for NeblinaComm"""
    def __init__(self, serialcom):
        self.comslip = slip.slip()
        self.sc = serialcom

    def sendCommand(self, subsystem, command, enable=True, **kwargs):
        commandPacket = neb.NebCommandPacket(subsystem, command, enable, **kwargs)
        self.comslip.sendPacketToStream(self.sc, commandPacket.stringEncode())

    def receivePacket(self):
        consoleBytes = self.comslip.receivePacketFromStream(self.sc)
        packet = neb.NebResponsePacket(consoleBytes)
        return packet

    def storePacketsUntil(self, packetType, subSystem, command):
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
        return packetList

    # Helper Functions
    def waitForAck(self, subSystem, command):
        ackPacket = self.waitForPacket(neb.PacketType_Ack, subSystem, command)
        return ackPacket
        
    def waitForPacket(self, packetType, subSystem, command):
        packet = None
        while( (packet == None) or \
            ( (packet.header.packetType != packetType) and (packet.header.packetType != neb.PacketType_ErrorLogResp) ) or \
            packet.header.subSystem != subSystem or \
            packet.header.command != command):
            try:
                packet = self.receivePacket()
            except NotImplementedError as nie:
                print('Dropped bad packet')
                print(nie)
                packet = None
                continue
            except neb.InvalidPacketFormatError as ipfe:
                print(ipfe)
                packet = None
                continue
            except neb.CRCError as crce:
                print('CRCError')
                print(crce)
                packet = None
                continue
            except KeyError as ke:
                packet = None
                print("Tried creating a packet with an invalid subsystem or command")
                print(ke)
                continue
            except TimeoutError as te:
                packet = None
                print('Read timed out.')
                return None
        return packet

    def switchStreamingInterface(self, interface=True):
        # True = UART
        # False = BLE
        self.sendCommand(neb.Subsys_Debug, neb.DebugCmd_SetInterface, interface)
        print('Waiting for the module to switch its interface...')
        packet = self.waitForAck(neb.Subsys_Debug, neb.DebugCmd_SetInterface)
        numTries = 0
        while(packet == None):
            numTries += 1
            if numTries > 5:
                print('The unit is not responding. Exiting...')
                exit()
            print('Trying again...')
            self.sendCommand(neb.Subsys_Debug, neb.DebugCmd_SetInterface, interface)
            packet = self.waitForAck(neb.Subsys_Debug, neb.DebugCmd_SetInterface)

    # Debug Commands
    def motionGetStates(self):
        self.sendCommand(neb.Subsys_Debug, neb.DebugCmd_MotAndFlashRecState)
        self.waitForAck(neb.Subsys_Debug, neb.DebugCmd_MotAndFlashRecState)
        packet = self.waitForPacket(neb.PacketType_RegularResponse,\
            neb.Subsys_Debug, neb.DebugCmd_MotAndFlashRecState)
        return (packet.data.distance, packet.data.force, packet.data.euler, packet.data.quaternion,\
            packet.data.imuData, packet.data.motion, packet.data.steps,packet.data.magData, packet.data.sitStand)

    def flashGetState(self):
        self.sendCommand(neb.Subsys_Debug, neb.DebugCmd_MotAndFlashRecState)
        self.waitForAck(neb.Subsys_Debug, neb.DebugCmd_MotAndFlashRecState)
        packet = self.waitForPacket(neb.PacketType_RegularResponse,\
            neb.Subsys_Debug, neb.DebugCmd_MotAndFlashRecState)
        return neb.MotAndFlashRecStateData.recorderStatusStrings[packet.data.recorderStatus]

    # Motine Engine commands
    def motionStream(self, streamingType, numPackets=None):
        errorList = []
        # Send command to start streaming
        self.sendCommand(neb.Subsys_MotionEngine, streamingType, True)
        packet = self.waitForAck(neb.Subsys_MotionEngine, streamingType)

        # Timeout mechanism.
        numTries = 0
        while (packet == None):
            print('Timed out. Trying again.')
            self.sendCommand(neb.Subsys_MotionEngine, streamingType, True)
            packet = self.waitForAck(neb.Subsys_MotionEngine, streamingType)
            numTries += 1
            if numTries > 5:
                print('Tried {0} times and it doesn\'t respond. Exiting.'.format(numTries))
                exit()
        numTries = 0

        # Stream forever if the number of packets is unspecified (None)
        keepStreaming = (numPackets == None or numPackets > 0)
        while(keepStreaming):
            try:
                packet = self.receivePacket()
                if(packet.header.subSystem == neb.Subsys_MotionEngine and \
                    packet.header.command == streamingType):
                    print(packet.data)
                elif(packet.header.subSystem!=neb.Subsys_Debug):
                    print('Unexpected packet: {0}'.format(packet))
                if(numPackets != None):
                    numPackets -= 1
                keepStreaming = (numPackets == None or numPackets > 0)
            except NotImplementedError as nie:
                print(nie)
            # In the event of Ctrl-C
            except KeyboardInterrupt as ki:
                # self.sendCommand(neb.Subsys_MotionEngine, streamingType, False)
                break
                # return
            except neb.CRCError as crce:
                print('CRCError')
                print(crce)
            except TimeoutError as te:
                if (streamingType!=neb.MotCmd_RotationInfo and streamingType!=neb.MotCmd_Pedometer and streamingType!=neb.MotCmd_FingerGesture):
                    print('Timed out, sending command again.')
                    numTries += 1
                    self.sendCommand(neb.Subsys_MotionEngine, streamingType, True)
                    if numTries > 3:
                        print('Tried {0} times and it doesn\'t respond. Exiting.'.format(numTries))
                        exit()
            except Exception as e:
                print(e)
        # Stop whatever it was streaming
        self.sendCommand(neb.Subsys_MotionEngine, streamingType, False)

    def motionSetDownsample(self, factor):
        self.sendCommand(neb.Subsys_MotionEngine,\
            neb.MotCmd_Downsample, factor)
        self.waitForAck(neb.Subsys_MotionEngine,\
            neb.MotCmd_Downsample)

    def motionSetAccFullScale(self, factor):
        self.sendCommand(neb.Subsys_MotionEngine,\
        neb.MotCmd_AccRange, factor)
        self.waitForAck(neb.Subsys_MotionEngine,\
            neb.MotCmd_AccRange)

    def motionStopStreams(self):
        self.sendCommand(neb.Subsys_MotionEngine,\
            neb.MotCmd_DisableStreaming, True)
        self.waitForAck(neb.Subsys_MotionEngine,\
            neb.MotCmd_DisableStreaming)

    def motionResetTimestamp(self):
        self.sendCommand(neb.Subsys_MotionEngine,\
            neb.MotCmd_ResetTimeStamp, True)
        self.waitForAck(neb.Subsys_MotionEngine,\
            neb.MotCmd_ResetTimeStamp)

    def EEPROMRead(self, readPageNumber):
        self.sendCommand(neb.Subsys_EEPROM, neb.EEPROMCmd_Read, pageNumber=readPageNumber)
        packet = self.waitForAck(neb.Subsys_EEPROM, neb.EEPROMCmd_Read)
        packet = self.waitForPacket(neb.PacketType_RegularResponse, neb.Subsys_EEPROM, neb.EEPROMCmd_Read)
        return packet.data.dataBytes

    def EEPROMWrite(self, writePageNumber, dataString):
        self.sendCommand(neb.Subsys_EEPROM, neb.EEPROMCmd_Write,\
            pageNumber=writePageNumber, dataBytes=dataString)
        packet = self.waitForAck(neb.Subsys_EEPROM, neb.EEPROMCmd_Write)

    def getBatteryLevel(self):
        self.sendCommand(neb.Subsys_PowerManagement,\
            neb.PowCmd_GetBatteryLevel, True)
        
        # Drop all packets until you get an ack
        packet = self.waitForAck(neb.Subsys_PowerManagement,\
            neb.PowCmd_GetBatteryLevel)
        packet = self.waitForPacket(neb.PacketType_RegularResponse,\
            neb.Subsys_PowerManagement,\
            neb.PowCmd_GetBatteryLevel)
        return packet.data.batteryLevel

    def getTemperature(self):
        self.sendCommand(neb.Subsys_PowerManagement,\
            neb.PowCmd_GetTemperature, True)

        # Drop all packets until you get an ack
        packet = self.waitForAck(neb.Subsys_PowerManagement,\
            neb.PowCmd_GetTemperature)
        packet = self.waitForPacket(neb.PacketType_RegularResponse,\
            neb.Subsys_PowerManagement,\
            neb.PowCmd_GetTemperature)
        return packet.data.temperature

    def flashErase(self):
        # Step 1 - Initialization
        self.sendCommand(neb.Subsys_MotionEngine,neb.MotCmd_IMU_Data, True)
        self.sendCommand(neb.Subsys_MotionEngine,neb.MotCmd_DisableStreaming, True)
        print('Sending the DisableAllStreaming command, and waiting for a response...')

        # Step 2 - wait for ack
        self.waitForAck(neb.Subsys_MotionEngine,neb.MotCmd_DisableStreaming)
        print('Acknowledge packet was received!')

        # Step 3 - erase the flash command
        self.sendCommand(neb.Subsys_Storage, neb.StorageCmd_EraseAll, True)
        print('Sent the EraseAll command, and waiting for a response...')

        # Step 4 - wait for ack
        self.waitForAck(neb.Subsys_Storage,neb.StorageCmd_EraseAll)
        print('Acknowledge packet was received! Started erasing... This takes about 3 minutes...')

        # Step 5 - wait for the completion notice
        self.waitForPacket(neb.PacketType_RegularResponse,\
            neb.Subsys_Storage, neb.StorageCmd_EraseAll)

    def flashRecord(self, numSamples, dataType):

        # Step 1 - Initialization
        self.sendCommand(neb.Subsys_MotionEngine,neb.MotCmd_DisableStreaming, True)
        print('Sending the DisableAllStreaming command, and waiting for a response...')

        # Step 2 - wait for ack
        self.waitForAck(neb.Subsys_MotionEngine,neb.MotCmd_DisableStreaming)
        print('Acknowledge packet was received!')

        # Step 3 - Start recording
        self.sendCommand(neb.Subsys_Storage, neb.StorageCmd_Record, True)
        print('Sending the command to start the flash recorder, and waiting for a response...')
        # Step 4 - wait for ack and the session number
        self.waitForAck(neb.Subsys_Storage, neb.StorageCmd_Record)
        packet = self.waitForPacket(neb.PacketType_RegularResponse,\
            neb.Subsys_Storage, neb.StorageCmd_Record)
        print('Acknowledge packet was received with the session number %d!' % packet.data.sessionID)
        sessionID = packet.data.sessionID

        # Step 5 - enable IMU streaming
        self.sendCommand(neb.Subsys_MotionEngine,dataType, True)
        print('Sending the enable IMU streaming command, and waiting for a response...')

        # Step 6 - wait for ack
        self.waitForAck(neb.Subsys_MotionEngine,dataType)
        print('Acknowledge packet was received!')
        
        # Step 7 Receive Packets        
        for x in range(1, numSamples+1):
            packet = self.waitForPacket(neb.PacketType_RegularResponse, neb.Subsys_MotionEngine, dataType)
            print('Recording %d packets, current packet: %d\r' % (numSamples, x), end="", flush=True)
        print('\n')

        # Step 8 - Stop the streaming
        self.sendCommand(neb.Subsys_MotionEngine, dataType, False)
        print('Sending the stop streaming command, and waiting for a response...')

        # Step 9 - wait for ack
        self.waitForAck(neb.Subsys_MotionEngine, dataType)
        print('Acknowledge packet was received!')

        # Step 10 - Stop the recording
        self.sendCommand(neb.Subsys_Storage,neb.StorageCmd_Record, False)
        print('Sending the command to stop the flash recorder, and waiting for a response...')

        # Step 11 - wait for ack and the closed session confirmation
        self.waitForAck(neb.Subsys_Storage,neb.StorageCmd_Record)
        packet = self.waitForPacket(neb.PacketType_RegularResponse,\
            neb.Subsys_Storage, neb.StorageCmd_Record)
        print('The acknowledge packet is received, and session %d is closed successfully' % sessionID)

    def flashPlayback(self, pbSessionID):
        self.sendCommand(neb.Subsys_Storage, neb.StorageCmd_Playback, True, sessionID=pbSessionID)
        print('Sent the start playback command, waiting for response...')
        #wait for confirmation
        packet = self.waitForPacket(neb.PacketType_RegularResponse,\
            neb.Subsys_Storage, neb.StorageCmd_Playback)
        if(packet.header.packetType==neb.PacketType_ErrorLogResp):
            print('Playback failed due to an invalid session number request!')
            return 0
        else:
            pbSessionID = packet.data.sessionID
            print('Playback routine started from session number %d' % pbSessionID);
            packetList = self.storePacketsUntil(neb.PacketType_RegularResponse, neb.Subsys_Storage, neb.StorageCmd_Playback)
            print('Finished playback from session number %d!' % pbSessionID)
            thefile = open('QData', 'w')
            for item in packetList:
                thefile.write("%s\n" % item.stringEncode())
            return len(packetList)

    def flashGetSessions(self):
        self.sendCommand(neb.Subsys_Storage, neb.StorageCmd_NumSessions)
        packet = self.waitForPacket(neb.PacketType_RegularResponse,\
            neb.Subsys_Storage, neb.StorageCmd_NumSessions)
        return packet.data.numSessions

    def flashGetSessionInfo(self, sessionID):
        self.sendCommand(neb.Subsys_Storage, neb.StorageCmd_SessionInfo, sessionID=sessionID)
        packet = self.waitForPacket(neb.PacketType_RegularResponse,\
            neb.Subsys_Storage, neb.StorageCmd_SessionInfo)
        if(packet.data.sessionLength == 0xFFFFFFFF):
            return None
        else:
            return (packet.data.sessionID, packet.data.sessionLength)

    def getLEDs(self, ledIndicesList):
        if type(ledIndicesList) != list:
            print("Use this function with a list of leds you want to know the value as an argument.")
            return
        self.sendCommand(neb.Subsys_LED, neb.LEDCmd_GetVal, ledIndicesList)
        packet = self.waitForPacket(neb.PacketType_RegularResponse,\
            neb.Subsys_LED, neb.LEDCmd_GetVal)
        return packet.data.ledTupleList

    def getLED(self, index):
        self.sendCommand(neb.Subsys_LED, neb.LEDCmd_GetVal, [index])
        packet = self.waitForPacket(neb.PacketType_RegularResponse,\
            neb.Subsys_LED, neb.LEDCmd_GetVal)
        return packet.data.ledTupleList[0]

    def setLEDs(self, ledValues):
        if type(ledValues) != list and type(ledValues[0]) == tuple:
            print("Use this function with a list of tuples as an argument.")
            return
        self.sendCommand(neb.Subsys_LED, neb.LEDCmd_SetVal, ledValueTupleList=ledValues)

    def setLED(self, ledIndex, ledValue):
        self.sendCommand(neb.Subsys_LED, neb.LEDCmd_SetVal, ledValueTupleList=(ledIndex,ledValue) )

    def debugFWVersions(self):
        self.sendCommand(neb.Subsys_Debug, neb.DebugCmd_FWVersions)
        packet = self.waitForPacket(neb.PacketType_RegularResponse, neb.Subsys_Debug, neb.DebugCmd_FWVersions)
        return packet

    def debugUnitTestEnable(self, enable=True):
        self.sendCommand(neb.Subsys_Debug, neb.DebugCmd_StartUnitTestMotion, enable)
        self.waitForAck(neb.Subsys_Debug, neb.DebugCmd_StartUnitTestMotion)

    def debugUnitTestSendVector(self, vectorTimestamp, accelVector, gyroVector, magVector):
        self.sendCommand(neb.Subsys_Debug, neb.DebugCmd_UnitTestMotionData,\
            timestamp=vectorTimestamp,\
            accel=accelVector, gyro=gyroVector,\
            mag=magVector)
        self.waitForPacket(neb.PacketType_RegularResponse, neb.Subsys_Debug, neb.DebugCmd_UnitTestMotionData)





