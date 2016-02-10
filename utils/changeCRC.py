import slip
import binascii
import neblina as neb
import neblinasim as nebsim

def genCRC(packetBytes):
    crc = 0
    packetSize = 20
    if len(packetBytes) < packetSize:
        return
    # print(packetBytes)
    packetBytes[2] = b'\xff'
    # print(packetBytes)
    ii = 0
    while ii < packetSize:
        ee = (crc) ^ (ord(packetBytes[ii]))
        ff = (ee) ^ (ee>>4) ^ (ee>>7)
        crc = ((ff<<1)%256) ^ ((ff<<4) % 256)
        ii += 1
    packetBytes[2] = bytes([crc])
    # print(packetBytes)

# Routine to change the CRC of the Neblina sample packets to include the whole
# packet instead of just the data bytes.
def main():

    # File Name Strings
    directoryName = "SampleData/"
    packetTypeName = "Pedometer"
    binaryFileSuffix = "Stream.bin"

    # Construct the file names for different output types
    testInputFileName = directoryName+packetTypeName+binaryFileSuffix
    testOutputCopyFileName = directoryName+packetTypeName+"Regen"+binaryFileSuffix
    testCRCChangeFileName = directoryName+packetTypeName+binaryFileSuffix

    outputBytesList = []
    nebSlip = slip.slip()
    testFile = open(testInputFileName, "rb")
    
    # Determine where to start decoding packets
    firstByte = testFile.read(1)
    startPosition = 1
    firstPacketBytes = b''
    # Find the first packet location
    if firstByte != b'\xc0':
        while (firstByte != b'\xc0'):
            firstPacketBytes += firstByte
            firstByte = testFile.read(1)
            startPosition = startPosition + 1
        firstPacketBytes += b'\xc0'
        testFile.seek(startPosition)
    else:
        testFile.seek(0)

    # Once the location is found, start decoding packets
    fileStream = testFile
    packets = nebSlip.decodePackets(fileStream)
    testFile.close()
    
    # Start writing to the copy and CRC changed packets
    testCopyFile = open(testOutputCopyFileName, "wb")
    testCRCChangeFile = open(testCRCChangeFileName, "wb")
    testCopyFile.write(firstPacketBytes)
    testCRCChangeFile.write(firstPacketBytes)
    for packet in packets:
        packetBytes = [packet[ii:ii+1] for ii in range(len(packet))]
        genCRC(packetBytes)
        contBytes = b''
    
        for byte in packetBytes:
            contBytes += byte
        encodedPacket = nebSlip.encode(packet)
        changedEncodedPacket = nebSlip.encode(contBytes)
    
        testCopyFile.write(encodedPacket)
        testCRCChangeFile.write(changedEncodedPacket)
    testCopyFile.close()

    # Check to see if there are any differences between the original bytes 
    # and the SLIP encoded bytes
    file1 = open(testInputFileName, "rb")
    file2 = open(testOutputCopyFileName, "rb")
    origBytes = file1.read()
    regenBytes = file2.read()
    origBytes = [origBytes[ii:ii+1] for ii in range(len(origBytes))]
    regenBytes = [regenBytes[ii:ii+1] for ii in range(len(regenBytes))]

    for idx,byte in enumerate(origBytes):
        if(byte != regenBytes[idx]):
            print('{0} == {1}'.format(
             origBytes[idx-1], regenBytes[idx-1] ))
            print('origBytes {0} != regenBytes {1} at idx={2}'
                .format(byte, regenBytes[idx], idx))
            break

if __name__ == "__main__":
    main()


