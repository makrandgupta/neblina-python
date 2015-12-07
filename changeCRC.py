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


def main():
    outputBytesList = []
    nebSlip = slip.slip()
    testFile = open("SampleData/QuaternionStream.bin", "rb")
    
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

    fileStream = testFile
    packets = nebSlip.decodePackets(fileStream)
    testFile.close()
    
    testCopyFile = open("SampleData/QuaternionStreamRegenerated.bin", "wb")
    testCRCChangeFile = open("SampleData/QuaternionStreamCRCChange.bin", "wb")
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

    file1 = open("SampleData/QuaternionStream.bin", "rb")
    file2 = open("SampleData/QuaternionStreamRegenerated.bin", "rb")

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


