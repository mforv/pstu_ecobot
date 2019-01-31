import serial
import sys

from time import sleep 
ROTOADDR  = 0x02 # адрес компьютера
MYADDR    = 0x01 # адрес контроллера
CMD       = 0xaa # признак начала команды
SET_CT    = 0x02 # команда - "встать в положение"
ASK_CT    = 0x03 # команда - "вернуть положение"
SET_FREE  = 0x05
SET_KEEP  = 0x06
ASK_STATE = 0x07
SET_VARS  = 0x08
SET_SPEED = 0x09
ASK_VARS  = 0x0A
SET_C_HOLD= 0x0B
SET_T_HOLD= 0x0C
# ASK_

MSG_STATE = 0x14 # состояние устройства
MSG_READY = 0x15 # устройство готово
MSG_POS   = 0x16 # отправлена позиция

LT = 1
RT = -1
UP = -1
DN = 1

FREE = 0
HOLD = 1
KEEP = 2

class Roto(object):
    port = None
    KA = -11
    KB = 0

    def __init__(self):
        for n in [0,1,2,3,4]:
            p = '/dev/ttyACM%s' % (n)
            print("Trying port %s..." % (p), file=sys.stderr)
            try:
                self.port = serial.Serial(
                    port=p,
                    baudrate=57600,
                    parity='N',
                    stopbits=1,
                    bytesize=8,
                    timeout=20,
                )
                sleep(2)
                self.to_port(self.to_cmd(SET_SPEED, 70, 40))
                state, cPOS, tPOS, DELTA, MODE, tMIN_DEG, tMAX_DEG, cMIN_DEG, cMAX_DEG, tMIN, tMAX, cMIN, cMAX, cSPD, tSPD = self.from_ans(self.from_port())
                assert tSPD == 40
                self.to_port(self.to_cmd(SET_CT, self.KA, self.KB))
                state, cPOS, tPOS = self.from_ans(self.from_port())
                assert state == MSG_POS
                break
            except serial.SerialException as e:
                print(e.with_traceback, file=sys.stderr)
                self.port = None

        assert self.port != None

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

    def ask(self):
        self.to_port(self.to_cmd(ASK_CT))
        _, _a, _b = self.from_ans(self.from_port())
        _a -= self.KA
        _b -= self.KB
        return _, _a, _b


if __name__ == "__main__":
    r = Roto()
    r.move(10,1)
    r.move(10,-10)
    r.move(-10,-10)
    r.move(-10,10)
    r.move(0,0)
