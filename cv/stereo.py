# -*- coding: utf-8 -*-
import os
import json
import numpy as np
import scipy as sp
import cv2
# import magic
import sys

from urllib import request
from copy import copy as cpobj
from datetime import datetime
from math import tan, radians, degrees
from time import sleep
from threading import Thread

from roto import Roto
from student import Student

class Stereo:
    state = dict(
        state = 'NORMAL_OP',
        errors = dict(
            rec = 0, # ошибки распознавания
            rng = 0, # ошибки измерения
            rot = 0, # ошибки поворота
        ),
        pos = dict(
            a = 0, # курс
            b = 0, # возвышение
        )
    )
    
    description = dict(
        cameras = dict(
            left  = dict(
                A = radians(62),
                B = radians(45),
                W = 640,
                H = 480,
                id = 2, 
                transform = [[[10,10],[600,10],[600,400]],[[10,20],[600,30],[600,420]]],
                picture = '/static/busy_.gif'),
            right = dict(
                A = radians(62),
                B = radians(45),
                W = 640,
                H = 480,
                id = 4, 
                transform = [[[10,10],[600,10],[600,400]],[[10,20],[600,30],[600,420]]],
                picture = '/static/busy_.gif'),
            wide  = 'http://192.168.1.6:8080/photoaf.jpg',
        ),
        roto = dict(
            a = dict(min = -130, max = 130),
            b = dict(min =  -20, max =  30),
        ),
    )

    object_list = dict()

    A_cam = radians(62) 
    B_cam = radians(45)
    
    def __init__(self):
        self.object_list = self.get_object_list('./bd')
        self.img_list = self.get_img_list(self.object_list)
        self.r = Roto()
        self.A_cam = self.description['cameras']['left']['A']
        self.B_cam = self.description['cameras']['left']['B']
        self.W_cam = self.description['cameras']['left']['W']
        self.H_cam = self.description['cameras']['left']['H']

    def z_range(self, d, y = 0):
        try:
            x  = 1 / d
            k1 = -4490183.80012
            k2 =   473388.00812
            k3 =        0.89120
            k4 =        0.11269
            k5 = 0.0009 * y + 0.784

            return (k4 + k1 * x**3 + k2 * x**2 + k3 * x) / k5
        except ZeroDivisionError:
            return 0

    def xy_to_ab_radians(self, xy = [0,0], AB = [0,0]):
        Xo, Yo = xy[0] - self.W_cam / 2, self.H_cam / 2 - xy[1]
        Ao, Bo = AB[0] - 0.0017 * Xo, AB[1] + 0.0019 * Yo
        return Ao, Bo

    def xy_to_ab(self):
        pass

    def pix_to_angle(self, pix):
        return 0.0017 * pix

    def getDisparityMap(self,imgL,imgR):
        disparity = cv2.StereoBM_create(0, 25)
        cv2.compute(imgL, imgR)
        zmap = {}

        for Yo in range(self.H_cam // 6, self.H_cam, self.H_cam // 3):
            for Xo in range(self.W_cam // 20, self.W_cam, self.W_cam // 10):
                D, n = 0, 0
                for x in range(Xo - self.W_cam // 20, Xo + self.W_cam // 20):
                    for y in range(Yo - self.H_cam // 6, Yo + self.H_cam // 6):
                        d = disparity[y,x]
                        if d > 0:
                            D += d
                            n += 1
                try:
                    z = self.z_range(D / n, y = Yo)
                    if z <   1: z = 0
                    if z > 100: z = 0
                except ZeroDivisionError:
                    z = 0

                zmap.update({(Xo,Yo):z})

        return zmap

    def get_img_list(self, object_list):
        _ = dict()
        sift = cv2.xfeatures2d.SIFT_create()
        # m = magic.open(magic.MAGIC_MIME)
        # m.load()

        for k in object_list.keys():
            _dir = object_list[k]['dir']
            for _name in os.listdir(_dir):
                __ = os.path.join(_dir,_name)
                if __.endswith('.jpg'):
                    print("Loading %s ... " % (__), end = '', flush = True, file=sys.stderr)
                    _img = cv2.imread(__,0) 
                    _h, _w = _img.shape
                    _kp, _des = sift.detectAndCompute(_img,None)
                    _.update(
                        {
                            __:dict(
                                name = k,
                                img = _img,
                                h = _h,
                                w = _w,
                                kp = _kp,
                                des = _des,
                                item = _name,
                            )
                        }
                    )
                    print("done", file=sys.stderr)
        return _

    def get_object_list(self, bd_dir):
        _ = dict()
        for a, dirs, files in os.walk(bd_dir):
            for _file in files:
                if _file == "descript.ion":
                    __ = os.path.join(a,_file)
                    obj = json.load(open(__))
                    obj.update({'dir':os.path.dirname(__)})
                    _.update({obj['name'] : obj}
                    )
        return _
                                              #'return_data'
    def recognize(self, camera='left', mode = 'save_image'):
        _, A0, B0 = self.r.ask() 

        FLANN_INDEX_KDTREE = 0
        MIN_MATCH_COUNT = 7
        sift = cv2.xfeatures2d.SIFT_create()
        index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
        search_params = dict(checks = 50)
        flann = cv2.FlannBasedMatcher(index_params, search_params)

        if mode == 'return_data':
            img2, img3 = self.stereo_shot(camera)
        else:
            img2, img3 = self.stereo_shot()
            D = self.getDisparityMap(img2,img3)

        kp2, des2 = sift.detectAndCompute(img2,None)
        # kp3, des3 = sift.detectAndCompute(img3,None)
        _ = dict()
        for k in self.object_list.keys():
            _.update({k: dict(matches = 0, items=[], item_coords=[], coords=[])})

        for k in self.img_list.keys():
            print("Trying %s ... " % (k), end = '', flush = True, file=sys.stderr)
            name1 = self.img_list[k]['name']
            img1 = self.img_list[k]['img']
            h = self.img_list[k]['h']
            w = self.img_list[k]['w']
            kp1 = self.img_list[k]['kp']
            des1 = self.img_list[k]['des']
            item = self.img_list[k]['item']
            try:
                w_o = self.object_list[name1]['w']
                h_o = self.object_list[name1]['h']
            except KeyError:
                w_o = 0
                h_o = 0

            good = []
            try:
                for m,n in flann.knnMatch(des1,des2,k=2):
                    if m.distance < 0.7*n.distance:
                        good.append(m)
            except cv2.error as e:
                print("CV excepion ", e, file=sys.stderr)

            print("done, %s matches" % (len(good)), file=sys.stderr)

            if len(good) > MIN_MATCH_COUNT:
                src_pts = np.array([ kp1[m.queryIdx].pt for m in good ], dtype=np.float32).reshape(-1,1,2)
                dst_pts = np.array([ kp2[m.trainIdx].pt for m in good ], dtype=np.float32).reshape(-1,1,2)

                M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)

                pts = np.array([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ], dtype=np.float32).reshape(-1,1,2)
                try:
                    dst = cv2.perspectiveTransform(pts,M)

                    H = max(dst[1][0][1],dst[2][0][1]) - min(dst[0][0][1],dst[3][0][1])
                    W = max(dst[2][0][0],dst[3][0][0]) - min(dst[1][0][0],dst[0][0][0])
                    X1 = [dst[0][0][0], dst[2][0][0]]
                    X2 = [dst[1][0][0], dst[3][0][0]]
                    Y1 = [dst[0][0][1], dst[2][0][1]]
                    Y2 = [dst[1][0][1], dst[3][0][1]]

                    k1, b1 = sp.polyfit(X1,Y1,1)
                    k2, b2 = sp.polyfit(X2,Y2,1)

                    x = (b2 - b1) / (k1 - k2)
                    y = k1 * x + b1
                    a,b = self.xy_to_ab_radians([x,y],[radians(A0),radians(B0)])

                    try:
                        z_w = w_o / tan(W * self.A_cam / self.W_cam)
                        z_h = h_o / tan(H * self.B_cam / self.H_cam)
                        z = Student([z_h, z_w, z_h, z_w, z_h, z_w])

                    except ZeroDivisionError:
                        z = 'n/a'

                    # print(h/w,H/W, file=sys.stderr)
                    # print(X1,x,X2, file=sys.stderr)
                    # print(Y1,y,Y2, file=sys.stderr)


                    cv2.imwrite('./log/%s' % (k.replace('/','_').lstrip('._')),cv2.polylines(cpobj(img2),[np.int32(dst)],True,255,3, cv2.LINE_AA))
                    if abs(h/w - H/W) < 1:
                        _.update(
                            {
                                name1: dict(
                                    text = self.object_list[name1]['text'],
                                    url = self.object_list[name1]['url'],
                                    matches = _[name1]['matches'] + len(good),
                                    items = _[name1]['items'] + [item],
                                    item_coords = _[name1]['item_coords'] + [dict(x=int(x),y=int(y))],
                                    rect = [H,W],
                                    dst = dst, 
                                    coords = dict(
                                        x = x, 
                                        y = y, 
                                        a = a, 
                                        b = b, 
                                        z = z),
                                )
                            }
                        )
                except cv2.error as e:
                    print(e, file=sys.stderr)
            del good

        # print(json.dumps(_,indent=2,ensure_ascii=0), file=sys.stderr)
        _.update(dict(img = img2))
        
        if mode == 'save_image':
            _.update(dict(D = D))
            return self.draw_best_matches(_)
        else:
            return _

    def rotate(self, data, returnimage = True):
        _ = self.r.move(
            data['a'],
            data['b'],
        )
        print(returnimage)
        if returnimage:
            return self.saveimage(img = self.snapshot())
        else:
            return dict(portdata = _)

    def stereo_shot(self, camera = 'both'):
        img_l = None
        img_r = None

        def L():
            nonlocal img_l
            img_l = self.snapshot(camera = 'left')
        def R():
            nonlocal img_r
            img_r = self.snapshot(camera = 'right')

        if camera == 'both':
            Thread(target = L).start()
            Thread(target = R).start()
            while any((img_l,img_r)) == None:
                sleep(0.01)

            return img_l, img_r
        else:
            _ = self.snapshot(camera)
            return _, _

    def snapshot(self, camera = 'left'):
        cap = cv2.VideoCapture(self.get_camera(camera))
        ret, frame = cap.read()
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rows,cols = img.shape
        transform = self.description['cameras'][camera]['transform']
        img = cv2.warpAffine(img,cv2.getAffineTransform(
            np.float32(transform[0]),
            np.float32(transform[1])
        ),(cols,rows))
        return img

    def saveimage(self, img = None, _name = ''):
        if _name == '':
            _name = datetime.strftime(datetime.now(), "/static/%Y_%m_%d-%H_%M_%S.jpg")
        try:
            cv2.imwrite('./%s' % (_name),img)
        except Exception as e:
            print(e, file=sys.stderr)
            pass

        return _name

    def get_state(self):
        _, A0, B0 = self.r.ask() 
        self.state.update({'pos':dict(
            a = A0, # курс
            b = B0, # возвышение
        )})
        return self.state

    def get_camera(self, camera = 'left'):
        return int(self.description['cameras'][camera]['id'])

    def draw_best_matches(self, cv_results = dict()):
        img = cv_results.pop('img')
        D = cv_results.pop('D')
        font = cv2.FONT_HERSHEY_SIMPLEX
        for k in cv_results.keys():
            r = cv_results[k]
            if r['matches'] > 0:
                x,y,z,a,b = r['coords']['x'], \
                            r['coords']['y'], \
                            r['coords']['z'], \
                            r['coords']['a'], \
                            r['coords']['b']
                h, w = r['rect']
                text_x = int(x - w / 2)
                text_y = int(y + h / 2) + 20
                dst = r['dst']
                cv2.putText(img, "o=%s" % (k), (text_x,text_y + 00), font, 0.4, (0,255,0), 1, cv2.LINE_AA)
                cv2.putText(img, "z=%s" % (z), (text_x,text_y + 15), font, 0.4, (0,255,0), 1, cv2.LINE_AA)
                cv2.putText(img, "a=%s" % (round(degrees(a),2)), (text_x,text_y + 30), font, 0.4, (0,255,0), 1, cv2.LINE_AA)
                cv2.putText(img, "b=%s" % (round(degrees(b),2)), (text_x,text_y + 45), font, 0.4, (0,255,0), 1, cv2.LINE_AA)
                cv2.polylines(img, [np.int32(dst)], True, 255, 3, cv2.LINE_AA)

        for x,y in D.keys():
            if D[(x,y)] > 0: z = str(round(D[(x,y)],2))
            else: z = ""
            cv2.putText(img, z, (x, y), font, 0.4, (255,0,0), 1, cv2.LINE_AA)
        return self.saveimage(img)

    def scan(self, A_min = -140, A_max = 140):
        
        scan_results = {}
        img_pair = dict(L = None, R = None)

        def cv_results_update(new_res, LR = 'L'):
            nonlocal scan_results
            nonlocal img_pair

            img_pair[LR] = new_res.pop('img')
            
            for k in new_res.keys():
                r = new_res[k]
                if r['matches'] > 0:
                    try:
                        scan_results[k]["a"] += r['coords']['a']
                        scan_results[k]["b"] += r['coords']['b']
                        scan_results[k]["w"] += self.pix_to_angle(r['rect'][0])
                        scan_results[k]["z"] += r['coords']['z'].X
                        scan_results[k]["D"] += r['coords']['z'].Dx

                        for _ in "abwzD": scan_results[k][_] /= 2

                    except KeyError:
                        scan_results.update(
                            {
                                k : {
                                    "name" : k,
                                    "a": r['coords']['a'], 
                                    "b": r['coords']['b'], 
                                    "w": self.pix_to_angle(r['rect'][0]),
                                    "z": r['coords']['z'].X, 
                                    "D": r['coords']['z'].Dx
                                }
                            }
                        )

        def map_update(img_pair = [None, None], A = 0):
            nonlocal scan_results
            try:
                zmap = scan_results['map']
            except KeyError:
                zmap = {}

            disparity = cv2.StereoBM_create(0, 25).compute(img_pair['L'], img_pair['R'])

            for Yo in range(self.H_cam // 6, self.H_cam, self.H_cam // 3):
                try:
                    _, idY = self.xy_to_ab_radians([0, Yo], [0,0])
                    zmapX = zmap[int(idY * 100)]
                except KeyError:
                    zmapX = {}
                
                for Xo in range(self.W_cam // 20, self.W_cam, self.W_cam // 10):
                    D, n = 0, 0
                    for x in range(Xo - self.W_cam // 20, Xo + self.W_cam // 20):
                        for y in range(Yo - self.H_cam // 6, Yo + self.H_cam // 6):
                            d = disparity[y,x]
                            if d > 0:
                                D += d
                                n += 1
                    try:
                        z = self.z_range(D / n, y = Yo)
                    except ZeroDivisionError:
                        z = 0


                    idX, idY = self.xy_to_ab_radians([Xo, Yo], [A,0])

                    zmapX.update({int(idX * 100):z})

                zmap.update({int(idY * 100): zmapX})
            del _, disparity

            scan_results.update({'map': zmap})




        for a in range(A_min,A_max,int(degrees(self.A_cam))):
            self.rotate({"a": a, "b": 0})
            sleep(.2)
            cv_results_update(self.recognize('left', mode = 'return_data'), LR = 'L')
            cv_results_update(self.recognize('right', mode = 'return_data'), LR = 'R')
            map_update(img_pair, radians(a))

        self.rotate({"a": 0, "b": 0})

        return scan_results

    def disp(self):
        pass
        imgL = cv2.imread('Yeuna9x.png',0)
        imgR = cv2.imread('SuXT483.png',0)

        stereo = cv2.StereoBM(1, 16, 15)
        disparity = stereo.compute(imgL, imgR)




if __name__ == "__main__":
    s = Stereo()
    print(datetime.now())
    s.stereo_shot()
    print(datetime.now())
    s.saveimage(s.snapshot('left'), 'left.jpg')
    print(datetime.now())
    s.saveimage(s.snapshot('right'), 'right.jpg')
    print(datetime.now())
