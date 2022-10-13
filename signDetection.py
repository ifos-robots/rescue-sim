import cv2 as cv
import numpy as np

# detects victim signs
# returns True and the thresholded sign image
# or False and the thresholded image
def isVictimSign(img, distance):
    gray_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    r, thresh = cv.threshold(
        gray_img, 200, 255, cv.THRESH_BINARY
    )

    whitePixels = np.sum(thresh == 255)
    blackPixels = np.sum(thresh == 0)

    # print("WHITE: " + str(whitePixels), "BLACK: " + str(blackPixels))

    # Sign recognition (between 0.05 - 0.15), made to be very strict
    isSign = False
    if distance < 0.15 and distance > 0.045:
        if distance < 0.095:
            if distance < 0.07:
                if distance < 0.055:
                    if whitePixels > 1550:
                        isSign = True
                    else:
                        isSign = False
                elif whitePixels > 1150:
                    isSign = True
            elif whitePixels > 750:
                isSign = True 
        elif whitePixels > 320:
            isSign = True

    # threshResize = cv.resize(thresh, (thresh.shape[1] * 5, thresh.shape[0] * 5), interpolation = cv.INTER_NEAREST)
    # cv.imshow('Thresh', threshResize)

    return isSign, thresh

# frames letter if it finds one
# returns True and a (48, 60) framed letter
# or False and the input's thresholded image
def frameVictimLetter(thresholdedImg, distance):
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

    letterBoundingBox = (0, 0, 0, 0)

    for contour_count, cnt in enumerate(contours):
        x, y, w, h = cv.boundingRect(cnt) 
        contArea = cv.contourArea(cnt)
        ratio = w / h

        # detect contour containing letter
        # only two different ranges
        if distance > 0.095:
            if contArea > 150 and contArea < 300 and ratio > 0.6:
                letterBoundingBox = (x, y, w, h)
                # cv.drawContours(border, contours, contour_count, 160, 1)
        else:
            if contArea > 280 and contArea < 820 and ratio > 0.6:
                letterBoundingBox = (x, y, w, h)
                # cv.drawContours(border, contours, contour_count, 160, 1)

    # contourImg = cv.resize(border, (border.shape[1] * 5, border.shape[0] * 5), interpolation = cv.INTER_NEAREST)
    # cv.imshow('Contours', contourImg)
    # cv.setWindowProperty('Contours', cv.WND_PROP_TOPMOST, 1)

    if letterBoundingBox != (0, 0 , 0, 0):
        # basically border[y:y+h,x:x+w], delimiting letter's ROI
        letterFramed = border[letterBoundingBox[1]:letterBoundingBox[1] + letterBoundingBox[3], letterBoundingBox[0]:letterBoundingBox[0] + letterBoundingBox[2]]

        # fixed 48/60 size, 0.8 ratio
        bndBoxImg = cv.resize(letterFramed, (48, 60), interpolation = cv.INTER_NEAREST)
        # cv.imshow('Letter', cv.resize(bndBoxImg, (48 * 3, 60 * 3), interpolation = cv.INTER_NEAREST))
        # cv.setWindowProperty('Letter', cv.WND_PROP_TOPMOST, 1)

        return True, bndBoxImg
    return False, thresholdedImg

# classifies letter into H, S, U
# comparing frame's top, center and bottom areas
# returns 'H', 'S', 'U' or '?'
def classifyVictimLetter(framedLetter):
    # OBS.: framedLetter comes into an standardized size (48,60)
    h, w = framedLetter.shape

    # Especifies letters black pixels patterns 
    # (acceptable ranges at each section)
    blackPixelsPatterns = {
        "H": {
            "top": (240, 330),
            "center": (530, 610),
            "bottom": (270, 360)
        },
        "S": {
            "top": (370, 430),
            "center": (340, 440),
            "bottom": (420, 500)
        },
        "U": {
            "top": (220, 330),
            "center": (270, 390),
            "bottom": (400, 500)
        },
    }

    topSection = framedLetter[0:(h//3 - 1), 0:w]
    topBlackPixels = np.sum(topSection == 0)
    
    centerSection = framedLetter[(h//3 - 1) + 1:(2*(h//3) - 1), 0:w]
    centerBlackPixels = np.sum(centerSection == 0)
    
    bottomSection = framedLetter[(2*(h//3) - 1) + 1:h, 0:w]
    bottomBlackPixels = np.sum(bottomSection == 0)

    # # easy debugging, you're welcome
    # print('-------')
    # print('top Pixels: ')
    # print('BLACK: ' + str(topBlackPixels))
    # print('center Pixels: ')
    # print('BLACK: ' + str(centerBlackPixels))
    # print('bottom Pixels: ')
    # print('BLACK: ' + str(bottomBlackPixels))
    # print('-------')

    foundLetter = '?'
    for letter in blackPixelsPatterns.keys():
        trueCount = 0
        for section, sectionBlackPixels in [('top', topBlackPixels), ('center', centerBlackPixels), ('bottom', bottomBlackPixels)]:
            if sectionBlackPixels >= blackPixelsPatterns[letter][section][0] and sectionBlackPixels <= blackPixelsPatterns[letter][section][1]:
                trueCount += 1
    
        if trueCount == 3:
            foundLetter = letter
    
    return foundLetter