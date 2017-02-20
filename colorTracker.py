import numpy as np
import imutils
import cv2
from collections import deque
from marker import ColorMarker
import sys

def getMarkerBoundaries(event, x,y, flags, param):
    global ix, iy
    global px, py, markers_box, flag, drawing
    if flag == False:
        if event == cv2.EVENT_LBUTTONDOWN:
            drawing = True
            ix, iy = x, y
        elif event == cv2.EVENT_MOUSEMOVE:
            if drawing == True:
            cv2.rectangle(resize_frame,(ix,iy),(x,y),(0,255,0),1)
            pass
        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
    markers_box.append((ix,iy,x,y))

    if len(markers_box)>= 4:
        flag = True


def getLocationOfMarkers():

    while True:
        (grabbed, frame) = camera.read()
        cv2.namedWindow('Localization')
        cv2.setMouseCallback('Localization',getMarkerBoundaries)

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
        marker.updateImagePosition((int(x)+xoffset,int(y)+yoffset))
        marker.bounding_circle_radius=int(radius)
###############################################################

def drawCircle(marker,frame):
    cv2.circle(frame, (int(marker.position_image[0]), int(marker.position_image[1])), int(marker.bounding_circle_radius),(0, 255, 255), 2)
    cv2.circle(frame, marker.position_image, 5, (0, 0, 255), -1)
###############################################################

def drawLine(frame,src,dest,color=(255,255,255),thickness=5):
    cv2.line(frame,src.position_image,dest.position_image,color,thickness)
###############################################################

def updateMAP(MAP,markers,bot,frame_size):
    marker_x=[]
    marker_y=[]
    MAP[:,:]=(255,255,255)
    for idx in range(0,4):
        mx=((markers[idx].position_image[0]*MAP_HEIGHT)/frame_size[0])
        marker_x.append(mx)

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
###############################################################


def transformImage(frame,m1,m2,m3,m4):
    pts1_array=np.zeros((4,2),dtype= "float32")
    pts2_array=np.zeros((4,2),dtype= "float32")

    pts1=(m1.position_image,m2.position_image,m3.position_image,m4.position_image)
    pts2=(m1.position_ideal,m2.position_ideal,m3.position_ideal,m4.position_ideal)

    print type(pts1)
    for idx_o in range(0,4):
        for idx_i in range(0,2):
            pts1_array[idx_o,idx_i]=np.float32(pts1[idx_o][idx_i])
            pts2_array[idx_o,idx_i]=np.float32(pts2[idx_o][idx_i])
    print type(pts1_array)
    #map(float, pts1)
    #map(float, pts2)
    print pts1
    print pts1_array
    print pts2
    print pts2_array
    pts1_af = np.float32([[pts1_array[0][1],pts1_array[0][0]],[pts1_array[1][1],pts1_array[1][0]],[pts1_array[2][1],pts1_array[2][0]],[pts1_array[3][1],pts1_array[3][0]]])
    pts2_af = np.float32([[pts2_array[0][1],pts2_array[0][0]],[pts2_array[1][1],pts2_array[1][0]],[pts2_array[2][1],pts2_array[2][0]],[pts2_array[3][1],pts2_array[3][0]]])


    M = cv2.getPerspectiveTransform(pts1_af,pts2_af)
    rows,cols,ch = frame.shape
    frame = cv2.warpPerspective(frame,M,(cols,rows))
    #cv2.imshow("affine",frame)


