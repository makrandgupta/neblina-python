import neblinaAPI as nebapi
import neblina as neb

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

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

with open('flashSession1.bin1.bin', "rb") as f:
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

# for packet in tempPacketList:
#     print(packet)
# for packet in magPacketList:
#     print(packet)

# magDataLists = [[],[],[]]
# magXYZ = [packet.data.mag for packet in magPacketList]
# magTimestamps = [packet.data.timestamp for packet in magPacketList]
# magDataLists[0] = [ magData[0] for magData in magXYZ ]
# magDataLists[1] = [ magData[1] for magData in magXYZ ]
# magDataLists[2] = [ magData[2] for magData in magXYZ ]
# print(len(magTimestamps))
# print(len(magDataLists[0]))
# plt.title('Magnetometer readings')
# plt.plot(magTimestamps, magDataLists[0], color='blue', lw=2, label='X')
# plt.plot(magTimestamps, magDataLists[1], color='green', lw=2, label='Y')
# plt.plot(magTimestamps, magDataLists[2], color='red', lw=2, label='Z')
# red_patch = mpatches.Patch(color='blue', label='Mag X')
# blue_patch = mpatches.Patch(color='green', label='Mag Y')
# green_patch = mpatches.Patch(color='red', label='Mag Z')
# plt.legend(handles=[red_patch, blue_patch, green_patch])


# plt.xlabel('Timestamp (milliseconds)')
# plt.ylabel('Tesla (T)')
# plt.grid(True)
# plt.show()

accelDataLists = [[],[],[]]
accelXYZ = [packet.data.accel for packet in imuPacketList]
gyroXYZ = [packet.data.gyro for packet in imuPacketList]
imuTimestamps = [packet.data.timestamp for packet in imuPacketList]
accelDataLists[0] = [ accelData[0] for accelData in accelXYZ ]
accelDataLists[1] = [ accelData[1] for accelData in accelXYZ ]
accelDataLists[2] = [ accelData[2] for accelData in accelXYZ ]
plt.title('Accelerometer readings')
plt.plot(imuTimestamps, accelDataLists[0], color='blue', lw=2, label='X')
plt.plot(imuTimestamps, accelDataLists[1], color='green', lw=2, label='Y')
plt.plot(imuTimestamps, accelDataLists[2], color='red', lw=2, label='Z')
red_patch = mpatches.Patch(color='blue', label='Accel X')
blue_patch = mpatches.Patch(color='green', label='Accel Y')
green_patch = mpatches.Patch(color='red', label='Accel Z')
plt.legend(handles=[red_patch, blue_patch, green_patch])
plt.xlabel('Timestamp (milliseconds)')
plt.ylabel('Acceleration (g)')
plt.grid(True)
plt.show()
