#!/bin/env python3
# -*- coding: utf-8 -*-
import json
# import subprocess
import sys

# from threading import Thread
from urllib.request import urlopen
from http.server import HTTPServer, BaseHTTPRequestHandler, urllib

import cv.stereo as stereo
#TODO: Почему эти импорты не используются?
import cv.roto 
import cv.navigate as nav  

'''МИСМП (Ecobot) — Система технического зрения — Модуль трансляции команд'''

class CVCommandWrapper():
    stereo = stereo.Stereo()

    def get_state(self):
        return self.stereo.get_state()

    def get_decription(self):
        return self.stereo.description

    def get_object_list(self):
        return self.stereo.object_list

    def get_picture(self, camera = 'left'):
        return self.stereo.saveimage(img = self.stereo.snapshot(camera))

    def do_recognize(self, data):
        print(data, file = sys.stderr)
        return self.stereo.recognize('left')

    #TODO: What does this method do?
    def do_find(self, data):
        print(data, file = sys.stderr)
        return dict(a=0)

    def do_scan(self, data):
        print(data, file = sys.stderr)
        A_min = max(-140, int(data['a_min'][0]))
        A_max = min( 140, int(data['a_max'][0]))
        _ = self.stereo.scan(A_min, A_max)
        json.dump(_, open('/tmp/log', 'w'), indent = 2)
        return _

    def do_rotate(self, data):
        print(data, file = sys.stderr)
        try:
            _ = int(data['returnimage'][0])
        except KeyError:
            _ = 0
        return self.stereo.rotate(data, returnimage = _)

    #TODO: What does this method do?
    def do_range(self, data):
        print(data, file = sys.stderr)
        return dict(a=0)

    #TODO: What does this method do?
    def do_cloud(self, data):
        print(data, file = sys.stderr)
        return dict(a=0)

    def from_camera(self, url):
        #'http://192.168.0.122:5555/describe'
        response = urlopen(url)
        return json.loads(response.read().decode("utf-8"))

if __name__ == "__main__":
    pass
