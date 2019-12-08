#!/bin/env python3
# -*- coding: utf-8 -*-

import io
import random
import struct

'''This module is for debugging purposes only, don't use it in production environments'''

class Serial:

    def __init__(self, port):
        self.port = port
        self.buffer = io.BytesIO()

    def process(self):
        command = self.read()
        if command == b'\xae\xae\x00\x00\x00':
            init_sequence = b'\xaa\xaa'
            for i in range(0, 76):
                rand_float = random.uniform(0, 180)
                init_sequence += struct.pack('<f', rand_float)
            init_sequence += b'\xab\xcd\xef\x00'
            self.write(init_sequence)
        elif command[0:2] == b'\xae\xae':
            answer = b'\xaa\xaa'
            answer += struct.pack('<f', random.randint(0, 1))
            self.write(answer)
        else:
            self.write(bytes([0xaa, 0xaa, 0x00, 0x00, 0x00, 0x00]))
            print("Wrong init")
    
    def write(self, string):
        self.buffer.write(bytes(string))
        # Если вдруг потребуется сохранять буфер в файл
        # with open('io', 'wb') as bf:
        #     bf.write(bytes(string))

    def read(self, size=-1) -> bytes:
        bf = self.buffer.getbuffer()
        del self.buffer
        self.buffer = io.BytesIO()
        return bytes(bf)
        # Если вдруг потребуется сохранять буфер в файл
        # with open('io', 'rb') as bf:
        #     return bf.read(size)

class SerialException(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
