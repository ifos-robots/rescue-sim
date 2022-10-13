from sys import last_traceback
import cv2 as cv
import numpy as np

class VictimDetection:
    def __init__(self, cameras, distances):
        self.cameras = cameras
        self.distances = distances

        self.lastDetections = {}

    # triggers detection, returns summary of findings
    def detectionPipeline(self):
        detections = {}
        for cameraImg, distanceValue, position in self.__getDistAndCamerasIterable():
            isVictim, thresholdedImg = isVictimSign(cameraImg, distanceValue)
            print(np.sum(thresholdedImg == 255), distanceValue, position)
            if isVictim:
                print('Victim detection')
                print(" Stage 1 - Victim sign probably found")
                isLetter, framedLetter = frameVictimLetter(thresholdedImg, distanceValue)
                if isLetter:
                    print(' Stage 2 - Letter framed')
                    letter = classifyVictimLetter(framedLetter)
                    print(' Stage 3 - Classified letter: ' + letter)
                    detections[position] = letter
                else:
                    detections[position] = 'N'
        
        if detections == self.lastDetections:
            return 'old', {}
        else:
            self.lastDetections = detections
            return 'new', detections

    def __getDistAndCamerasIterable(self):
        return zip(
            [self.cameras.left_image, self.cameras.right_image], 
            [self.distances.left_distance, self.distances.right_distance], 
            ['left', 'right']
        )
