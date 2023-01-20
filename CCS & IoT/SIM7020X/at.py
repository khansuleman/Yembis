#!/usr/bin/python

import RPi.GPIO as GPIO
import serial
import time

ser = serial.Serial('/dev/ttyS0',115200,timeout=5)
ser.flushInput()

powerKey = 4
command_input = ''
rec_buff = ''

def powerOn(powerKey):
    print('SIM7020E is starting:')
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(powerKey,GPIO.OUT)
    time.sleep(0.1)
    GPIO.output(powerKey,GPIO.HIGH)
    time.sleep(1)
    GPIO.output(powerKey,GPIO.LOW)
    time.sleep(5)

def powerDown(powerKey):
    print('SIM7020E is logging off:')
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(powerKey,GPIO.OUT)
    GPIO.output(powerKey,GPIO.HIGH)
    time.sleep(2)
    GPIO.output(powerKey,GPIO.LOW)
    time.sleep(5)
    print('Good bye')

def checkStart():
    while True:
        # simcom module uart may be fool,so it is better to send much times when it starts.
        ser.write( 'AT\r\n'.encode() )
        time.sleep(1)
        ser.write( 'AT\r\n'.encode() )
        time.sleep(1)
        ser.write( 'AT\r\n'.encode() )
        time.sleep(1)
        if ser.inWaiting():
            time.sleep(0.01)
            recBuff = ser.read(ser.inWaiting())
            print('SIM7020E is ready\r\n')
            print( 'try to start\r\n' + recBuff.decode() )
            if 'OK' in recBuff.decode():
                recBuff = ''
                break
        else:
            powerOn(powerKey)

try:
    checkStart()
    print('Checking start')
    while True:
        command_input = input('Please input the AT command,press Ctrl+C to exit:')
        ser.write((command_input+  '\r\n' ).encode())
        time.sleep(0.1)
        if ser.inWaiting():
            time.sleep(0.01)
            rec_buff = ser.read(ser.inWaiting())
        if rec_buff != '':
            print(rec_buff.decode())
            rec_buff = ''
except Exception as e:
    print(e)
    if ser != None:
        print(ser)
        ser.close()
    powerDown(powerKey)
    GPIO.cleanup()
