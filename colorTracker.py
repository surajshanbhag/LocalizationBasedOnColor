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
        #marker.addPointAsAvg((int(x)+xoffset,int(y)+yoffset))
        marker.position_image=(int(x)+xoffset,int(y)+yoffset)
        marker.bounding_circle_radius=int(radius)

def drawCircle(marker,frame):
    cv2.circle(frame, (int(marker.position_image[0]), int(marker.position_image[1])), int(marker.bounding_circle_radius),(0, 255, 255), 2)
    cv2.circle(frame, marker.position_image, 5, (0, 0, 255), -1)

def drawLine(frame,src,dest,color=(255,255,255),thickness=5):
    cv2.line(frame,src.position_image,dest.position_image,color,thickness)

def updateMAP(MAP,markers,bot,frame_size):
    marker_x=[]
    marker_y=[]
    MAP[:,:]=(255,255,255)
    for idx in range(0,4):
        marker_x.append((markers[idx].position_image[0]*MAP_HEIGHT)/frame_size[0])
        marker_y.append((markers[idx].position_image[1]*MAP_HEIGHT)/frame_size[1])
        cv2.circle(MAP, (marker_x[idx],marker_y[idx]), 30,(0, 255, 255), 2)
        cv2.circle(MAP, (marker_x[idx],marker_y[idx]), 5, (0, 0, 255), -1)
    cv2.line(MAP,(marker_x[0],marker_y[0]),(marker_x[1],marker_y[1]),(0,0,0),2)
    cv2.line(MAP,(marker_x[1],marker_y[1]),(marker_x[3],marker_y[3]),(0,0,0),2)
    cv2.line(MAP,(marker_x[3],marker_y[3]),(marker_x[2],marker_y[2]),(0,0,0),2)
    cv2.line(MAP,(marker_x[2],marker_y[2]),(marker_x[0],marker_y[0]),(0,0,0),2)



    marker_x=[]
    marker_y=[]
    for idx in range(0,2):
        marker_x.append((bot[idx].position_image[0]*MAP_HEIGHT)/frame_size[0])
        marker_y.append((bot[idx].position_image[1]*MAP_HEIGHT)/frame_size[1])
        MAP[marker_x[idx],marker_y[idx]]=(0,255,255)
        cv2.circle(MAP, (marker_x[idx],marker_y[idx]), 30,(0, 255, 255), 2)
        cv2.circle(MAP, (marker_x[idx],marker_y[idx]), 5, (0, 0, 255), -1)
    cv2.line(MAP,(marker_x[0],marker_y[0]),(marker_x[1],marker_y[1]),(0,255,0),2)

######################################################################################################
frame_size=(1280,720)

boundaryMarker1=ColorMarker((133,100,0),(1964,205,241))
boundaryMarker2=ColorMarker((133,100,0),(1964,205,241))
boundaryMarker3=ColorMarker((133,100,0),(1964,205,241))
boundaryMarker4=ColorMarker((133,100,0),(1964,205,241))


botMarker1=ColorMarker((84,134,116),(153,221,255))
botMarker2=ColorMarker((38,82,76),(96,167,222))


#Mat Map(4000,4000, CV_8UC3, Scalar(255,255,255));
pixel2meter=100
MAP_HEIGHT=1000
MAP_WIDTH=1000
MAP = np.zeros((MAP_HEIGHT,MAP_WIDTH,3), np.uint8)
MAP[:,:]=(255,255,255)




if __name__ == '__main__':
    print len(sys.argv)
    if len(sys.argv) == 1:
        camera=cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
    elif sys.argv[1] == '1':
        camera=cv2.VideoCapture(int(sys.argv[1]))
        while not (camera.isOpened()):
            print "waiting for camera ..."
        camera.set(cv2.CAP_PROP_FRAME_WIDTH,frame_size[0])
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT,frame_size[1])
    else:
        camera=cv2.VideoCapture(sys.argv[1])


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
#        boundaryMarker1.position_image=(320,180)
#        boundaryMarker2.position_image=(960,180)
#        boundaryMarker3.position_image=(320,540)
#        boundaryMarker4.position_image=(960,540)

        drawLine(frame,boundaryMarker1,boundaryMarker2)
        drawLine(frame,boundaryMarker2,boundaryMarker4)
        drawLine(frame,boundaryMarker4,boundaryMarker3)
        drawLine(frame,boundaryMarker3,boundaryMarker1)

        getBoundingCircle(botMarker1,frame,0)
        drawCircle(botMarker1,frame)

        getBoundingCircle(botMarker2,frame,0)
        drawCircle(botMarker2,frame)
 #       botMarker1.position_image=(640,360)
 #       botMarker2.position_image=(700,400)

        drawLine(frame,botMarker1,botMarker2)

        updateMAP(MAP,(boundaryMarker1,boundaryMarker2,boundaryMarker3,boundaryMarker4),(botMarker1,botMarker2),frame_size)
        cv2.imshow("input",frame)
        cv2.imshow("MAP",MAP)

        cv2.waitKey(1)

