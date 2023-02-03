import cv2
import json
import math
import time
import numpy as np
import os
from os import path
from datetime import datetime
from PIL import Image, ImageOps #Install pillow instead of PIL
from PIL import Image as im
import numpy as np
from edge_impulse_linux.image import ImageImpulseRunner
import sys, getopt


#################################################################################
# Model
#################################################################################
runner = None

model = "/home/pi/.ei-linux-runner/models/181016/v1/model.eim"

dir_path = os.path.dirname(os.path.realpath(__file__))
modelfile = os.path.join(dir_path, model)

#################################################################################
# data.txt
#################################################################################

kastid = 0
distance = 0

with open('data.txt') as f:
    line = f.readline()
    while True:
        line = f.readline()
        if not line:
            break
        data = line.split(";")
        kastid = data[0]
        distance = data[1]
        line1 = data[2]
        distance1 = data[3]


#################################################################################
# JSON
#################################################################################
traffic_record_folder_name = "TrafficRecord"

if not os.path.exists(traffic_record_folder_name):
    os.makedirs(traffic_record_folder_name)


speed_record_file_location = traffic_record_folder_name + "//SpeedRecord.json"
listObj = []

# Check if file exists
if path.isfile(speed_record_file_location) is False:
    # Writing to sample.json
    with open(speed_record_file_location, "w") as outfile:
        outfile.write('[]')


#################################################################################
# main
#################################################################################
class EuclideanDistTracker:
    def __init__(self):
        # Store the center positions of the objects
        self.center_points = {}

        self.id_count = 0
        # self.start = 0
        # self.stop = 0
        self.et = 0
        self.s1 = np.zeros((1, 1000))
        self.s2 = np.zeros((1, 1000))
        self.s = np.zeros((1, 1000))
        self.f = np.zeros(1000)
        self.capf = np.zeros(1000)
        self.count = 0
        self.exceeded = 0

    def update(self, objects_rect):
        objects_bbs_ids = []

        # Get center point of new object
        for rect in objects_rect:
            x, y, w, h = rect
            cx = (x + x + w) // 2
            cy = (y + y + h) // 2

            # CHECK IF OBJECT IS DETECTED ALREADY
            same_object_detected = False

            for id, pt in self.center_points.items():
                dist = math.hypot(cx - pt[0], cy - pt[1])

                if dist < 70:
                    self.center_points[id] = (cx, cy)
                    objects_bbs_ids.append([x, y, w, h, id])
                    same_object_detected = True

                  # START TIMER
                    if (y >= (int(line1) - 40) and y <= int(line1)):
                        self.s1[0, id] = time.time()

                    # STOP TIMER and FIND DIFFERENCE
                    if (y >= ((int(line1) - 40) - int(distance1)) and y <= (int(line1) - int(distance1))):
                        self.s2[0, id] = time.time()
                        self.s[0, id] = self.s2[0, id] - self.s1[0, id]

                    # CAPTURE FLAG
                    if (y < 235):
                        self.f[id] = 1

            # NEW OBJECT DETECTION
            if same_object_detected is False:
                self.center_points[self.id_count] = (cx, cy)
                objects_bbs_ids.append([x, y, w, h, self.id_count])
                self.id_count += 1
                self.s[0, self.id_count] = 0
                self.s1[0, self.id_count] = 0
                self.s2[0, self.id_count] = 0

        # ASSIGN NEW ID to OBJECT
        new_center_points = {}
        for obj_bb_id in objects_bbs_ids:
            _, _, _, _, object_id = obj_bb_id
            center = self.center_points[object_id]
            new_center_points[object_id] = center

        self.center_points = new_center_points.copy()
        return objects_bbs_ids

    # SPEEED FUNCTION
    def getsp(self, id):
        if (self.s[0, id] != 0):
            #calculate speed
            s = (float(distance) * 3.6) / self.s[0, id]
        else:
            s = 0

        return int(s)


    # SAVE VEHICLE DATA
    def capture(self, img, x, y, h, w, sp, id):
        if (self.capf[id] == 0):
            
            self.capf[id] = 1
            self.f[id] = 0
            
            # save image to destination folder
            crop_img = img[y - 10:y + h + 10, x - 10:x + w + 10]

            predicted = ""
            predictedValue = 0

            #################################################################################
            # Image classification
            #################################################################################
            with ImageImpulseRunner(modelfile) as runner:
                try:
                    model_info = runner.init()
                    labels = model_info['model_parameters']['labels']

                    img = crop_img
                    if img is None:
                        print('Failed to load image')
                        exit(1)

                    # imread returns images in BGR format, so we need to convert to RGB
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                    # get_features_from_image also takes a crop direction arguments in case you don't have square images
                    features, cropped = runner.get_features_from_image(img)

                    res = runner.classify(features)

                    if "classification" in res["result"].keys():                       
                        for label in labels:                            
                            score = res['result']['classification'][label]
                            if score > predictedValue:
                                predicted = label
                                predictedValue = score
                            
                        print(predicted)

                    elif "bounding_boxes" in res["result"].keys():
                        print('Found %d bounding boxes (%d ms.)' % (len(res["result"]["bounding_boxes"]), res['timing']['dsp'] + res['timing']['classification']))
                        for bb in res["result"]["bounding_boxes"]:
                            print('\t%s (%.2f): x=%d y=%d w=%d h=%d' % (bb['label'], bb['value'], bb['x'], bb['y'], bb['width'], bb['height']))
                            cropped = cv2.rectangle(cropped, (bb['x'], bb['y']), (bb['x'] + bb['width'], bb['y'] + bb['height']), (255, 0, 0), 1)

                    # the image will be resized and cropped, save a copy of the picture here
                    # so you can see what's being passed into the classifier
                    cv2.imwrite('debug.jpg', cv2.cvtColor(cropped, cv2.COLOR_RGB2BGR))

                finally:
                    if (runner):
                        runner.stop()

            #################################################################################
            # JSON
            #################################################################################
            predicted_index = 3
            if (predicted == "Bycicle"):
                predicted_index = 1
            elif (predicted == "Bus"):
                predicted_index = 2
            elif (predicted == "Car"):
                predicted_index = 3
            elif (predicted == "Motorcycle"):
                predicted_index = 4
            elif (predicted == "Truck"):
                predicted_index = 5
            
            
            now = datetime.now()

            
            with open(speed_record_file_location) as fp:
                listObj = json.load(fp)

            listObj.append({
                "metingID": 0,
                "cameraID": kastid,
                "categorieID": predicted_index,
                "locationID": 1,
                "datumTijd": str(now.strftime("%Y-%m-%dT%H:%M:%S")),
                "snelheid": sp
            })
 
            with open(speed_record_file_location, 'w') as json_file:
                json.dump(listObj, json_file, 
                                    indent=4,  
                                    separators=(',',': '))
