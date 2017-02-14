import numpy as np
import imutils
import cv2
from collections import deque
from marker import ColorMarker
import sys

def getBoundingCircle(marker,frame,quadrant):
    #convert to HSV space
    height, width, channels = frame.shape
    # 0 means whole image
    xoffset=0
    yoffset=0
    if quadrant == 1:
        frame=frame[1:height/2,1:width/2]
    elif quadrant == 2:
        frame=frame[1:height/2,width/2:width]
        xoffset=int(width/2)
    elif quadrant == 3:
        frame=frame[height/2:height,1:width/2]
        yoffset=int(height/2)
    elif quadrant == 4:
        frame=frame[height/2:height,width/2:width]
        yoffset=int(height/2)
        xoffset=int(width/2)

    frame_hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    # create a Mask for marker 1
    mask = cv2.inRange(frame_hsv,marker.color_lower,marker.color_upper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # find contours
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2]

    if len(cnts) >0:
        c=max(cnts,key=cv2.contourArea)
        ((x,y),radius)=cv2.minEnclosingCircle(c)
        M=cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        marker.position_image=(int(x)+xoffset,int(y)+yoffset)
        marker.bounding_circle_radius=int(radius)

def drawCircle(marker,frame):
    cv2.circle(frame, (int(marker.position_image[0]), int(marker.position_image[1])), int(marker.bounding_circle_radius),(0, 255, 255), 2)
    cv2.circle(frame, marker.position_image, 5, (0, 0, 255), -1)

def drawLine(frame,src,dest,color=(255,255,255),thickness=5):
    cv2.line(frame,src.position_image,dest.position_image,color,thickness)


boundaryMarker1=ColorMarker((133,100,0),(1964,205,241))
boundaryMarker2=ColorMarker((133,100,0),(1964,205,241))
boundaryMarker3=ColorMarker((133,100,0),(1964,205,241))
boundaryMarker4=ColorMarker((133,100,0),(1964,205,241))


botMarker1=ColorMarker((84,134,116),(153,221,255))
botMarker2=ColorMarker((38,82,76),(96,167,222))



print len(sys.argv)
if len(sys.argv) == 1:
    camera=cv2.VideoCapture(0)
else:
    camera=cv2.VideoCapture(int(sys.argv[1]))


while True:
    #read frame
    (grabbed, frame) = camera.read()
    #convert to HSV space
    getBoundingCircle(boundaryMarker1,frame,1)
    drawCircle(boundaryMarker1,frame)

    getBoundingCircle(boundaryMarker2,frame,2)
    drawCircle(boundaryMarker2,frame)

    getBoundingCircle(boundaryMarker3,frame,3)
    drawCircle(boundaryMarker3,frame)

    getBoundingCircle(boundaryMarker4,frame,4)
    drawCircle(boundaryMarker4,frame)

    drawLine(frame,boundaryMarker1,boundaryMarker2)
    drawLine(frame,boundaryMarker2,boundaryMarker4)
    drawLine(frame,boundaryMarker4,boundaryMarker3)
    drawLine(frame,boundaryMarker3,boundaryMarker1)

    getBoundingCircle(botMarker1,frame,0)
    drawCircle(botMarker1,frame)

    getBoundingCircle(botMarker2,frame,0)
    drawCircle(botMarker2,frame)

    drawLine(frame,botMarker1,botMarker2)

    #cv2.line(frame,botMarker1.position_image,botMarker2.position_image,(255,255,255),8)
    #cv2.polylines(frame,[pts],True,(0,255,255))

    cv2.imshow("Frame",frame)
    cv2.waitKey(1)

