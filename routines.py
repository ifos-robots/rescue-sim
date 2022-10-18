import cv2 as cv
import numpy as np

class VictimDetection:
    def __init__(self, cameras, distances):
        self.cameras = cameras
        self.distances = distances

        self.__lastDetections = {}

    # triggers detection, returns summary of findings
    def detectionPipeline(self):
        detections = {}
        for cameraImg, distanceValue, position in self.__getDistAndCamerasIterable():
            isVictim, thresholdedImg = isVictimSign(cameraImg, distanceValue)
            if isVictim:
                isLetter, framedLetter = frameVictimLetter(thresholdedImg, distanceValue)
                if isLetter:
                    letter = classifyVictimLetter(framedLetter)
                    detections[position] = letter
            else:
                detections[position] = 'N'
        
        if detections == self.__lastDetections:
            return 'old', {}
        else:
            self.__lastDetections = detections
            return 'new', detections

    def __getDistAndCamerasIterable(self):
        return zip(
            [self.cameras.left_image, self.cameras.right_image], 
            [self.distances.left_distance, self.distances.right_distance], 
            ['left', 'right']
        )
