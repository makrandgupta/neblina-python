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

    def sendCommand(self, subsystem, command, enable):
        commandPacket = neb.NebCommandPacket(subsystem, command, enable)
        self.comslip.sendPacketToStream(self.sc, commandPacket.stringEncode())

    def receivePacket(self):
        consoleBytes = self.comslip.receivePacketFromStream(self.sc)
        packet = neb.NebResponsePacket(consoleBytes)
        return packet

    # Helper Functions
    def waitForAck(self):
        try:
            packet = self.receivePacket()
            while(packet.header.packetType != neb.PacketType_Ack):
                packet = self.receivePacket()
        except neb.CRCError as crce:
            print('CRCError')
            print(crce)
        except Exception as e:
            print(e)
            self.waitForAck()
        return packet
        
    def waitForPacket(self, packetType, subSystem, command):
        try:
            packet = self.receivePacket()
            print('waiting and got: {0}'.format(packet))
            while(packet.header.packetType != packetType or \
                packet.header.subSystem != subSystem or \
                packet.header.command != command):
                packet = self.receivePacket()
                print('waiting and got: {0}'.format(packet))
        except NotImplementedError as nie:
            print('Dropped bad packet')
            print(nie)
        except neb.CRCError as crce:
            print('CRCError')
            print(crce)
        except Exception as e:
            print(e)
        return packet

    def motionStream(self, streamingType):
        errorList = []
        # Send command to start streaming
        self.sendCommand(neb.Subsys_MotionEngine, streamingType, True)

        packet = self.waitForAck()
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




