# Neblina Protocol Simulated output
# (C) 2015 Motsai Research Inc.

import binascii
import json
import random
import math
import os

from neblinaResponsePacket import NebResponsePacket as nebResponsePacket

usPerSecond = 1000000

def main():
    packetList = []
    spinningPacketStringList = []
    walkingPacketStringList = []
    imuDataPacketStringList = []
    samplingFrequency = 50.0

    # Create spinning object packets
    spinning = createSpinningObjectPacketList(samplingFrequency, 0.5, 0.0, 0.0)
    # Get last packet in the list and use its timestamp to determine the timestamp of the next rotation
    startTimestamp = spinning[-1].data.timestamp + int(1/samplingFrequency)
    spinning += createSpinningObjectPacketList(samplingFrequency, 0.0, 0.5, 0.0, startTimestamp)
    startTimestamp = spinning[-1].data.timestamp + int(1/samplingFrequency)
    spinning += createSpinningObjectPacketList(samplingFrequency, 0.0, 0.0, 0.5, startTimestamp)

    walking = createWalkingPathPacketList( 100, 40.0, 5.0, 3, -44.0 )
    imuData = createRandomIMUDataPacketList( 50, 300 )

    # Create a list of the encoded rotating packets
    for packet in spinning:
        packetString = packet.stringEncode()
        spinningPacketStringList.append( packetString )
        # print( packet.data )

    for packet in walking:
        packetString = packet.stringEncode()
        walkingPacketStringList.append( packetString )
        # print( packet.data )

    for packet in imuData:
        packetString = packet.stringEncode()
        imuDataPacketStringList.append( packetString )
        # print( packet.data )

    # Generate the data directory
    if not os.path.exists('./generated'):
        os.makedirs('./generated')

    anglesFile = open("./generated/euleranglePackets.bin", "wb")
    for packet in spinningPacketStringList:
        anglesFile.write(packet)
    anglesFile.close()

    walkingFile = open("./generated/pedometerPackets.bin", "wb")
    for packet in walkingPacketStringList:
        walkingFile.write(packet)
    walkingFile.close()

    imuFile = open("./generated/imuPackets.bin", "wb")
    for packet in imuDataPacketStringList:
        imuFile.write(packet)
    imuFile.close()


# Takes a Neblina packet list and converts the packets to JSON format
def convertToJson(packetList):
    jsonPacketList = []
    for idx,packet in enumerate(packetList):
        d = json.dumps(packet, default=lambda o: o.__dict__)
        jsonPacketList.append(obj)
        # obj = json.loads(d)
        # print(obj)
    return jsonPacketList

def createTestAnglePacketList():
    packetList = [0]*4
    packet = neb.NebResponsePacket.createEulerAngleResponsePacket(\
    timestamp, yawDegrees, pitchDegrees, rollDegrees)


def createWalkingPathPacketList(numSteps, averageSPM=61.0, maxDegreesDeviation=2.5, turns=2, startingPath=0.0):
    packetList = []
    timestamp = 0
    stepCount = 0
    walkingDirection = startingPath
    timestampDivergence = 0.5 # Half a second time divergence

    # Choose at which step numbers the turns should occur
    turnStepIndices = []
    for ii in range(0,turns):
        turnStepIndices.append( random.randint(1, numSteps) )

    for ii in range(0,numSteps):
        # Choose a new random direction
        if(ii in turnStepIndices ):
            angleVariation = random.randrange(-90, 91, 180)
        else:
            angleVariation = random.gauss(0, 1.0)
            if( angleVariation > maxDegreesDeviation ):
                angleVariation = maxDegreesDeviation
            elif ( angleVariation < -maxDegreesDeviation ):
                angleVariation = -maxDegreesDeviation

        # Update new walking direction
        walkingDirection = walkingDirection+angleVariation
        # Make sure the direction stays within -180 and +180
        if( walkingDirection > 180.0 ):
            walkingDirection -= 360
        elif ( walkingDirection < -180.0 ):
            walkingDirection += 360

        # Choose a new timestamp
        secondsPerStep = 60.0/averageSPM
        timeDelta = random.gauss(secondsPerStep, 0.05)
        if (timeDelta < 0.1):
            timeDelta = 0.1
        elif(timeDelta > secondsPerStep+0.1):
            timeDelta = secondsPerStep+0.1
        timestamp = timestamp + int(secondsPerStep*usPerSecond)
        stepsPerMinute = int(60.0/timeDelta)

        # Build the packet object
        packet = nebResponsePacket.createPedometerResponsePacket(\
        timestamp, ii, stepsPerMinute, walkingDirection)
        packetList.append(packet)

    return packetList


