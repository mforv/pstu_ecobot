#!/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import struct
import test_serial as serial  # TODO: Replace with pyserial after debugging

'''МИСМП (Ecobot) — Обертка для команд микроконтроллера'''

ports = []

def to_port(port: int, buffer: bytes):
    if sys.version_info >= (3, 8):
        print(f'> {buffer.hex(":")}', file=sys.stderr)  # Fancy byte separators only for Python 3.8+
    else:
        print(f'> {buffer.hex()}', file=sys.stderr)
    ports[port].write(buffer)

def from_port(port: int) -> bytes:
    data = ports[port].read()
    if sys.version_info >= (3, 8):
        print(f'> {data.hex(":")}', file=sys.stderr)  # Fancy byte separators only for Python 3.8+
    else:
        print(f'> {data.hex()}', file=sys.stderr)
    return data

def send_command(device_port: int, command_code: int, message=None):
    '''Отправляем на указанный порт заданный код команды и сообщение
    :param device_port: int
    :param command_code: hex int
    :param message: iterable of floats or None
    '''
    command = b'\xae\xae' + bytes([command_code])
    b_message = bytes()
    if message is not None:
        for msg in message:
            b_message += struct.pack('<f', msg)
    command += bytes([len(b_message)])
    command += b_message +  b'\x00'
    to_port(device_port, command)

def get_answer(device_port: int):
    '''Получаем код ответа с заданного порта'''
    b_answer = from_port(device_port)
    if b_answer[0:2] == b'\xaa\xaa':
        answer_code = struct.unpack('<f', b_answer[2:6])
        # print('Answer', answer_code[0])
        return answer_code[0]
    else:
        print('Wrong sync sequence!')
        return 0.0

def ask(command_code: 0x00, message=None):
    '''Отправляем на указанный порт заданный код команды и сообщение, получаем код ответа
    :param command_code: hex int
    :param message: iterable of floats
    :returns: An answer code
    '''
    device_port = 0
    send_command(device_port, command_code, message)
    # time.sleep(1)
    ports[0].process()  #TODO: Remove after debugging
    return get_answer(device_port)

def initialize():
    '''Команда инициализации, возвращает текущие состояния всех устройств'''
    send_command(0, 0)
    # time.sleep(1)
    ports[0].process()  #TODO: Remove after debugging
    init_answer = from_port(0)
    if init_answer[0:2] == b'\xaa\xaa':
        parsed_answer = []
        byte_start, byte_end = 2, 6
        chunk = init_answer[byte_start:byte_end]
        while chunk != b'\xab\xcd\xef\x00':
            value = struct.unpack('<f', chunk)
            parsed_answer.append(value[0])
            byte_start += 4
            byte_end += 4
            chunk = init_answer[byte_start:byte_end]
        # print(parsed_answer, len(parsed_answer))
        return parsed_answer
    else:
        print('Wrong sync sequence!')
        return []

def assign_port(max_amount=1):
    for n in range(max_amount):
        p = f'/dev/ttyUSB{n}'
        print(f'Trying port {p}...', file=sys.stderr)
        try:
            ports.append(serial.Serial(port=p))
            # time.sleep(2)
            break
        except serial.SerialException as e:
            print(e, file=sys.stderr)
            # ports.append(None)

if __name__ == "__main__":
    assign_port()
    initialize()
    print(ask(0x0D, [1.0]))
    print(ask(0x12, [37.3, 44.7, -50.4]))
    print(ask(0x0A))
    print(ask(0x13))

