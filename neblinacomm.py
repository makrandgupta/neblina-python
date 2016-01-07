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
                    print('waiting and got: {0}'.format(packet.data))
                    packetList.append(packet)
                packet = self.receivePacket()
                # if ( (packet.header.subSystem!=0x01) or (packet.header.packetType!=neb.PacketType_RegularResponse) or (packet.header.command!=0x03) ):
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
            #print('waiting and got: {0}'.format(packet))
            while( ( (packet.header.packetType != packetType) and (packet.header.packetType != neb.PacketType_ErrorLogResp) ) or \
                packet.header.subSystem != subSystem or \
                packet.header.command != command):
                packet = self.receivePacket()
                #print('waiting and got: {0}'.format(packet))
        except NotImplementedError as nie:
            print('Dropped bad packet')
            print(nie)
        except neb.CRCError as crce:
            print('CRCError')
            print(crce)
        except Exception as e:
            print(type(e))
        return packet

    def switchStreamingInterface(self, interface=True):
        # True = UART
        # False = BLE
        self.sendCommand(neb.Subsys_Debug, neb.DebugCmd_SetInterface, interface)
        print('Waiting for the module to switch its interface...')
        self.waitForAck(neb.Subsys_Debug, neb.DebugCmd_SetInterface)

    # Motine Engine commands
    def motionStream(self, streamingType):
        errorList = []
        # Send command to start streaming
        self.sendCommand(neb.Subsys_MotionEngine, streamingType, True)

        packet = self.waitForAck(neb.Subsys_MotionEngine, streamingType)
        print('Got Ack: {0}'.format(packet))

        while(True):
            try:
                packet = self.receivePacket()
                if(packet.header.subSystem == neb.Subsys_MotionEngine and \
                    packet.header.command == streamingType):
                    print(packet.data)
                elif(packet.header.subSystem!=neb.Subsys_Debug):
                    print('Unexpected packet: {0}'.format(packet))
            except NotImplementedError as nie:
                print(nie)
            # In the event of Ctrl-C
            except KeyboardInterrupt as ki:
                # Stop whatever streaming
                self.sendCommand(neb.Subsys_MotionEngine, streamingType, False)
                return
            except neb.CRCError as crce:
                print('CRCError')
                print(crce)
            except Exception as e:
                print(e)

    def motionSetDownsample(self, factor):
        self.sendCommand(neb.Subsys_MotionEngine,\
            neb.MotCmd_Downsample, factor)

    def motionSetAccFullScale(self, factor):
        self.sendCommand(neb.Subsys_MotionEngine,\
        neb.MotCmd_AccRange, factor)

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
        print('ack: {0}'.format(packet))
        packet = self.receivePacket()
        return packet.data.batteryLevel





