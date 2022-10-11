from controller import Robot
import numpy as np
import cv2 as cv

import os

timeStep = 32  # Set the time step for the simulation

robot = Robot()

wheel_left = robot.getDevice(
    "left wheel motor"
)  # Create an object to control the left wheel
wheel_right = robot.getDevice(
    "right wheel motor"
)
wheel_left.setPosition(float("inf"))
wheel_right.setPosition(float("inf"))

frontDist = robot.getDevice("dist front")
frontDist.enable(timeStep)

cam_front = robot.getDevice("camera front")
cam_front.enable(timeStep)

samples =  np.empty((0,100))
responses = []

# Distinguish
def isVictimSign(img, distance):
    img = np.frombuffer(img, np.uint8).reshape(
        (cam_front.getHeight(), cam_front.getWidth(), 4)
    )  # Convert img to RGBA format (for OpenCV)
    gray_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    r, thresh = cv.threshold(
        gray_img, 200, 255, cv.THRESH_BINARY
    ) # Threshold the image to get only white pixels

    # counting the number of pixels
    whitePixels = np.sum(thresh == 255)
    blackPixels = np.sum(thresh == 0)

    print("WHITE: " + str(whitePixels), "BLACK: " + str(blackPixels))

    # Near sign recognition (between 0.05 - 0.095)
    isSign = False
    if distance < 0.095 and distance > 0.05:
        if distance < 0.07:
            if distance < 0.055:
                if whitePixels > 1550:
                    isSign = True
                else:
                    isSign = False
            elif whitePixels > 1200:
                isSign = True
        elif whitePixels > 860:
            isSign = True   

    threshResize = cv.resize(thresh, (thresh.shape[1] * 5, thresh.shape[0] * 5), interpolation = cv.INTER_NEAREST)
    cv.imshow('Thresh', threshResize)

    return isSign, thresh

    # contours, hierarchy = cv.findContours(
    #     thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE
    # )  # Find all shapes within thresholded image

    # currentFoundSign = []

    # contour_count = 0
    # for cnt in contours:
    #     x, y, w, h = cv.boundingRect(cnt)  # Find width and height of contour
    #     contArea = cv.contourArea(cnt)  # Area covered by the shape
    #     ratio = w / h  # Calculate width to height ratio of contour
    #     # if the contour area and width to height ratio are within certain ranges

    #     if contArea > 220 and contArea < 1080 and ratio > 0.6 and ratio < 1.2:
    #         cv.drawContours(img, contours, contour_count, (0,255,0), 1)

    #         currentFoundSign = gray_img[y:y+h,x:x+w]

    #     contour_count += 1

    # img = cv.resize(img, (img.shape[1] * 7, img.shape[0] * 7), interpolation = cv.INTER_NEAREST)
    # cv.imshow('Contours', img)
    # cv.setWindowProperty('Contours', cv.WND_PROP_TOPMOST, 1)

    # return currentFoundSign

# frames character and classifies H, S, U
def classifyVictim(thresholdedImg):
    # prevents contours from segmenting the letters when too close
    border = cv.copyMakeBorder(
        thresholdedImg,
        top=1,
        bottom=1,
        left=1,
        right=1,
        borderType=cv.BORDER_CONSTANT,
        value=255
    )
    
    contours, hierarchy = cv.findContours(
        border, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE
    )

    print(" --- ")

    charBoundingBox = (0, 0, 0, 0)

    contour_count = 0
    for cnt in contours:
        x, y, w, h = cv.boundingRect(cnt)  # Find width and height of contour
        contArea = cv.contourArea(cnt)  # Area covered by the shape
        ratio = w / h  # Calculate width to height ratio of contour

        # detect contour containing character
        # (very poor, may be enhanced with color detection inside contour) 
        if contArea > 280 and contArea < 820 and ratio > 0.65:
            charBoundingBox = (x, y, w, h)
            print(w, h)
            cv.drawContours(border, contours, contour_count, 160, 1)

        contour_count += 1

    contourImg = cv.resize(border, (border.shape[1] * 5, border.shape[0] * 5), interpolation = cv.INTER_NEAREST)
    cv.imshow('Contours', contourImg)
    cv.setWindowProperty('Contours', cv.WND_PROP_TOPMOST, 1)

    # basically border[y:y+h,x:x+w]
    charFramed = border[charBoundingBox[1]:charBoundingBox[1] + charBoundingBox[3], charBoundingBox[0]:charBoundingBox[0] + charBoundingBox[2]]

    # fixed (40/50 size, 0.8 ratio)
    bndBoxImg = cv.resize(charFramed, (40, 50), interpolation = cv.INTER_NEAREST)
    cv.imshow('Letter', bndBoxImg)
    cv.setWindowProperty('Letter', cv.WND_PROP_TOPMOST, 1)



while robot.step(timeStep) != -1:
    
    print(
        "Front: "
        + str(frontDist.getValue())
    )
    
    isVictim, thresholdedImg = isVictimSign(cam_front.getImage(), frontDist.getValue())
    
    if isVictim:
        print("FOUND VICTIM")
        classifyVictim(thresholdedImg)

    key = cv.waitKey(1)
 
    if key == 0:
        wheel_left.setVelocity(6.28)
        wheel_right.setVelocity(6.28)
    else:
        wheel_left.setVelocity(0)
        wheel_right.setVelocity(0)


    if key != -1 and chr(key) in ['h', 's', 'u'] and foundSign != []:

        roismall = cv.resize(foundSign,(10,10))
        sample = roismall.reshape((1,100))

        samples = np.append(samples, sample, 0)
        responses.append(chr(key))

        print(str(chr(key)) + ' was pressed and saved')

    # Stops loop if 'q' is pressed
    if key & 0xFF == ord('q'):
        print(samples)
        print(responses)

        responses = np.array(responses)
        responses = responses.reshape((responses.size,1))

        path = os.getcwd()
        np.savetxt('generalsamples.data', samples)
        np.savetxt('generalresponses.data', responses, fmt="%s")

        print('Files were saved at: ' + os.getcwd())

        break
