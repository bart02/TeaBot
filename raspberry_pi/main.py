import cv2 as cv


def findBigContour(mask, limit=1000):
    contours = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)[0]
    if contours:
        contours = sorted(contours, key=cv.contourArea, reverse=True)
        if cv.contourArea(contours[0]) > limit:
            return contours[0]
        else:
            return None
    else:
        return None


cap = cv.VideoCapture(0)
red = False
green = False
while True:
    _, frame = cap.read()
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    hsv = cv.blur(hsv, (5, 5))

    # green
    mask = cv.inRange(hsv, (79, 118, 56), (98, 185, 115))
    cnt = findBigContour(mask)
    if cnt is not None:
        cv.drawContours(frame, cnt, -1, (0, 255, 0), 3)
        green = True
    else:
        green = False

    # red
    mask = cv.inRange(hsv, (0, 162, 142), (32, 255, 255))
    cnt = findBigContour(mask)
    if cnt is not None:
        cv.drawContours(frame, cnt, -1, (0, 0, 255), 3)
        red = True
    else:
        red = False

    cv.imshow("Contours", frame)
    if green and red:
        print("ERR")
    elif green:
        print('Green')
    elif red:
        print('Red')
    else:
        print('No')
    # print(green, red)


    if cv.waitKey(1) == 27:
        break

cv.destroyAllWindows()