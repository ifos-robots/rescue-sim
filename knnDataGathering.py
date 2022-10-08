from controller import Robot
import numpy as np
import cv2 as cv

import os

timeStep = 32  # Set the time step for the simulation

robot = Robot()

frontDist = robot.getDevice("dist front")
frontDist.enable(timeStep)

cam_front = robot.getDevice("camera front")
cam_front.enable(timeStep)

samples =  np.empty((0,100))
responses = []


# Detect presence of victim signs from far
def findSign(img):
    img = np.frombuffer(img, np.uint8).reshape(
        (cam_front.getHeight(), cam_front.getWidth(), 4)
    )  # Convert img to RGBA format (for OpenCV)
    gray_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    r, thresh = cv.threshold(
        gray_img, 80, 255, cv.THRESH_BINARY_INV
    )  # Inverse threshold image (0-80 -> white; 80-255 -> black)
    contours, hierarchy = cv.findContours(
        thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE
    )  # Find all shapes within thresholded image
    
    thresh = cv.resize(thresh, (thresh.shape[1] * 5, thresh.shape[0] * 5), interpolation = cv.INTER_NEAREST)
    cv.imshow('Thresh', thresh)

    currentFoundSign = []

    contour_count = 0
    for cnt in contours:
        x, y, w, h = cv.boundingRect(cnt)  # Find width and height of contour
        contArea = cv.contourArea(cnt)  # Area covered by the shape
        ratio = w / h  # Calculate width to height ratio of contour
        # if the contour area and width to height ratio are within certain ranges

        if contArea > 220 and contArea < 1080 and ratio > 0.6 and ratio < 1.2:
            cv.drawContours(img, contours, contour_count, (0,255,0), 1)

            currentFoundSign = gray_img[y:y+h,x:x+w]

        contour_count += 1

    img = cv.resize(img, (img.shape[1] * 7, img.shape[0] * 7), interpolation = cv.INTER_NEAREST)
    cv.imshow('Contours', img)
    cv.setWindowProperty('Contours', cv.WND_PROP_TOPMOST, 1)

    return currentFoundSign


while robot.step(timeStep) != -1:
    
    foundSign = findSign(cam_front.getImage())
    
    key = cv.waitKey(1)

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
