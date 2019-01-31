import serial
import sys

#Ver M1.01
#Edited by Masalskiy M from 20.11.2018

from time import sleep
ROTOADDR  = 0x02; # адрес компьютера
MYADDR    = 0x01; # адрес контроллера
CMD       = 0xaa; # признак начала команды
SET_CT    = 0x02; # команда - "встать в положение"
ASK_CT    = 0x03; # команда - "вернуть положение"
SET_FREE  = 0x05;
SET_KEEP  = 0x06;
ASK_STATE = 0x07;
SET_VARS  = 0x08;
SET_SPEED = 0x09;
ASK_VARS  = 0x0A;
SET_C_HOLD= 0x0B;
SET_T_HOLD= 0x0C;
SET_LASER_ON= 0x0D;
SET_LASER_OFF= 0x0E;
ASK_USONIC= 0x0F;
ASK_VLMM= 0x10;
SET_CTZ    = 0x11; # команда - "встать в положение Z"
ASK_CTZ    = 0x12; # команда - "вернуть положение Z"
# ASK_

MSG_STATE = 0x14; # состояние устройства
MSG_READY = 0x15; # устройство готово
MSG_POS   = 0x16; # отправлена позиция

LT = 1;
RT = -1;
UP = -1;
DN = 1;

FREE = 0;
HOLD = 1;
KEEP = 2;

class Roto(object):
    port = None
    KA = 0
    KB = 0
    KZ = 0

    def __init__(self):
        pass

    def to_port(self, string):
        print('>>> %s' % (string), file=sys.stderr)
        self.port.write(string)

    def from_port(self):
        _ = self.port.readline()
        print('<<< %s' % (_), file=sys.stderr)
        return str(_)

    def to_cmd(self, *args):
        s = "%s %s " % (ROTOADDR, CMD, )
        for arg in args:
            s += str(arg) + " "
        s = s.strip()
        s += "\n"
        return bytes(s,'ascii')

    def from_ans(self, string=""):
        cmd, host, state = 0,0,0
        try:
            _ = [int(_) for _ in string.strip("'b\\n\\r").split(' ')]
            print(_, file=sys.stderr)
            host, cmd, state = _[:3]
        except serial.SerialException as e:
            print(e.with_traceback, file=sys.stderr)
        assert cmd == CMD and host == MYADDR
        return [state] + _[3:]

    def move(self, c, t):
        if type(c) == list: c = int(c[0])
        if type(t) == list: t = int(t[0])
        self.to_port(self.to_cmd(SET_CT,c + self.KA, t + self.KB))
        return self.from_ans(self.from_port())
    def moveZ(self, z):
        if type(z) == list: z = int(z[0])
        self.to_port(self.to_cmd(SET_CTZ,z + self.KZ))
        return self.from_ans(self.from_port())
#-----------------Пример добавления ф-ции------------
    def laserOn(self):
        self.to_port(self.to_cmd(SET_LASER_ON))
        return self.from_ans(self.from_port())
    def laserOff(self):
        self.to_port(self.to_cmd(SET_LASER_OFF))
        return self.from_ans(self.from_port())
#----------------------------------------------------
    def ask_uS(self):
        self.to_port(self.to_cmd(ASK_USONIC))
        _, _a = self.from_ans(self.from_port())
        return _, _a
    def ask_VL(self):
        self.to_port(self.to_cmd(ASK_VLMM))
        _, _a = self.from_ans(self.from_port())
        return _, _a
    def ask(self):
        self.to_port(self.to_cmd(ASK_CT))
        _, _a, _b, _z = self.from_ans(self.from_port())
        _a -= self.KA
        _b -= self.KB
        _z -= self.KZ
        return _, _a, _b,_z


if __name__ == "__main__":
    r = Roto()
    r.ask()
    #-------------Запуск примера----------
    #r.laserOn()
    #sleep(3)
    #r.laserOff()
    #-------------------------------------
    #r.move(150,150)
    #r.move(10,-10)
    #r.move(-10,-10)
    #r.move(-10,10)
    #r.move(0,0)
    
    # r.move(180, 180)
    # r.moveZ(50)
    # r.laserOn()
    # sleep(10)
    # r.move(120, 150)
    # r.moveZ(10)
    # sleep(10)
    # r.move(180, 180)
    # r.moveZ(50)
    # sleep(10)
    r.laserOff()
    
    # r.moveZ(-30)
    # sleep(2)
    # r.move(150, 180)
    # sleep(2)
    # r.move(180, 180)
    # r.moveZ(30)
    # sleep(2)
    # r.move(180, 150)
    # r.laserOn()
    # r.moveZ(-30)
    # sleep(1)
    # print(r.ask_VL())
    # r.move(180, 180)
    # r.moveZ(-30)
    # sleep(3)
    # print(r.ask_uS())
    # r.laserOff()
    # r.moveZ(60)
