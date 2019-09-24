#!/usr/bin/env python3
# -*- coding: utf_8 -*-

import time
import serial
import libscrc # pip3 install libscrc

def CreateSerial(inputPort):
	ser = serial.Serial(
		port=inputPort,
		baudrate=9600,
		parity=serial.PARITY_NONE,
		stopbits=serial.STOPBITS_ONE,
		bytesize=serial.EIGHTBITS,
		timeout=1
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
	time.sleep(0.5)
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

def GenerateOutputHex(a1, a2, r1, r2):
	address = 64
	addressHex = IntToHex(address)

	a1Hex = IntToHex(a1).replace(' ', '')
	a2Hex = IntToHex(a2).replace(' ', '')
	r1Hex = IntToHex(r1).replace(' ', '')
	r2Hex = IntToHex(r2).replace(' ', '')
	if (len(a1Hex) < 8):
		a1Hex = a1Hex.ljust(8, '0')
	if (len(a2Hex) < 8):
		a2Hex = a2Hex.ljust(8, '0')
	if (len(r1Hex) < 8):
		r1Hex = r1Hex.ljust(8, '0')
	if (len(r2Hex) < 8):
		r2Hex = r2Hex.ljust(8, '0')
	a1Hex = HexToGroup(a1Hex)
	a2Hex = HexToGroup(a2Hex)
	r1Hex = HexToGroup(r1Hex)
	r2Hex = HexToGroup(r2Hex)
	a1Hex.reverse()
	a2Hex.reverse()
	r1Hex.reverse()
	r2Hex.reverse()
	functionHex = ''.join(a1Hex) + ''.join(a2Hex) + ''.join(r1Hex) + ''.join(r2Hex)

	buffer = addressHex + functionHex
	outputHex = buffer + GetCRC16Modbus(buffer)
	return outputHex
#end define

def Reaction(inputHex):
	if (inputHex == '40 00 30 70'): # Тест канала связи
		outputHex = '40 00 30 70'
	elif (inputHex == '40 01 01 01 01 01 01 01 01 46 42'): # Запрос на открытие канала связи со счётчиком
		outputHex = '40 00 30 70'
	elif (inputHex == '00 08 05 b6 03'): # Опросить счётчики, находящиеся в сети и получить их сетевые адреса
		outputHex = '00 00 40 70 30'
	elif (inputHex == '40 08 05 b7 d7'): # Опросить счётчики, находящиеся в сети и получить их сетевые адреса
		outputHex = '40 00 40 71 e4'
	elif (inputHex == '40 08 00 77 d4'): # Прочитать серийный номер и дату выпуска счетчика
		outputHex = '40 24 03 32 40 17 09 12 3a 57'
	elif (inputHex == '40 08 03 37 d5'): # Прочитать версию ПО счетчика
		outputHex = '40 02 03 05 74 d7'
	elif (inputHex == '40 08 12 f7 d9'): # Прочитать варианта исполнения счётчика
		outputHex = '40 60 e0 c1 97 07 00 5c 92'
	elif (inputHex == '40 08 26 f6 0e'): # Прочитать множитель т CRC16 ПО
		outputHex = '40 27 e1 ab ac'
	elif (inputHex == '40 08 02 f6 15'): # Прочитать коэффициент трансформации счетчика
		outputHex = '40 00 01 00 01 b5 cf'
	elif (inputHex == '40 08 12 f7 d9'): # Прочитать варианта исполнения счётчика
		outputHex = '40 60 e0 c1 97 07 00 5c 92'
	elif (inputHex == '40 05 00 01 c4 25'): # Прочитать количество энергии от сброса по 1 тарифу
		outputHex = GenerateOutputHex(273, 0, 0, 0)
	elif (inputHex == '40 05 00 02 84 24'): # Прочитать количество энергии от сброса по 2 тарифу
		outputHex = GenerateOutputHex(283, 0, 0, 0)
	elif (inputHex == '40 05 00 03 45 e4'): # Прочитать количество энергии от сброса по 3 тарифу
		outputHex = GenerateOutputHex(293, 0, 0, 0)
	elif (inputHex == '40 05 00 04 04 26'): # Прочитать количество энергии от сброса по 4 тарифу
		outputHex = GenerateOutputHex(303, 0, 0, 0)
	elif (inputHex == '40 05 60 00 2d e5'): # 
		outputHex = '40 00 00 00 00 00 00 00 00 00 00 00 00 fd 2b'
	elif (inputHex == '40 05 60 01 ec 25'): # 
		outputHex = '40 00 00 00 00 00 00 00 00 00 00 00 00 fd 2b'
	elif (inputHex == '40 05 60 02 ac 24'): # 
		outputHex = '40 00 00 00 00 00 00 00 00 00 00 00 00 fd 2b'
	elif (inputHex == '40 05 60 03 6d e4'): # 
		outputHex = '40 00 00 00 00 00 00 00 00 00 00 00 00 fd 2b'
	elif (inputHex == '40 05 60 04 2c 26'): # 
		outputHex = '40 00 00 00 00 00 00 00 00 00 00 00 00 fd 2b'
	elif (inputHex == '40 05 00 00 05 e5'): # 
		outputHex = '40 00 00 00 00 00 00 00 00 00 00 00 00 fd 2b'
	elif (inputHex == '40 05 00 05 c5 e6'): # 
		outputHex = '40 00 00 00 00 00 00 00 00 00 00 00 00 fd 2b'

	elif (inputHex == '41 00 31 e0'): # 
		outputHex = '41 00 31 e0'
	elif (inputHex == '41 01 01 01 01 01 01 01 01 4b d2'): # 
		outputHex = '41 00 31 e0'
	elif (inputHex == '41 05 00 01 c5 d9'): # 
		outputHex = GenerateOutputHex(274, 0, 0, 0)
	elif (inputHex == '41 05 00 02 85 d8'): # 
		outputHex = GenerateOutputHex(284, 0, 0, 0)
	elif (inputHex == '41 05 00 03 44 18'): # 
		outputHex = GenerateOutputHex(294, 0, 0, 0)
	elif (inputHex == '41 05 00 04 05 da'): # 
		outputHex = GenerateOutputHex(304, 0, 0, 0)


	elif (inputHex == '42 00 31 10'): # 
		outputHex = '42 00 31 10'
	elif (inputHex == '42 01 01 01 01 01 01 01 01 5f 22'): # 
		outputHex = '42 00 31 10'
	elif (inputHex == '42 05 00 01 c5 9d'): # 
		outputHex = GenerateOutputHex(275, 0, 0, 0)
	elif (inputHex == '42 05 00 02 85 9c'): # 
		outputHex = GenerateOutputHex(285, 0, 0, 0)
	elif (inputHex == '42 05 00 03 44 5c'): # 
		outputHex = GenerateOutputHex(295, 0, 0, 0)
	elif (inputHex == '42 05 00 04 05 9e'): # 
		outputHex = GenerateOutputHex(305, 0, 0, 0)


	elif (inputHex == '43 00 30 80'): # 
		outputHex = '43 00 30 80'
	elif (inputHex == '43 01 01 01 01 01 01 01 01 52 b2'): # 
		outputHex = '43 00 30 80'
	elif (inputHex == '43 05 00 01 c4 61'): # 
		outputHex = GenerateOutputHex(276, 0, 0, 0)
	elif (inputHex == '43 05 00 02 84 60'): # 
		outputHex = GenerateOutputHex(286, 0, 0, 0)
	elif (inputHex == '43 05 00 03 45 a0'): # 
		outputHex = GenerateOutputHex(296, 0, 0, 0)
	elif (inputHex == '43 05 00 04 04 62'): # 
		outputHex = GenerateOutputHex(306, 0, 0, 0)


	elif (inputHex == '44 00 32 b0'): # 
		outputHex = '44 00 32 b0'
	elif (inputHex == '44 01 01 01 01 01 01 01 01 74 82'): # 
		outputHex = '44 00 32 b0'
	elif (inputHex == '44 05 00 01 c5 15'): # 
		outputHex = GenerateOutputHex(277, 0, 0, 0)
	elif (inputHex == '44 05 00 02 85 14'): # 
		outputHex = GenerateOutputHex(287, 0, 0, 0)
	elif (inputHex == '44 05 00 03 44 d4'): # 
		outputHex = GenerateOutputHex(297, 0, 0, 0)
	elif (inputHex == '44 05 00 04 05 16'): # 
		outputHex = GenerateOutputHex(307, 0, 0, 0)


	elif (inputHex == '45 00 33 20'): # 
		outputHex = '45 00 33 20'
	elif (inputHex == '45 01 01 01 01 01 01 01 01 79 12'): # 
		outputHex = '45 00 33 20'
	elif (inputHex == '45 05 00 01 c4 e9'): # 
		outputHex = GenerateOutputHex(278, 0, 0, 0)
	elif (inputHex == '45 05 00 02 84 e8'): # 
		outputHex = GenerateOutputHex(288, 0, 0, 0)
	elif (inputHex == '45 05 00 03 45 28'): # 
		outputHex = GenerateOutputHex(298, 0, 0, 0)
	elif (inputHex == '45 05 00 04 04 ea'): # 
		outputHex = GenerateOutputHex(308, 0, 0, 0)
	else:
		outputHex = ''
	return outputHex
#end define


###
### Start of the program
###

# Открываем порт для передачи данных
ser = CreateSerial("/dev/ttyRS485-1")

i = 0
inputBuffer = b''
inputBuffer_old = b''
while True:
	i += 1
	inputBuffer += ser.read(1)
	buffer = inputBuffer.hex()
	buffer = HexToGroup(buffer)
	inputHex = ' '.join(buffer)
	outputHex = Reaction(inputHex)
	if (len(outputHex) > 0):
		i = 0
		inputBuffer = b''
		WriteHexToSerial(ser, outputHex)
	if (len(inputBuffer) != len(inputBuffer_old)):
		i = 0
	if (i > 3):
		i = 0
		inputBuffer = b''
	inputBuffer_old = inputBuffer
#end while

CloseSerial(ser)
