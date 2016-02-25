import pyqtgraph as pg
import neblinaAPI as nebapi
import neblina as neb

# parser = argparse.ArgumentParser(description='Graph a file of packets.')

# parser.add_argument('filename', metavar='N', type=int, nargs='+',
#                      help='The name of the file containing the stored binary packet data')


# fileHandle = open('flashSession0', 'rb')

# Build packet list from a file name
packetLists = []
tempPacketList = []
imuPacketList = []
magPacketList = []
rotationPacketList = []
timestamps = [[],[],[]]

with open('flashSession0.bin', "rb") as f:
    packetBytes = f.read(20)
    print(packetBytes)
    if(len(packetBytes) == 0): 
        print('Empty session')
        exit()
    while len(packetBytes) != 0:
        # Build packet list
        packet = neb.NebResponsePacket(packetBytes, checkCRC=False)
        subSystem = packet.header.subSystem
        command = packet.header.command
        if subSystem == neb.Subsys_MotionEngine:
            if(command == neb.MotCmd_MAG_Data):
                magPacketList.append(packet)
            elif(command == neb.MotCmd_IMU_Data):
                imuPacketList.append(packet)
            elif(command == neb.MotCmd_RotationInfo):
                rotationPacketList.append(packet)
        elif subSystem == neb.Subsys_PowerManagement:
            if(command == neb.PowCmd_GetTemperature):
                tempPacketList.append(packet)
        packetBytes = f.read(20)

# print(tempPacketList)
# print(rotationPacketList)
# print(imuPacketList)
# print(magPacketList)
for packet in tempPacketList:
    print(packet)
for packet in magPacketList:
    print(packet)


accelData = []
gyroData = []
magData = []
# timestamps 	= [packet.header.timestamp for packet in packetList]
# magData 	= [packet.data.mag for packet in magPacketList]
# accelData 	= [packet.data.accel for packet in imuPacketList]
# imuData 	= 
# rotations 	= [packet.data.rotationCount]
# tempData 	= [packet.data.temperature for packet in tempPacketList]


# # Populate the initial IMU data list
# for elem in (packet for idx,packet in enumerate(imuPacketList) ):
#     # For all three axis
#     for idx,axisSample in enumerate(elem.data.accel):
#         # Gyro and Accel have same num of axis
#         accelData[idx].append(axisSample)
#         gyroData[idx].append(axisSample)

# # Populate the initial IMU data list
# for elem in (packet for idx,packet in enumerate(magPacketList) ):
#     # For all three axis
#     for idx,axisSample in enumerate(elem.data.accel):
#         # Gyro and Accel have same num of axis
#         accelData[idx].append(axisSample)
#         gyroData[idx].append(axisSample)


# pw = pg.plot(timestamps, yVals, pen='r')  # plot x vs y in red
# pw.plot(xVals, yVals2, pen='b')

# win = pg.GraphicsWindow()  # Automatically generates grids with multiple items
# win.addPlot(timestamps, row=0, col=0)

# pg.show(imageData)  # imageData must be a numpy array with 2 to 4 dimensions
