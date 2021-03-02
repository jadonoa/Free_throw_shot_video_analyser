import cv2
import os
import numpy as np
import imutils
import time
from collections import deque
from django.conf import settings

frames_path = settings.MEDIA_ROOT + '/frames/'

def createFrames(path):
    # Define the upper and lower bounds of the colour of the ball (orange/red) in the HSV colour space
    colourLower = (0, 170, 35)
    colourUpper = (10, 255, 255)
    bufferLen = 24
    # maximum size of deque is 24. Queue length = Cotrail tail length.
    pts = deque(maxlen=bufferLen)

    # return
    capture = cv2.VideoCapture(path)

    # Allow the camera or video file to warm up
    time.sleep(2.0)

    cnt = 0

    # Main loop
    while True:
        # Get the current frame
        frame = capture.read()

        # Handle the frame from VideoCapture or VideoStream
        frame = frame[1]

        # If we are viewing a video and we did not grab a frame, then we have reached the end of the video
        if frame is None:
            break

        # Resize the frame, blur it, and convert it to the HSV color space. Resizes the frame allows us to process it faster
        frame = imutils.resize(frame, width=1900) #1850
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        # Construct a mask for the color of the basketball, then perform a series of dilations and erosions to remove any small blobs left in the mask
        # The ball is separated by lines of different colour so we get separated blobs. High dilation joins the blobs together
        mask = cv2.inRange(hsv, colourLower, colourUpper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=20)

        # Find contours in the mask and initialize the current (x, y) center of the ball
        contrs = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contrs = imutils.grab_contours(contrs)
        center = None

        # Only proceed if at least one contour was found
        if len(contrs) > 0:
            # Find the largest contour in the mask, then use it to compute the minimum enclosing circle and centroid
            c = max(contrs, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        # Update the points in the queue
        pts.appendleft(center)

        # Loop over the set of tracked points
        for i in range(1, len(pts)):
            # If either of the tracked points are None, ignore them
            if pts[i - 1] is None or pts[i] is None:
                continue

            # Otherwise, compute the thickness of the line and draw the connecting lines
            thickness = int(np.sqrt(bufferLen / float(i + 1)) * 2.5)
            cv2.line(frame, pts[i - 1], pts[i], (0, 255, 0), thickness)

        cv2.imwrite(frames_path + str(cnt) + '.png', frame)
        cnt += 1

        key = cv2.waitKey(1) & 0xFF

        # if the 'q' key is pressed, stop the loop
        if key == ord("q"):
            break

    # otherwise, release the camera
    capture.release()


def frames_to_video():
    input_frame_path = frames_path

    img_list = os.listdir(input_frame_path)
    num_frames = len(img_list)
    test_frame = cv2.imread(os.path.join(input_frame_path, '0.png'))
    height, width, channels = test_frame.shape

    fps = 30
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    size = (width, height)

    output_file_name = settings.MEDIA_ROOT + '/trackingVideo.mov'

    out = cv2.VideoWriter(output_file_name, fourcc, fps, size)

    for i in range(num_frames):
        img_name = str(i) + '.png'
        img_path = os.path.join(input_frame_path, img_name)
        img = None

        try:
            img = cv2.imread(img_path)
            out.write(img)

        except:
            print(img_name + 'does not exist')

        if img is not None:
            cv2.waitKey(1)

    out.release()


def createBlankFrames(path):
    capture = cv2.VideoCapture(path)

    # Allow the camera or video file to warm up
    time.sleep(2.0)

    cnt = 0

    # Main loop
    while True:
        # Get the current frame
        frame = capture.read()

        # Handle the frame from VideoCapture or VideoStream
        frame = frame[1]

        # If we are viewing a video and we did not grab a frame, then we have reached the end of the video
        if frame is None:
            break

        cv2.imwrite(frames_path + str(cnt) + '.png', frame)
        cnt += 1

        key = cv2.waitKey(1) & 0xFF

        # if the 'q' key is pressed, stop the loop
        if key == ord("q"):
            break

    # otherwise, release the camera
    capture.release()