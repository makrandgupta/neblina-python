# Neblina 3D plotting utility
# (C) 2015 Motsai Research Inc.

from visual import *
import time
import NeblinaSim as sim
import NeblinaData as neb
import BLENeblinaStream as nebStream

def main():
    simulatedData = True
    samplingFrequency = 2.0
    samplingPeriod = 1/samplingFrequency

    if simulatedData == True:
        packetList = sim.createSpinningObjectPacketList(samplingFrequency)    
    else:
        ble = nebStream.BLENeblinaStream()

    scene = display(title='Neblina3D Demo',
     x=200, y=200, width=1000, height=800, scale=(0.21,0.21,0.21),
     center=(0,-1,-1), forward=(0,1,0), background=(0,1,1))
    staticframe = frame()
    staticframe.axis = (1,0,0)
    f = frame()
    f.axis = (1,0,0)
    
    # Create 3D models
    cylinder(frame=f, pos=(0,0,0), radius=0.25, length=2,color=color.cyan) # body
    box(frame=f, pos=(1,1,0), length=0.5, width=0.2, height=2, color=color.red)
    box(frame=f, pos=(1,-1,0), length=0.5, width=0.2, height=2, color=color.red)
    box(frame=f, pos=(0,0.25,0), length=0.2, width=0.2, height=0.35, color=color.yellow) # tail wings
    box(frame=f, pos=(0,-0.25,0), length=0.2, width=0.2, height=0.35, color=color.yellow)
    box(frame=f, pos=(0.25 ,0,-0.5), length=0.4, width=0.75, height=0.1, color=color.yellow) # rudder
    pyramid(frame = f, pos=(2,0,0), size=(2,1,0.5)) # cockpit

    # Origin arrows
    arrow(frame=staticframe, pos=(0,0,0), axis=(1.5,0,0), shaftwidth=0.05, color=color.red) # yaw
    arrow(frame=staticframe, pos=(0,0,0), axis=(0,1.5,0), shaftwidth=0.05, color=color.green) # pitch
    arrow(frame=staticframe, pos=(0,0,0), axis=(0,0,1.5), shaftwidth=0.05, color=color.blue) # roll

    ii = 0
    angles = [0]*3
    while True:
        if simulatedData == True:
            angles[0] = packetList[ii].data.yaw
            angles[1] = packetList[ii].data.pitch
            angles[2] = packetList[ii].data.roll
        else:
            angles = ble.getEulerAngles()
        
        f2 = frame()
        f2.axis = (1,0,0) # change orientation of both objects
        f2.origin = (0,0,0)
        f2.rotate(angle = radians(angles[0]+180.0), axis = (0,0,1))
        print(angles[0]+180.0)
        # f2.rotate(angle = radians(angles[1]), axis = (0,1,0))
        # f2.rotate(angle = radians(angles[2]), axis = (1,0,0))
        # print '(y:{0},p:{1},r:{2})'.format(angles[0], angles[1], angles[2])
        if simulatedData == True:
            ii = ii + 1
            ii = ii % len(packetList)
        f.axis = f2.axis
        time.sleep(samplingPeriod)

if __name__ == "__main__":
    main()
