import cv2
import math
import time
import numpy as np
import os
from datetime import datetime
from keras.models import load_model
from PIL import Image, ImageOps #Install pillow instead of PIL
from PIL import Image as im
import numpy as np


#model
# Disable scientific notation for clarity
np.set_printoptions(suppress=True)
# Load the model
model = load_model('../CNN_model/keras_Model.h5', compile=False)
# Load the labels
class_names = open('../CNN_model/labels.txt', 'r').readlines()

# Create the array of the right shape to feed into the keras model
# The 'length' or number of images you can put into the array is
# determined by the first position in the shape tuple, in this case 1.
data1 = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)


kastid = 0
beginperiode = ""
eindperiode = ""
gemeente = ""
straat = ""
limit = 0
vrachtwagenvrijezone = 0
distance = 0

with open('data.txt') as f:
    line = f.readline()
    while True:
        line = f.readline()
        if not line:
            break
        data = line.split(";")
        kastid = data[0]
        beginperiode = data[1]
        eindperiode = data[2]
        gemeente = data[3]
        straat = data[4]
        limit = data[5]
        vrachtwagenvrijezone = data[6]
        distance = data[7]



traffic_record_folder_name = "TrafficRecord"

if not os.path.exists(traffic_record_folder_name):
    os.makedirs(traffic_record_folder_name)


speed_record_file_location = traffic_record_folder_name + "//SpeedRecord.csv"
file = open(speed_record_file_location, "w")
file.write("ID;KASTID;BEGINPERIODE;EINDPERIODE;GEMEENTE;STRAAT;SNELHEIDSLIMIET;VRACHTWAGENVRIJEZONE;SNELHEID;TIJD;OVERSCHREDEN;TYPE\n")
file.close()


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

                    # START TIMER (410 en 430 zijn plaatsen op sherm)
              #      if (y >= 410 and y <= 430):
              #          self.s1[0, id] = time.time()

                    # STOP TIMER and FIND DIFFERENCE (235 en 255 zijn plaatsen op sherm)
              #      if (y >= 235 and y <= 255):
              #          self.s2[0, id] = time.time()
              #          self.s[0, id] = self.s2[0, id] - self.s1[0, id]

                    # START TIMER (410 en 430 zijn plaatsen op sherm)
                    if (y >= 120 and y <= 140):
                        self.s1[0, id] = time.time()

                    # STOP TIMER and FIND DIFFERENCE (235 en 255 zijn plaatsen op sherm)
                    if (y >= 270 and y <= 290):
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

            image = im.fromarray(crop_img)

            #resize the image to a 224x224 with the same strategy as in TM2:
            #resizing the image to be at least 224x224 and then cropping from the center
            size = (224, 224)
            image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)

            #turn the image into a numpy array
            image_array = np.asarray(image)

            # Normalize the image
            normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1

            # Load the image into the array
            data1[0] = normalized_image_array

            prediction = model.predict(data1)
            index = np.argmax(prediction)
            class_name = class_names[index]
            # confidence_score = prediction[0][index]

            # print('Class:', class_name, end='')
            # print('Confidence score:', confidence_score)
            # print(class_name.split(" ")[1])
            
            # write object in csv file
            filet = open(speed_record_file_location, "a")
            now = datetime.now()
            if (sp > int(limit)):
                filet.write(str(id)+ ";" + str(kastid)+ ";" + beginperiode + ";" + eindperiode+ ";" + gemeente+ ";" + straat + ";" + str(limit)+  ";" + str(vrachtwagenvrijezone) + ";" + str(sp) + ";" + str(now.strftime("%d/%m/%Y %H:%M:%S")) + ";" + str(1) + ";" + str(class_name.split(" ")[0]) + "\n")
            else:
                filet.write(str(id)+ ";" + str(kastid)+ ";" + beginperiode + ";" + eindperiode+ ";" + gemeente+ ";" + straat + ";" + str(limit)+ ";"  + str(vrachtwagenvrijezone) + ";" + str(sp) + ";" + str(now.strftime("%d/%m/%Y %H:%M:%S")) + ";" + str(0) + ";" + str(class_name.split(" ")[0]) + "\n")
            filet.close()

    # SPEED_LIMIT
    def limit(self):
        return int(limit)
