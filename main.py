import cv2
from datetime import datetime
import numpy as np
import os
import matplotlib.pyplot as plt 
import matplotlib.animation as animation
from matplotlib import style
from sqlalchemy import create_engine

 
class distance_check():

    def __init__(self, distance_limit, items_considered) -> None:
        self.distance_limit = distance_limit
        self.distance_all = []
        self.items_considered = items_considered

    def distance_store(self, distance: float) -> list:
        self.distance_all.append(distance)

    def avg_distance(self) -> float:
        return np.mean(self.distance_all[-self.items_considered:])

    def check_distance_exception(self) -> bool:

        if self.avg_distance() < self.distance_limit:
            return True
        else: return False

class mysql_upload():

    def __init__(self, table_name) -> None:
        
        self.sqlEngine = create_engine('mysql+pymysql://root:@127.0.0.1/face_to_monitor_distance', pool_recycle=3600),
        self.dbConnection = self.sqlEngine.connect(),


# distance from camera to object(face) measured
# centimeter
Known_distance = 60
 
 
# width of face in the real world or Object Plane
# centimeter
Known_width = 13
 
# Colors
GREEN = (0, 255, 0)
RED = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
 
# defining the fonts
fonts = cv2.FONT_HERSHEY_COMPLEX
 
# face detector object
face_detector = cv2.CascadeClassifier('./haar-cascade-files-master/haarcascade_frontalface_default.xml')

 
# focal length finder function
def Focal_Length_Finder(measured_distance, real_width, width_in_rf_image):
 
    # finding the focal length
    focal_length = (width_in_rf_image * measured_distance) / real_width
    return focal_length
 
# distance estimation function
def Distance_finder(Focal_Length, real_face_width, face_width_in_frame):
 
    distance = (real_face_width * Focal_Length)/face_width_in_frame
 
    # return the distance
    return distance
 
 
def face_data(image):
 
    face_width = 0  # making face width to zero
 
    # converting color image ot gray scale image
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
 
    # detecting face in the image
    faces = face_detector.detectMultiScale(gray_image, 1.3, 5)
 
    # looping through the faces detect in the image
    # getting coordinates x, y , width and height
    for (x, y, h, w) in faces:
 
        # draw the rectangle on the face
        cv2.rectangle(image, (x, y), (x+w, y+h), GREEN, 2)
 
        # getting face width in the pixels
        face_width = w
 
    # return the face width in pixel
    return face_width

# reading reference_image from directory
image_name = "sample_image.jpg"
ref_image = cv2.imread(image_name)

# find the face width(pixels) in the reference_image
ref_image_face_width = face_data(ref_image)
 
# get the focal by calling "Focal_Length_Finder"
# face width in reference(pixels),
# Known_distance(centimeters),
# known_width(centimeters)
Focal_length_found = Focal_Length_Finder(
    Known_distance, Known_width, ref_image_face_width)

# print(f'focal length found is {Focal_length_found}')
 
# show the reference image
cv2.imshow(image_name, ref_image)
 
# initialize the camera object so that we
# can get frame from it
cap = cv2.VideoCapture(0)
 
if not cap. isOpened():
    raise IOError("Cannot open webcam")

distance_check = distance_check(distance_limit=50, items_considered=20)

image_open = True
process_pid = None

f = open("distance.txt", 'w')
columns = 'image_name|date_time|distances|avg_distances|distance_limit'
f.write(f'{columns}\n')

# looping through frame, incoming from
# camera/video
while cap.isOpened():
    row = []
    # reading the frame from camera
    _, frame = cap.read()
 
    # calling face_data function to find
    # the width of face(pixels) in the frame
    face_width_in_frame = face_data(frame)
 
    # check if the face is zero then not
    # find the distance
    if face_width_in_frame != 0:
       
        # finding the distance by calling function
        # Distance distance finder function need
        # these arguments the Focal_Length,
        # Known_width(centimeters),
        # and Known_distance(centimeters)
        
        Distance = Distance_finder(
            Focal_length_found, Known_width, face_width_in_frame)
        
        now = datetime.now()

        distance_check.distance_store(Distance)

        # draw line as background of text
        cv2.line(frame, (30, 30), (230, 30), RED, 32)
        cv2.line(frame, (30, 30), (230, 30), BLACK, 28)
 
        # Drawing Text on the screen
        cv2.putText(
            frame, f"Distance: {round(Distance,2)} CM", (30, 35),
          fonts, 0.6, GREEN, 2)

        avg_distance = distance_check.avg_distance()
        print(f'now: {now}; distance: {round(Distance,2)} CM; avg distance: {avg_distance}')
        row.append(image_name)
        row.append(str(now))
        row.append(str(Distance))
        row.append(str(avg_distance))
        row.append(str(distance_check.distance_limit))
        row = '|'.join(row)

        f.write(f'{row}\n')

        if distance_check.check_distance_exception():
            print('Too close')
            
            if not image_open:
                cwd = os.path.join(os.getcwd(), image_name)
                os.system('{} {}'.format('open', cwd))
                image_open = True
            else:
                pass
        
        else: 
            if image_open:
                processes = os.popen('ps -ax').read().split('\n')

                for process in processes:
                    if process.split('/')[-1] == 'Preview':
                        process_pid = process.split(' ')[0]

                os.system(f'kill {process_pid}')  
                image_open = False
            
            print('too close')


    else: print('face not recognised')


    # show the frame on the screen
    cv2.imshow("frame", frame)
 
    # quit the program if you press 'q' on keyboard
    if cv2.waitKey(1) == ord("q"):
        break
 
# closing the camera
cap.release()
 
# closing the the windows that are opened
cv2.destroyAllWindows()