import cv2 as cv
import numpy as np

class VictimDetection:
    def __init__(self, cameras, distances):
        self.cameras = cameras
        self.distances = distances

        self.__lastDetections = {
            "left": ['old', "Null"],
            "right": ['old', "Null"]
        }

    # triggers detection, returns summary of findings
    def detectionPipeline(self):
        detections = {
            "left": ['old', "Null"],
            "right": ['old', "Null"]
        }
        
        for cameraImg, distanceValue, position in self.__getDistAndCamerasIterable():
            isVictim, thresholdedImg = isVictimSign(cameraImg, distanceValue)
            if isVictim == 1:
                isLetter, framedLetter = frameVictimLetter(thresholdedImg, distanceValue)
                if isLetter:
                    letter = classifyVictimLetter(framedLetter)
                    detections[position][1] = letter
            elif isVictim == 0:
                detections[position][1] = 'Near'
            elif isVictim == -1:
                detections[position][1] =  'Null'

            hazmat = hazmatDetection(cameraImg, distanceValue) 
            if hazmat in ['F', 'P', 'C', 'O']:
                detections[position][1] =  hazmat
                print(hazmat)

        # prevents multiple detections from the same sign
        for position in self.__lastDetections.keys():
            if detections[position][1] == self.__lastDetections[position][1]:
                detections[position][0] = 'old'
                self.__lastDetections[position][0] = 'old'
            else:
                detections[position][0] = 'new'
                self.__lastDetections[position][0] = 'new'
                self.__lastDetections[position][1] = detections[position][1]
        
        return detections

    def __getDistAndCamerasIterable(self):
        return zip(
            [self.cameras.left_image, self.cameras.right_image], 
            [self.distances.left_distance, self.distances.right_distance], 
            ['left', 'right']
        )
            