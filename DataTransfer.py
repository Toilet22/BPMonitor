#-*- coding: utf-8 -*-
import threading
from time import sleep
from PyQt4.QtCore import QObject, SIGNAL
from serial import Serial
from struct import *

class DataTransfer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.qtobj = QObject()
        self.__terminate = True
        
    def open(self, settings):
        try:
            self.serial = Serial(settings["port"], settings["baud"], settings["bytesize"],
                    settings["parity"], settings["stopbits"], settings["timeout"])
            self.serial.flushInput()
            self.serial.flushOutput()
        except Exception, msg:
            return False, msg.message.decode("gbk")
        
        if self.serial._isOpen:
            return True
    
    def terminate(self):
        self.__terminate = True
        
    def __send(self, data, _type):
        self.serial.write(data)
    
    def __recv(self):
        '''
        Read data from serial port.
        Return data after receive data.
        '''
        data = None
        while 1:
            if self.__terminate == True:
                break

            n = self.serial.inWaiting()
            if n>0:
                data = self.serial.read(2*(n/2))
                break

            else:
                sleep(0.02)

        return data

    def startTransfer(self):
    	'''
    	Send a char 's' to the board to start the data transfer.
    	'''
        self.__terminate = False
    	self.serial.write('s')

    def pauseTransfer(self):
    	'''
    	Send a char 'p' to the board to pause the data transfer.
    	'''
        self.__terminate = True
    	self.serial.write('p')

    
    def close(self):
        if self.serial.isOpen():
            self.serial.close()
    
    def run(self):
        while 1:
            data = self.__recv()
            if data:
                self.qtobj.emit(SIGNAL("NewData"), data)

        self.serial.close()