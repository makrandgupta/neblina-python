import sys
import math
import numpy as np
import btle
import struct
import binascii
import neblina as neb
import time

Battery_Service_UUID = "0000180F-0000-1000-8000-00805f9b34fb"
EulerAngle_Service_UUID = "0DF9F021-1532-11E5-8960-0002A5D5C51B"

class NeblinaDelegate(btle.DefaultDelegate):
    def __init__(self,params):
        self.Name = params
        btle.DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        print(cHandle)
        print(data)
        print(self.Name)

class BLENeblinaStream(object):
    """docstring for BLENeblinaStream"""
    def __init__(self):
        self.periph = btle.Peripheral("F5:F2:09:FC:41:FC","random") # Promoty3
        #self.periph = btle.Peripheral("E6:2E:9B:39:53:2E","random") # Promoty4
        # self.periph = btle.Peripheral("F0:12:84:D8:04:53","random") # Heblina

        print("Setup delegate")
        self.periph.setDelegate( NeblinaDelegate('Neblina') )

        services = self.periph.getServices()
        for x in xrange(1,len(services)):
            print(str(services[x]))

        try:
            print("Trying to get Descriptors")
            desc = self.periph.getDescriptors(1,7)
            for descriptor in desc:
                print(descriptor)
        except btle.BTLEException as e:
            print("Exception =>",e)
    
    def getEulerAngles(self):
        try:
            serv = self.periph.getServiceByUUID(EulerAngle_Service_UUID)
            buff = [0]*20
            angle = [0]*3
            char = serv.getCharacteristics()
            packetString = char[0].read()

            try:
                nebPacket = neb.NebResponsePacket(packetString)
                angle[0] = nebPacket.data.yaw
                angle[1] = nebPacket.data.pitch
                angle[2] = nebPacket.data.roll
            except KeyError as keyError:
                # print('Invalid Motion Engine Code')
                print(keyError)
            except NotImplementedError as notImplError:
                # print(binascii.hexlify(bytearray(packetString)))
                # print('Got a non-standard packet at #{0}'\
                    # .format(idx))
                print(notImplError)
            except neb.CRCError as crcError:
                print(crcError)
                # print('Got a CRCError at packet #{0}'\
                    # .format(idx))
            except neb.InvalidPacketFormatError as invPacketError:
                print(invPacketError)


            return angle

        except btle.BTLEException as e:
            print("Exception =>",e)
            self.periph.disconnect()
            


class NeblinaDelegate(btle.DefaultDelegate):
    def __init__(self,params):
        self.Name = params
        btle.DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        print(cHandle)
        print(data)
        print(self.Name)


if(__name__ == "__main__"):
    outfile = open('data.bin','wb')
    count = 0;
    #periph = btle.Peripheral("E6:2E:9B:39:53:2E","random") # Promoty4
    periph = btle.Peripheral("F5:F2:09:FC:41:FC","random") # Promoty3

    service = periph.getServiceByUUID(EulerAngle_Service_UUID)
    char = service.getCharacteristics()
    while True:
        packetString = char[0].read()
        print binascii.hexlify(packetString)
        outfile.write(packetString)
        outfile.close();
        time.sleep(0.1);
        outfile = open('data.bin', 'wb')

    outfile.close()




	
