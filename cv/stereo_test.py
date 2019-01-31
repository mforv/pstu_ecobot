
import cv2
from matplotlib import pyplot as plt

cap = cv2.VideoCapture(2)
ret, frame = cap.read()
imgL = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

cap = cv2.VideoCapture(4)
ret, frame = cap.read()
imgR = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
stereo = cv2.StereoBM_create(numDisparities=16, blockSize=15)
disparity = stereo.compute(imgL,imgR)
plt.imshow(disparity,'gray')
plt.show()