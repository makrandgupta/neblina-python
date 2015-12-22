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

    def sendCommand(self, subsystem, command, enable, **kwargs):
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
        try:
            packet = self.receivePacket()
            #print('waiting and got: {0}'.format(packet))
            while(packet.header.packetType != packetType or \
                packet.header.subSystem != subSystem or \
                packet.header.command != command):
                packetList.append(packet)
                packet = self.receivePacket()
                print('waiting and got: {0}'.format(packet.data))
        except NotImplementedError as nie:
            print('Dropped bad packet')
            print(nie)
        except neb.CRCError as crce:
            print('CRCError')
            print(crce)
        except Exception as e:
            print(type(e))
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
                else:
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

    def EEPROMRead(self, readPageNumber):
        self.sendCommand(neb.Subsys_EEPROM, neb.EEPROMCmd_Read, True, pageNumber=readPageNumber)
        packet = self.waitForAck(neb.Subsys_EEPROM, neb.EEPROMCmd_Read)
        packet = self.waitForPacket(neb.PacketType_RegularResponse, neb.Subsys_EEPROM, neb.EEPROMCmd_Read)
        return packet.data.dataBytes

    def EEPROMWrite(self, writePageNumber, dataString):
        self.sendCommand(neb.Subsys_EEPROM, neb.EEPROMCmd_Write, False,\
            pageNumber=writePageNumber, dataBytes=dataString)
        packet = self.waitForAck(neb.Subsys_EEPROM, neb.EEPROMCmd_Write)





