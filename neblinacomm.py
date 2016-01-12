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
        while(len(consoleBytes) != 20):
            consoleBytes = self.comslip.receivePacketFromStream(self.sc)
        packet = neb.NebResponsePacket(consoleBytes)
        return packet

    def storePacketsUntil(self, packetType, subSystem, command):
        packetList = []
        packetCounter = 0
        try:
            packet = self.receivePacket()
            #print('waiting and got: {0}'.format(packet))
            while(packet.header.packetType != packetType or \
                packet.header.subSystem != subSystem or \
                packet.header.command != command):
                if (packet.header.subSystem!=neb.Subsys_Debug):
                    packetCounter = packetCounter + 1
                    # print('waiting and got: {0}'.format(packet.data))
                    packetList.append(packet)
                packet = self.receivePacket()
        except NotImplementedError as nie:
            print('Dropped bad packet')
            print(nie)
        except neb.CRCError as crce:
            print('CRCError')
            print(crce)
        except Exception as e:
            print(type(e))
        print('Total IMU Packets Read: %d' %packetCounter)
        return packetList

    # Helper Functions
    def waitForAck(self, subSystem, command):
        ackPacket = self.waitForPacket(neb.PacketType_Ack, subSystem, command)
        return ackPacket
        
    def waitForPacket(self, packetType, subSystem, command):
        try:
            packet = self.receivePacket()
            # print('waiting and got: {0}'.format(packet))
            while( ( (packet.header.packetType != packetType) and (packet.header.packetType != neb.PacketType_ErrorLogResp) ) or \
                packet.header.subSystem != subSystem or \
                packet.header.command != command):
                packet = self.receivePacket()
                # print('waiting and got: {0}'.format(packet))
        except NotImplementedError as nie:
            print('Dropped bad packet')
            print(nie)
        except neb.CRCError as crce:
            print('CRCError')
            print(crce)
        except KeyError as ke:
            print("Key Error")
            print(ke)
            print("Unrecognized packet command or subsystem code")
        return packet

    def switchStreamingInterface(self, interface=True):
        # True = UART
        # False = BLE
        self.sendCommand(neb.Subsys_Debug, neb.DebugCmd_SetInterface, interface)
        print('Waiting for the module to switch its interface...')
        self.waitForAck(neb.Subsys_Debug, neb.DebugCmd_SetInterface)

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
        print('Got Ack: {0}'.format(packet))

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
        
        for x in range(1, numSamples+1):
            packet = self.receivePacket()
            while ((packet.header.subSystem!=neb.Subsys_MotionEngine) or \
                (packet.header.packetType!=neb.PacketType_RegularResponse) or \
                (packet.header.command!= dataType)):
                packet = self.receivePacket()
                continue
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
            return
        else:
            pbSessionID = packet.data.sessionID
            print('Playback routine started from session number %d' % pbSessionID);
            packetList = self.storePacketsUntil(neb.PacketType_RegularResponse, neb.Subsys_Storage, neb.StorageCmd_Playback)
            print('Finished playback from session number %d!' % pbSessionID)
            thefile = open('QData', 'w')
            for item in packetList:
                thefile.write("%s\n" % item.stringEncode())
