#!/usr/bin/python
import cv2
import sys
import numpy as np
import imutils
from collections import  deque
from Marker import *
from Bot import Bot

global bot1,marker1,marker2,marker3,marker4,markers
global state,camera,settlingTime,boundariesSetCount
global frame
colorsRed=((145,054,101),(186,205,255))
colorsGreen=((114,123,135),(148,232,255))
colorsBlue=((0,99,142),(99,173,255))
settlingTime=200 # No of frames


###############################################################drawCircle
def drawCircle(marker,frame):
    cv2.circle(frame, marker.position_average_pixels, marker.boundingCircle_radius,(0, 255, 255), 2)
    cv2.circle(frame, marker.position_average_pixels, 5, (0, 0, 255), -1)


###############################################################drawLine
def drawLine(frame,src,dest,color=(255,255,255),thickness=5):
    cv2.line(frame,src.position_image,dest.position_image,color,thickness)


###########################################################findMarkers
def findMarkers():
    global markers,camera,settlingTime
    count=1
    while count < settlingTime:
        # repeat for N frames to get a good values for each marker
        ret,frame=camera.read()
        height,width,channels=frame.shape

        # Calculate each marker Position
        for index in range(0,4):
            marker=markers[index]
            # get the boundary set for each marker
            boundaryPoint=marker.boundaries
            xoffset=boundaryPoint[0][0]
            yoffset=boundaryPoint[0][1]

            # crop out the part of the frame having the marker
            marker_frame=frame[boundaryPoint[0][1]:boundaryPoint[1][1],boundaryPoint[0][0]:boundaryPoint[1][0]]

            #convert to HSV space and get the Contour and find the Center
            marker_frame_hsv=cv2.cvtColor(marker_frame,cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(marker_frame_hsv,marker.hsv_lower,marker.hsv_upper)
            mask = cv2.erode(mask,None,iterations=2)
            mask = cv2.dilate(mask,None,iterations=2)
            contours=cv2.findContours(mask.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2]
            if len(contours) >0:
                c=max(contours,key=cv2.contourArea)
                ((x,y),radius)=cv2.minEnclosingCircle(c)
                M=cv2.moments(c)
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

                marker.updateImagePosition((int(x)+xoffset,int(y)+yoffset),count)
                marker.boundingCircle_radius=int(radius)
                print count
                print marker.position_average_pixels
                print marker.position_current_pixels
                print #####"
                drawCircle(marker,frame)

        count+=1
        cv2.imshow('Localization',frame)
        cv2.waitKey(1)

###########################################################getMarkerBoundaries
def getMarkerBoundaries():
    global markers,boundariesSetCount
    global camera
    while boundariesSetCount != 4 :
        ret,frame=camera.read()
        for marker in markers:
            if marker.boundaries[1] != (0,0):
                cv2.rectangle(frame,marker.boundaries[0],marker.boundaries[1],(0,255,0),1)
        cv2.namedWindow('Localization')
        cv2.setMouseCallback('Localization', MarkerBoundariesEvent)
        cv2.imshow('Localization',frame)
        cv2.waitKey(1)
        print boundariesSetCount
    print "Boundaries Set"
    print "###############################################################"


###########################################################MarkerBoundariesEvent

def MarkerBoundariesEvent(event,x,y,flags,param):
    global markers,boundariesSetCount
    if event == cv2.EVENT_LBUTTONDOWN:
        markers[boundariesSetCount].boundaries[0]=(x,y)
        print markers[0].boundaries
        print markers[1].boundaries
        print markers[2].boundaries
        print markers[3].boundaries
    elif event == cv2.EVENT_LBUTTONUP:
        markers[boundariesSetCount].boundaries[1]=(x,y)
        boundariesSetCount+=1
        print markers[0].boundaries
        print markers[1].boundaries
        print markers[2].boundaries
        print markers[3].boundaries


############################################################__main__
if __name__== '__main__':
    global boundariesSetCount
    global bot1,marker1,marker2,marker3,marker4,markers

    bot1=Bot(colorsGreen,colorsBlue)
    marker1=ColorMarker(0,colorsRed)
    marker2=ColorMarker(1,colorsRed)
    marker3=ColorMarker(2,colorsRed)
    marker4=ColorMarker(3,colorsRed)
    markers=[marker1,marker2,marker3,marker4]
    boundariesSetCount=0
    frame_size=(1280,720)

    state="getMarkerBoundaries"
    if len(sys.argv) == 1:          #capture from built in Webcam for no arguments
        camera=cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH,frame_size[0])
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT,frame_size[1])
    elif sys.argv[1] == '1':        # capture from usb Webcam
        camera=cv2.VideoCapture(int(sys.argv[1]))
        while not (camera.isOpened()):
            print "waiting for camera ..."
        camera.set(cv2.CAP_PROP_FRAME_WIDTH,frame_size[0])
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT,frame_size[1])
    else:                           #  capture from video file
        camera=cv2.VideoCapture(sys.argv[1])

# get marker Boundaries
    while True:
        if state == "getMarkerBoundaries":
            getMarkerBoundaries()
            state = "FindMarkers"
        elif state == "FindMarkers":
            findMarkers()
            state = "CalculatePerspective"
        elif state == "CalculatePerspective":
            gettransformationMatrix()
            state = "LocalizePublish"
        elif state == "LocalizePublish":
            getBotPosition()
            publishROSMsg()

