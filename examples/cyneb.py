
import neblina as neb
import neblinaAPI as nebapi
import neblinasim as nsim
import slip
import serial

comslip = slip.slip()

# Try to open the serial COM port
comPortName = 'COM3'
sc = None
while sc is None:
    try:
        sc = serial.Serial(port=comPortName,baudrate=115200, timeout=1.5)
    except serial.serialutil.SerialException as se:
        if 'Device or resource busy:' in se.__str__():
            print('Opening COM port is taking a little while, please stand by...')
        else:
            print('se: {0}'.format(se))
        time.sleep(1)

imuDataPacketList = createRandomIMUDataPacketList()

for packet in imuDataPacketList:
    comslip.sendPacketToStream(sc, packet.stringEncode())
    time.sleep(0.5)
