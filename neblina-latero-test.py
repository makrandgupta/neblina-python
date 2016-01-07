import socket
import unittest
import array
import struct
import time
import serial
#this code works with python 3.4

LATERO_ADR = ('192.168.87.98', 8900)
MAGIC_HEAD = 'CA'	# Magic byte indicating Latero Frame
VER_HEAD = '11'		# Version 1, Rev 1 of protocol
TYPE_HEAD = '01' 	#full = '01', IO = '02', RAW = '03'
SEQ_HEAD = '0000'

#test parameters
tolerance = 3 # percent, voltage tolerance
zeroThresh = 0.1 # threshold for 0 volt

class LateroOverInternet:
    def __init__(self):

        print('\n\ninitializing...')
        self.sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        self.sock.settimeout(5)

        self.IO_Out = 0x0000
        self.DAC_Out = [0x0000,0x0000,0x0000,0x0000]
        self.Blade = [0x00] * 64
        self.VBatt = []

    def BuildPacket(self):
        self.Packet = []

        # Packet header
        self.Packet.extend(bytearray.fromhex(MAGIC_HEAD + VER_HEAD + 
                                              TYPE_HEAD + SEQ_HEAD))             
        # Packet body
        self.Packet.extend(struct.pack("!5H",self.IO_Out,self.DAC_Out[0],
                                         self.DAC_Out[1],self.DAC_Out[2],
                                         self.DAC_Out[3]))
        self.Packet += self.Blade
        #print('packet built')
        
    def ExchangePacket(self):
        self.BuildPacket()
        self.sent = self.sock.sendto(bytearray(self.Packet), LATERO_ADR)
        #print('I sent these',self.sent,'bytes to the latero:',self.Packet)
        self.data, self.server = self.sock.recvfrom(4096) # Latero not answering

        self.ReHeader = struct.unpack('!3BH',self.data[:5])
        self.IO_In = struct.unpack('!H',self.data[5:7])
        self.Ctrlstatus = struct.unpack('!H',self.data[7:9])
        self.IOstatus = struct.unpack('!H',self.data[9:11])
        self.Quad_In = struct.unpack('!4I',self.data[11:27])
        self.Adc_In_Raw = struct.unpack('!4h',self.data[27:35])
        self.Adc_In = [round(x/32768.0*10.0,3) for x in self.Adc_In_Raw]
        
        
latero = LateroOverInternet()
print('starting unit test')
#latero.DAC_Out = [0x2B89,0x0000,0x0000,0x0000] #DAC 1 set to 3.3V
latero.DAC_Out = [0x0300,0x547B,0x28F6,0x35C3] #simulate neblina voltage, remove this
latero.ExchangePacket()
print('\npacket sent and got a response from latero at',latero.server)

class JigTest(unittest.TestCase):
    def test1_CurrentDraw(self):
        print('Voltage read test')
        time.sleep(0.828)
        latero.ExchangePacket()

        print('\n-->ADC 1=',latero.Adc_In[0],'V (current draw test)')
        print('-->Neblina is drawing', latero.Adc_In[0]*100.0,'mA')
        self.assertLess(zeroThresh,latero.Adc_In[0],"\n\nno voltage detected")


    def test2_6V6(self): 
        print('-->ADC 2=',latero.Adc_In[1],'V (6V6 test)')
        self.assertLess(zeroThresh,latero.Adc_In[1],"\n\nno voltage detected")
        self.assertAlmostEqual(6.6,latero.Adc_In[1],delta=6.6/100*tolerance,
            msg='\n\n6.6V is not in the '+str(tolerance)+"% tolerance zone")        

    def test3_3V2(self):        
        print('-->ADC 3=',latero.Adc_In[2],'V (3V2 test)')
        self.assertLess(zeroThresh,latero.Adc_In[2],"\n\nno voltage detected")
        self.assertAlmostEqual(3.2,latero.Adc_In[2],delta=3.2/100*tolerance,
            msg='\n\n3.2V is not in the '+str(tolerance)+"% tolerance zone")        
        
    def test4_VBATT(self):        
        print('-->ADC 4=',latero.Adc_In[3],'V (Battery voltage test)')
        latero.VBatt = latero.Adc_In[3]
        self.assertLess(zeroThresh,latero.Adc_In[3],"\n\nno voltage/battery detected")
        self.assertGreater(4.2,latero.Adc_In[3],
                           "\n\nNeblina is over charging battery or no battery is connected")
        self.assertLess(3.4,latero.Adc_In[3],"\n\nNeblina is not charging battery")


        
    def test5_CurrentChg(self):    
        print('\nswitched relay, reading new voltage')   
        latero.IO_Out = 0x0001 #relay turned on
        latero.DAC_Out = [0x0DD3,0x4000,0x170A,0x3503] #simulate neblina voltage

        latero.ExchangePacket()
        time.sleep(0.828)
        latero.ExchangePacket()

        print('\n-->ADC 1 =',latero.Adc_In[0],'V (charging current test)')
        print('-->Neblina is charging the battery at',round(latero.Adc_In[0]/0.0027,2),'mA')
        self.assertLess(-0.02,latero.Adc_In[0],"\n\nNeblina is powered by VBatt (it shouldn't)")
        self.assertNotAlmostEqual(latero.Adc_In[0],0,delta=zeroThresh,
            msg="\n\nNeblina is NOT charging the battery")

    def test6_5V(self):
        print('-->ADC 2 =',latero.Adc_In[1],'V (5V test)')
        self.assertLess(zeroThresh,latero.Adc_In[1],"\n\nno voltage detected")
        self.assertAlmostEqual(5,latero.Adc_In[1],delta=5/100*tolerance,
            msg='\n\n5V is not in the '+str(tolerance)+"% tolerance zone")        

    def test7_1V8(self):        
        print('-->ADC 3 =',latero.Adc_In[2],'V (1V8 test)')
        self.assertLess(zeroThresh,latero.Adc_In[2],"\n\nno voltage detected")
        self.assertAlmostEqual(1.8,latero.Adc_In[2],delta=1.8/100*tolerance,
            msg='\n\n1.8V is not in the '+str(tolerance)+"% tolerance zone")        
        
    def test8_VSYS(self):        
        print('-->ADC 4 =',latero.Adc_In[3],'V (PMIC VSYS voltage test)')
        self.assertLess(zeroThresh,latero.Adc_In[3],"\n\nno voltage detected")
        self.assertGreater(latero.Adc_In[3],latero.VBatt-0.1,
            '\n\nVSYS is too low, it should >= to VBatt)')


suite = unittest.TestLoader().loadTestsFromTestCase(JigTest)
unittest.TextTestRunner(verbosity=1).run(suite)

'''
print('Header received:',latero.ReHeader)
print('IO input:',latero.IO_In)
print('Ctrl status:',latero.Ctrlstatus)
print('IO status',latero.IOstatus)
print('Quadrature:',latero.Quad_In)
print('ADC input:', latero.Adc_In)  
'''

latero.IO_Out = 0x0000
latero.DAC_Out = [0x0000,0x0000,0x0000,0x0000]
latero.ExchangePacket()
latero.sock.close()
