import cv2
import numpy as np
cap = cv2.VideoCapture(0)

while True:
    ret,frame = cap.read()
    x,y =frame.shape[0:2]
    small_frame = cv2.resize(frame,(int(y/2),int(x/2)))
    cv2.imshow('small',small_frame)
    gray = cv2.cvtColor(small_frame,cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray,50,120)
    minLineLength =10
    maxLineGap = 5
    lines = cv2.HoughLinesP(edges,1,np.pi/180,100,minLineLength,maxLineGap)
#    if lines == None or len(lines) == 0:
#        continue
    for x1,y1,x2,y2 in lines[0]:
        cv2.line(small_frame,(x1,y1),(x2,y2),(0,255,0),2)
    cv2.imshow('line',small_frame)
    if cv2.waitKey(1) & 0xff == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()

    