# RPS = Rotation Per Second
def createSpinningObjectPacketList(samplingFrequency = 50.0,\
                                yawRPS=0.5, pitchRPS=0.0, rollRPS=0.0, startTimestamp = 0):
    packetList = []
    degreesPerSecond = [0]*3
    degreesPerSecond[0] = yawRPS*360
    degreesPerSecond[1] = pitchRPS*360
    degreesPerSecond[2] = rollRPS*360
    samplingPeriod = 1/samplingFrequency

    # Figure out the longest rotation without it being 0 dps
    # Remove the non-moving elements
    movingRotationsList = [x for x in degreesPerSecond if x != 0.0]

    # If it isn't moving, create a dummy packet list
    if len(movingRotationsList) == 0:
        time = range(0, 100)
    else :
        # Find the lowest DPS
        slowestMovingRotation = min(movingRotationsList)
        # Create enough samples for the longest rotation.
        numSamples = int(samplingFrequency*(1/slowestMovingRotation)*360)
        time = range(0, numSamples)

    for n in time:
        # A rotation is a sawtooth function that starts at 0 for n=0
        yawDegrees  =   round((((degreesPerSecond[0]*samplingPeriod*n) + 180 )% 360 ) - 180, 2 )
        pitchDegrees =  round((((degreesPerSecond[1]*samplingPeriod*n) + 90 )% 180 ) - 90, 2 )
        rollDegrees =   round((((degreesPerSecond[2]*samplingPeriod*n) + 180 )% 360 ) - 180, 2 )
        # Simulate the heading 'demo mode' activated
        demoDegrees =   round((((1.5*degreesPerSecond[0]*samplingPeriod*n) + 180 )% 360 ) - 180, 2 )
        timestamp =  ( n*samplingPeriod*usPerSecond ) + startTimestamp
        packet = nebResponsePacket.createEulerAngleResponsePacket(\
            timestamp, yawDegrees, pitchDegrees, rollDegrees, demoDegrees)
        packetList.append( packet )

    return packetList


def createRandomIMUDataPacketList(samplingFrequency = 50.0, numSamples = 300, freq = 1.0):
    packetList = []
    accel = [0]*3
    gyro = [0]*3
    timestamp = 0
    maxIMUValue = 16739 #TBD

    for n in range(numSamples):
        accel[0] = maxIMUValue*math.sin(  (2*math.pi*freq*n)/samplingFrequency+(math.pi/4) ) + random.gauss(0,maxIMUValue/10)
        accel[1] = maxIMUValue*math.sin(  (2*math.pi*freq*n)/samplingFrequency+(math.pi/2) ) + random.gauss(0,maxIMUValue/10)
        accel[2] = maxIMUValue*math.sin( 2*math.pi*freq*n/samplingFrequency ) + random.gauss(0,maxIMUValue/10)
        gyro[0] = maxIMUValue*math.cos( (2*math.pi*freq*n)/samplingFrequency+(math.pi/3)  ) + random.gauss(0,maxIMUValue/10)
        gyro[1] = maxIMUValue*math.cos( (2*math.pi*freq*n)/samplingFrequency+(7*math.pi/12)  ) + random.gauss(0,maxIMUValue/10)
        gyro[2] = maxIMUValue*math.cos( (2*math.pi*freq*n)/samplingFrequency+(9*math.pi/15)  ) + random.gauss(0,maxIMUValue/10)
        timestamp += int( (1.0/samplingFrequency)*usPerSecond )

        packet = nebResponsePacket.createIMUResponsePacket(timestamp, accel, gyro)
        packetList.append( packet )

    return packetList

def createRandomMAGDataPacketList(samplingFrequency = 50.0, numSamples = 300, freq = 1.0):
    packetList = []
    mag = [0]*3
    accel = [0]*3
    timestamp = 0
    maxMAGValue = 10000 #TBD

    for n in range(numSamples):
        mag[0] = maxMAGValue*math.sin(  (2*math.pi*freq*n)/samplingFrequency+(math.pi/4) ) + random.gauss(0,maxMAGValue/20)
        mag[1] = maxMAGValue*math.sin(  (2*math.pi*freq*n)/samplingFrequency+(math.pi/2) ) + random.gauss(0,maxMAGValue/20)
        mag[2] = maxMAGValue*math.sin( 2*math.pi*freq*n/samplingFrequency ) + random.gauss(0,maxMAGValue/20)
        accel[0] = maxMAGValue*math.cos( (2*math.pi*freq*n)/samplingFrequency+(math.pi/3)  ) + random.gauss(0,maxMAGValue/20)
        accel[1] = maxMAGValue*math.cos( (2*math.pi*freq*n)/samplingFrequency+(7*math.pi/12)  ) + random.gauss(0,maxMAGValue/20)
        accel[2] = maxMAGValue*math.cos( (2*math.pi*freq*n)/samplingFrequency+(9*math.pi/15)  ) + random.gauss(0,maxMAGValue/20)
        timestamp += int( (1.0/samplingFrequency)*usPerSecond )

        packet = nebResponsePacket.createMAGResponsePacket(timestamp, mag, accel)
        packetList.append( packet )

    return packetList



if __name__ == "__main__":
    main()

