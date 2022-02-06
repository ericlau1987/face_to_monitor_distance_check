import cv2
from datetime import datetime
import numpy as np
import os
import matplotlib.pyplot as plt 
import matplotlib.animation as animation
from matplotlib import style
from Upload_mysql import upload_mysql
from Distance_check import distance_check

# distance from camera to object(face) measured
# centimeter
Known_distance = 43
 
 
# width of face in the real world or Object Plane
# centimeter
Known_width = 10
 
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
    # faces = face_detector.detectMultiScale(gray_image, 1.3, 5)
    faces = face_detector.detectMultiScale(gray_image)
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
image_name = "jeffrey_image.png"
popup_image_name = 'sample_image.jpg'
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
# cv2.imshow(image_name, ref_image)
 
# initialize the camera object so that we
# can get frame from it
cap = cv2.VideoCapture(0)
 
if not cap.isOpened():
    raise IOError("Cannot open webcam")

distance_check = distance_check(distance_limit=50, items_considered=20)

# image_open is to detect whether popup_image is open or not
image_open = False
# initalize the process_pid of Preview to close the popup_image
process_pid = None

ml = upload_mysql('distance')
# ml = upload_mysql('test2')

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
        
        Distance_updated = distance_check.correct_large_distance(Distance)

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
        # print(f'now: {now}; distance: {round(Distance,2)} CM; avg distance: {avg_distance}')
        # append items into row
        row.append(image_name)
        row.append(now)
        row.append(Distance)
        row.append(Distance_updated)
        row.append(avg_distance)
        row.append(distance_check.distance_limit)

        # insert items into mysql
        ml.insert_table(row)

        # check whether distance is too close
        #if yes, show the popup_image as warning
        if distance_check.check_distance_exception():
            # print('too close')
            # if the popup_image is still open, 
            # don't need to open it again
            # otherwise, open it
            if not image_open:
                cwd = os.path.join(os.getcwd(), popup_image_name)
                os.system('{} {}'.format('open', cwd))
                image_open = True
            else:
                pass
        
        else: 
            # if popup_image is open and distance is not close,
            # close the image by killing Preview
            if image_open:
                # list all processes
                processes = os.popen('ps -ax').read().split('\n')

                for process in processes:
                    # remove leading spaces
                    process = process.strip()
                    # identify process pid for the process relevant to Preview
                    if process.split('/')[-1] == 'Preview':
                        process_pid = process.split(' ')[0]
                        # print(f'process: {process}; process_id: {process_pid}')

                os.system(f'kill {process_pid}')  
                process_pid = None
                image_open = False

    else: 
        pass
        # print('face not recognised')


    # show the frame on the screen
    cv2.imshow("frame", frame)
 
    # quit the program if you press 'q' on keyboard
    if cv2.waitKey(1) == ord("q"):
        break
 
# closing the camera
cap.release()
 
# closing the the windows that are opened
cv2.destroyAllWindows()