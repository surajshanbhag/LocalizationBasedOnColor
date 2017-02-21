#!/usr/bin/python
import cv2
import sys
import numpy as np
import imutils
from collections import  deque
from Marker import *
from Bot import Bot

global bot1,marker1,marker2,marker3,marker4,markers
global MAP
global state,camera,settlingTime,boundariesSetCount
global frame,transformMatrix
colorsRed=((145,054,101),(186,205,255))
colorsGreen=((11,122,143),(97,210,196))
colorsBlue=((86,125,137),(145,255,255))
settlingTime=2 # No of frames
frame_size=(1280,720)
map_size=(1000,1000)   # ensure this is even number
sqaureSize=1



###############################################################drawCircle
def drawCircle(frame,position,radius,color=(0,255,255),thick=2):
    cv2.circle(frame, position, radius,color,thick)
    cv2.circle(frame, position, 5, (0, 0, 255), -1)



###############################################################drawLine
def drawLine(frame,srcPoint,destPoint,color=(255,255,255),thickness=5):
    cv2.line(frame,srcPoint,destPoint,color,thickness)


###############################################################getTransformationMatrix
def getTransformationMatrix():
    global markers,camera,transformMatrix
    ret, frame=camera.read()
    h,w=map_size
    pt1=markers[0].position_average_pixels
    pt2=markers[1].position_average_pixels
    pt3=markers[2].position_average_pixels
    pt4=markers[3].position_average_pixels

    pts_b4Warp=np.float32([[pt1[0],pt1[1]],[pt2[0],pt2[1]],[pt3[0],pt3[1]],[pt4[0],pt4[1]]])
    pts_aftWarp=np.float32([[w/4,h/4],[3*w/4,h/4],[3*w/4,3*h/4],[w/4,3*h/4]])
    markers[0].position_map=[w/4,h/4]
    markers[1].position_map=[3*w/4,h/4]
    markers[2].position_map=[3*w/4,3*h/4]
    markers[3].position_map=[w/4,3*h/4]

    transformMatrix=cv2.getPerspectiveTransform(pts_b4Warp,pts_aftWarp)


###########################################################findBot
def findBot(frame,frame_warped):
    global bot1,camera,settlingTime,markers
    ret,frame=camera.read()
    height,width,channels=frame.shape


    findMarkers(bot1.Marker1,frame,(0,0),1)
    findMarkers(bot1.Marker2,frame,(0,0),1)

    findMarkers(bot1.Marker1,frame_warped,(0,0),1,True)
    findMarkers(bot1.Marker2,frame_warped,(0,0),1,True)






###########################################################findBoundaryMarkers
def findBoundaryMarkers():
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

            findMarkers(marker,marker_frame,(xoffset,yoffset),count)
            drawCircle(frame,marker.position_average_pixels,marker.boundingCircle_radius)

        count+=1
        cv2.imshow('Localization',frame)
        cv2.waitKey(1)

###########################################################findMarkers
def findMarkers(marker,frame,(xoffset,yoffset),count,imageIsMAP=False):
    #convert to HSV space and get the Contour and find the Center
    frame_hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(frame_hsv,marker.hsv_lower,marker.hsv_upper)
    mask = cv2.erode(mask,None,iterations=2)
    mask = cv2.dilate(mask,None,iterations=2)
    contours=cv2.findContours(mask.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2]
    if len(contours) >0:
        c=max(contours,key=cv2.contourArea)
        ((x,y),radius)=cv2.minEnclosingCircle(c)
        M=cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        if imageIsMAP == False:
            marker.updateImagePosition((int(x)+xoffset,int(y)+yoffset),count)
            marker.boundingCircle_radius=int(radius)
        else:
            marker.updateMapPosition((int(x)+xoffset,int(y)+yoffset))
            marker.boundingCircle_radius=int(radius)

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


########################################################### updateMAP
def updateMAP():
    global MAP,markers,bot1
    lineColor=(255,255,255)
    circleColor=(0,0,255)
    circleCenter=(0,255,255)
    leftTop=markers[0].position_map
    rightTop=markers[1].position_map
    rightBottom=markers[2].position_map
    leftBottom=markers[3].position_map
    botMarker1=bot1.Marker1.position_map
    botMarker2=bot1.Marker2.position_map

    drawCircle(MAP,bot1.Marker1.position_map,bot1.Marker1.boundingCircle_radius)
    drawCircle(MAP,bot1.Marker2.position_map,bot1.Marker2.boundingCircle_radius)
    drawLine(MAP,(botMarker1[0],botMarker1[1]),(botMarker2[0],botMarker2[1]))

    cv2.circle(MAP,(leftTop[0],leftTop[1]),5,circleColor,2)
    cv2.circle(MAP,(rightTop[0],rightTop[1]),5,circleColor,2)
    cv2.circle(MAP,(rightBottom[0],rightBottom[1]),5,circleColor,2)
    cv2.circle(MAP,(leftBottom[0],leftBottom[1]),5,circleColor,2)

    drawLine(MAP,(leftTop[0],leftTop[1]),(rightTop[0],rightTop[1]),lineColor,2)
    drawLine(MAP,(rightTop[0],rightTop[1]),(rightBottom[0],rightBottom[1]),lineColor,2)
    drawLine(MAP,(rightBottom[0],rightBottom[1]),(leftBottom[0],leftBottom[1]),lineColor,2)
    drawLine(MAP,(leftBottom[0],leftBottom[1]),(leftTop[0],leftTop[1]),lineColor,2)

############################################################__main__
if __name__== '__main__':
    global boundariesSetCount
    global bot1,marker1,marker2,marker3,marker4,markers,MAP
    global transformMatrix

    bot1=Bot(colorsGreen,colorsBlue)
    marker1=ColorMarker(0,colorsRed)
    marker2=ColorMarker(1,colorsRed)
    marker3=ColorMarker(2,colorsRed)
    marker4=ColorMarker(3,colorsRed)
    markers=[marker1,marker2,marker3,marker4]
    boundariesSetCount=0
    MAP = np.zeros((map_size[0],map_size[1],3), np.uint8)

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
        if state== "getMarkerBoundaries":
            getMarkerBoundaries()
            state = "FindMarkers"
        elif state == "FindMarkers":
            findBoundaryMarkers()
            state = "CalculatePerspective"
        elif state == "CalculatePerspective":
            getTransformationMatrix()
            state = "LocalizePublish"
        elif state == "LocalizePublish":
            MAP[:,:,:]=0
            ret, frame=camera.read()
            frame_warped = cv2.warpPerspective(frame,transformMatrix,(1000,1000))
            findBot(frame,frame_warped)
            drawCircle(frame,bot1.Marker1.position_average_pixels,bot1.Marker1.boundingCircle_radius)
            drawCircle(frame,bot1.Marker2.position_average_pixels,bot1.Marker2.boundingCircle_radius)
            drawCircle(frame_warped,bot1.Marker1.position_map,bot1.Marker1.boundingCircle_radius)
            drawCircle(frame_warped,bot1.Marker2.position_map,bot1.Marker2.boundingCircle_radius)


            updateMAP()
            cv2.imshow('Warped',frame_warped)
            cv2.imshow('Original',frame)
            cv2.imshow('MAP',MAP)
            cv2.waitKey(1)
            #getBotPosition()
            #publishROSMsg()

