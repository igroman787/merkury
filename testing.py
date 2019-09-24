import time
import serial
import struct
import libscrc # pip3 install libscrc

def CreateSerial(inputPort):
    ser = serial.Serial(
        port=inputPort,
        baudrate=9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        #timeout=1
    )
    ser.isOpen()
    return ser
#end define

def CloseSerial(ser):
    ser.close()
#end define

def WriteHexToSerial(ser, inputHex, isPrintSending = True):
    inputHex = inputHex.replace(' ', '')
    outputBytes = bytes.fromhex(inputHex)
    hexGroup = HexToGroup(inputHex)
    inputLength = len(hexGroup)
    hexGroupString = ' '.join(hexGroup)
    if (isPrintSending == True):
        print("sending[" + str(inputLength) + "]: " + hexGroupString)
    ser.write(outputBytes)
#end define

def ReadHexFromSerial(ser, isPrintGetting = True):
    buffer = b''
    # let wait half a second before reading output (let give device time to answer)
    time.sleep(0.1)
    while ser.inWaiting() > 0:
        buffer += ser.read(1)
    if buffer != '':
        bufferHex = buffer.hex()
        bufferHexGroup = HexToGroup(bufferHex)
        bufferLength = len(bufferHexGroup)
        bufferHexGroupString = ' '.join(bufferHexGroup)
        if (isPrintGetting == True):
            print("getting[" + str(bufferLength) + "]: " + bufferHexGroupString)
    return bufferHexGroupString
#end define

def grouper(iterable, n):
    args = [iter(iterable)] * n
    return zip(*args)
#end define

def HexToGroup(inputHex):
    inputHex = inputHex.replace(' ', '')
    return [''.join(i) for i in grouper(inputHex, 2)]
#end define

def StringToHex(inputString):
    myBytes = inputString.encode("utf-8")
    outputHex = myBytes.hex()
    return outputHex
#end define

def IntToHex(inputInt):
    buffer = format(inputInt, 'x')
    if (len(buffer)%2 != 0):
        buffer = '0' + buffer
    buffer = HexToGroup(buffer)
    outputHex = ' '.join(buffer)
    return outputHex
#end define

def HexToString(inputHex):
    inputBytes = bytes.fromhex(inputHex)
    outputString = inputBytes.decode("utf-8")
    return outputString
#end define

def HexToInt(inputHex):
    inputString = HexToString(inputHex)
    outputInt = int(inputString, 16)
    return outputInt
#end define

def GetCRC16Modbus(inputHex):
    myBytes = bytes.fromhex(inputHex)
    crc16 = libscrc.modbus(myBytes)
    crc16Hex = HexToGroup(IntToHex(crc16))
    crc16Hex.reverse()
    outputHex = ' '.join(crc16Hex)
    return outputHex
#end define

def GenerateOutputHex():
    address = 64
    addressHex = IntToHex(address)
    functionHex = '05 31 00'
    buffer = addressHex + functionHex
    outputHex = buffer + GetCRC16Modbus(buffer)
    return outputHex
#end define


###
### Start of the program
###

# Открываем порт для передачи данных
ser = CreateSerial("/dev/ttyRS485-1")

# Принимаем пакеты информации
#outputHex = '40 01 01 01 01 01 01 01 01 46 42'
#WriteHexToSerial(ser, outputHex)
#ReadHexFromSerial(ser)

#outputHex = GenerateOutputHex()
#WriteHexToSerial(ser, outputHex)
#ReadHexFromSerial(ser)

#inputBuffer = ''
#while True:
#    try:
#        inputHex = ser.read().hex()
#        inputBuffer += inputHex + " "
#        timeText = time.strftime('%d.%m.%Y, %H:%M:%S'.ljust(20, " "))
#        print(timeText, inputHex)
#    except KeyboardInterrupt:
#        print(timeText, inputBuffer)
#        break
#end while

all = '40 00 30 70 40 00 30 70 40 01 01 01 01 01 01 01 01 46 42 40 00 30 70 40 08 05 b7 d7 40 00 40 71 e4 40 08 00 77 d4 40 24 03 32 40 17 09 12 3a 57 40 08 03 37 d5 40 02 03 05 74 d7 40 08 12 f7 d9 40 60 e0 c1 97 07 00 5c 92 40 08 26 f6 0e 40 27 e1 ab ac 40 08 02 f6 15 40 00 01 00 01 b5 cf'
all += '40 01 01 01 01 01 01 01 01 46 42 40 00 30 70 40 08 12 f7 d9 40 60 e0 c1 97 07 00 5c 92 40 05 00 00 05 e5 40 00 00 04 01 ff ff ff ff 00 00 47 00 ff ff ff ff 5c 07 40 05 00 01 c4 25 40 00 00 b7 00 ff ff ff ff 00 00 03 00 ff ff ff ff e3 b1 40 05 00 02 84 24 40 00 00 4d 00 ff ff ff ff 00 00 45 00 ff ff ff ff 17 ed 40 05 00 03 45 e4 40 00 00 00 00 ff ff ff ff 00 00 00 00 ff ff ff ff 54 35 40 05 00 04 04 26 40 00 00 00 00 ff ff ff ff 00 00 00 00 ff ff ff ff 54 35 40 05 00 05 c5 e6 40 00 00 00 00 ff ff ff ff 00 00 00 00 ff ff ff ff 54 35 40 05 60 00 2d e5 40 00 00 56 00 00 00 56 00 00 00 55 00 2d 13 40 05 60 01 ec 25 40 00 00 3d 00 00 00 3c 00 00 00 3c 00 78 12 40 05 60 02 ac 24 40 00 00 19 00 00 00 1a 00 00 00 1a 00 25 cb 40 05 60 03 6d e4 40 00 00 00 00 00 00 00 00 00 00 00 00 fd 2b 40 05 60 04 2c 26 40 00 00 00 00 00 00 00 00 00 00 00 00 fd 2b'
#all = '40010101010101010146424000307040050001c425400000b700ffffffff00000300ffffffffe3b14005000284244000004d00ffffffff00004500ffffffff17ed4005000345e44000000000ffffffff00000000ffffffff54354005000404264000000000ffffffff00000000ffffffff5435'
all = ' '.join(HexToGroup(all))

i = 0
outputHex = ''
while True:
    inputHex = ReadHexFromSerial(ser, False)
    if len(inputHex) == 0:
        i += 1
        outputHex = ' '.join(HexToGroup(all)[0:i])
        WriteHexToSerial(ser, outputHex, False)
    else:
        i = 0
        all = all.replace(outputHex, '', 1)
        all = all.replace(inputHex, '', 1)
        print('>>', outputHex)
        print('<<', inputHex)
        print('')
    if i > len(all):
        break
#end while

CloseSerial(ser)