def transformMAP(frame,m1,m2,m3,m4):
    pts1_array=np.zeros((4,2),dtype= "float32")
    pts2_array=np.zeros((4,2),dtype= "float32")

    pts1=(m1.position_image,m2.position_image,m3.position_image,m4.position_image)
    pts2=(m1.position_ideal,m2.position_ideal,m3.position_ideal,m4.position_ideal)

    print type(pts1)
    for idx_o in range(0,4):
        for idx_i in range(0,2):
            pts1_array[idx_o,idx_i]=np.float32(pts1[idx_o][idx_i])
            pts2_array[idx_o,idx_i]=np.float32(pts2[idx_o][idx_i])
    print type(pts1_array)
    #map(float, pts1)
    #map(float, pts2)
    pts1_af = np.float32([[pts1[0][0],pts1[0][1]],[pts1[1][0],pts1[1][1]],[pts1[2][0],pts1[2][1]]])
    pts2_af = np.float32([[pts2[0][0],pts2[0][1]],[pts2[1][0],pts2[1][1]],[pts2[2][0],pts2[2][1]]])
    #pts1_af = np.float32([[pts1[0][1],50],[200,50],[50,200]])
    #pts2_af = np.float32([[10,100],[200,50],[100,250]])


    M = cv2.getAffineTransform(pts1_af,pts2_af)
    rows,cols,ch = frame.shape
    frame = cv2.warpAffine(frame,M,(cols,rows))
    #cv2.imshow("affine",frame)

######################################################################################################
MAP_HEIGHT=1000
MAP_WIDTH=1000
MAP = np.zeros((MAP_HEIGHT,MAP_WIDTH,3), np.uint8)
MAP[:,:]=(255,255,255)

frame_size=(1280,720)

bounMark1=ColorMarker((133,100,0),(1964,205,241),(MAP_HEIGHT/4,MAP_WIDTH/4))
bounMark2=ColorMarker((133,100,0),(1964,205,241),(MAP_HEIGHT/4,3*MAP_WIDTH/4))
bounMark3=ColorMarker((133,100,0),(1964,205,241),(3*MAP_HEIGHT/4,3*MAP_WIDTH/4))
bounMark4=ColorMarker((133,100,0),(1964,205,241),(MAP_HEIGHT/4,3*MAP_WIDTH/4))


botMark1=ColorMarker((84,134,116),(153,221,255),(MAP_HEIGHT/2,MAP_WIDTH/2))
botMark2=ColorMarker((38,82,76),(96,167,222),(MAP_HEIGHT/2,MAP_WIDTH/2))


#Mat Map(4000,4000, CV_8UC3, Scalar(255,255,255));
pixel2meter=100

def trackColor():
    #read frame
    while True:
        (grabbed, frame) = camera.read()
#        bounMark1.position_image=(320,180)
#        bounMark2.position_image=(960,180)
#        bounMark3.position_image=(320,540)
#        bounMark4.position_image=(960,540)
#        botMark1.position_image=(640,360)
#       botMark2.position_image=(700,400)

        getBoundingCircle(bounMark1,frame,1)
        drawCircle(bounMark1,frame)

        getBoundingCircle(bounMark2,frame,2)
        drawCircle(bounMark2,frame)

        getBoundingCircle(bounMark3,frame,3)
        drawCircle(bounMark3,frame)

        getBoundingCircle(bounMark4,frame,4)
        drawCircle(bounMark4,frame)
        drawLine(frame,bounMark1,bounMark2)
        drawLine(frame,bounMark2,bounMark4)
        drawLine(frame,bounMark4,bounMark3)
        drawLine(frame,bounMark3,bounMark1)

        getBoundingCircle(botMark1,frame,0)
        drawCircle(botMark1,frame)

        getBoundingCircle(botMark2,frame,0)
        drawCircle(botMark2,frame)

        drawLine(frame,botMark1,botMark2)
        transformImage(frame,bounMark1,bounMark2,bounMark3,bounMark4)

        updateMAP(MAP,(bounMark1,bounMark2,bounMark3,bounMark4),(botMark1,botMark2),frame_size)
        cv2.imshow("input",frame)
        cv2.imshow("MAP",MAP)
        cv2.waitKey(1)


if __name__ == '__main__':
    source=0
    if len(sys.argv) == 1:
        camera=cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
    elif sys.argv[1] == '1':
        camera=cv2.VideoCapture(int(sys.argv[1]))
        source = int(sys.argv[1])
        while not (camera.isOpened()):
            print "waiting for camera ..."
        camera.set(cv2.CAP_PROP_FRAME_WIDTH,frame_size[0])
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT,frame_size[1])
    else:
        camera=cv2.VideoCapture(sys.argv[1])
        source=sys.argv[1]
    key = cv2.waitKey(1) & 0xFF


    while True:
        getLocationOfMarkers()
        trackColor()
        print "done"



