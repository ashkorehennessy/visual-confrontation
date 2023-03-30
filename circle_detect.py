import cv2
import numpy as np
cap = cv2.VideoCapture(0)

while True:
    ret,frame = cap.read()
    x,y = frame.shape[0:2]
    small_frame = cv2.resize(frame,(int(y/2),int(x/2)))
    cv2.imshow('small',small_frame)
    gray = cv2.cvtColor(small_frame,cv2.COLOR_BGR2GRAY)
    gray_img = cv2.medianBlur(gray,5)
    cimg = cv2.cvtColor(gray_img,cv2.COLOR_GRAY2BGR)
    
    circles = cv2.HoughCircles(gray_img,cv2.HOUGH_GRADIENT,1,120,param1=100,param2=30,minRadius=0,maxRadius=0)
    circles =np.uint16(np.around(circles))
    for i in circles[0,:]:
        cv2.circle(small_frame,(i[0],i[1]),i[2],(0,255,0),2)
        cv2.circle(small_frame,(i[0],i[1]),2,(0,0,255),3)
        
    cv2.imshow('circles',small_frame)
    if cv2.waitKey(1) & 0xff == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()