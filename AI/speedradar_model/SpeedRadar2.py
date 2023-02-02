import cv2
from tracker2 import *
import numpy as np
end = 0


#Creater Tracker Object
tracker = EuclideanDistTracker()

cap = cv2.VideoCapture(0)
# cap = cv2.VideoCapture("../../../traffic4.mp4")

f = 25
w = int(1000/(f-1))


#Object Detection
object_detector = cv2.createBackgroundSubtractorMOG2(history=None,varThreshold=None)
#100,5

#KERNALS  (ROI)
kernalOp = np.ones((3,3),np.uint8)
kernalOp2 = np.ones((5,5),np.uint8)
kernalCl = np.ones((11,11),np.uint8)
fgbg=cv2.createBackgroundSubtractorMOG2(detectShadows=True)
kernal_e = np.ones((5,5),np.uint8)

while True:
    ret,frame = cap.read()
    if not ret:
        break
    
    # camera laptop
    # frame = cv2.resize(frame, None, fx=2, fy=2)

    # video
    frame = cv2.resize(frame, None, fx=0.5, fy=0.5)

    height,width,_ = frame.shape
    #print(height,width)
    #540,960


    #Extract ROI
    #roi = frame[50:540,200:960]
    roi = frame[0:720,0:1280]

    #MASKING METHOD 1
    mask = object_detector.apply(roi)
    _, mask = cv2.threshold(mask, 250, 255, cv2.THRESH_BINARY)

    #DIFFERENT MASKING METHOD 2 -> This is used
    fgmask = fgbg.apply(roi)
    ret, imBin = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)
    mask1 = cv2.morphologyEx(imBin, cv2.MORPH_OPEN, kernalOp)
    mask2 = cv2.morphologyEx(mask1, cv2.MORPH_CLOSE, kernalCl)
    e_img = cv2.erode(mask2, kernal_e)

    #Contour Detection
    contours,_ = cv2.findContours(e_img,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    detections = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        #THRESHOLD
        if area > 200:
            x,y,w,h = cv2.boundingRect(cnt)
            cv2.rectangle(roi,(x-10,y-10),(x+w+10,y+h+10),(0,255,0),3)
            detections.append([x,y,w,h])

    #Object Tracking
    boxes_ids = tracker.update(detections)
    for box_id in boxes_ids:
        x,y,w,h,id = box_id

        cv2.putText(roi,str(id)+" "+str(tracker.getsp(id)),(x,y-15), cv2.FONT_HERSHEY_PLAIN,1,(255,255,0),2)
        cv2.rectangle(roi,(x-10,y-10),(x+w+10,y+h+10),(0,255,0),2)

        s = tracker.getsp(id)
        if (tracker.f[id] == 1 and s != 0):
            tracker.capture(roi, x, y, h, w, s, id)

    # DRAW LINES
    #image, start_point, end_point, color, thickness

    # DRAW LINES
    cv2.line(frame, (0, (int(line1) - 20)), (640, (int(line1) - 20)), (0, 0, 255), 2)
    cv2.line(frame, (0, int(line1)), (640, int(line1)), (0, 0, 255), 2)

    cv2.line(frame, (0, (int(line1) - int(distance1))), (640, (int(line1) - int(distance1))), (0, 0, 255), 2)
    cv2.line(frame, (0, ((int(line1) - 20) - int(distance1))), (640, ((int(line1) - 20) - int(distance1))), (0, 0, 255), 2)


    #DISPLAY
    #cv2.imshow("Mask",mask2)
    #cv2.imshow("Erode", e_img)
    cv2.imshow("ROI", roi)
    cv2.imshow("MASK", mask)

    key = cv2.waitKey(w-10)
    if key==27:
        tracker.end()
        end=1
        break

if(end!=1):
    tracker.end()

cap.release()
cv2.destroyAllWindows()
