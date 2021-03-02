import cv2
import imutils
import time
import os
from collections import deque
from django.conf import settings

max_heights_make_path = settings.MEDIA_ROOT + '/maxHeights/make/'
max_heights_miss_path = settings.MEDIA_ROOT + '/maxHeights/miss/'


def max_height(lower, upper, make_or_miss):
    # Define the upper and lower bounds of the colour of the ball (orange/red) in the HSV colour space
    colourLower = (0, 170, 35)
    colourUpper = (10, 255, 255)
    bufferLen = 24
    # maximum size of deque is 24. Queue length = Cotrail tail length.
    pts = deque(maxlen=bufferLen)

    maxHeight = 1000
    maxHeightFrames = None

    # Allow the camera or video file to warm up
    time.sleep(2.0)

    input_frame_path = settings.MEDIA_ROOT + '/frames/'

    frame_num = 0

    for i in range(lower, upper):
        img_name = str(i) + '.png'
        img_path = os.path.join(input_frame_path, img_name)
        # img = None

        img = cv2.imread(img_path)
        # Resize the frame, blur it, and convert it to the HSV color space. Resizes the frame allows us to process it faster
        frame = imutils.resize(img, width=1900)  # 1850
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

        if center is not None:
            if center[1] < maxHeight:  # measured in pixels
                maxHeightFrames = frame
                maxHeight = center[1]
                frame_num = i

        key = cv2.waitKey(1) & 0xFF

        # if the 'q' key is pressed, stop the loop
        if key == ord("q"):
            break

        if img is not None:
            cv2.waitKey(1)

    if make_or_miss == 1:
        cv2.imwrite(max_heights_miss_path + str(frame_num) + '.png', maxHeightFrames)

    elif make_or_miss == 2:
        cv2.imwrite(max_heights_make_path + str(frame_num) + '.png', maxHeightFrames)

    frame_name = str(frame_num) + '.png'

    return frame_name
