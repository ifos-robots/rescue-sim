from controller import Robot, Motor, DistanceSensor, Camera, Emitter
import struct
import numpy as np
import cv2 as cv

timeStep = 32  # Set the time step for the simulation
max_velocity = 6.28  # Set a maximum velocity time constant

robot = Robot()

wheel_left = Wheel(
    robot.getDevice("left wheel motor"), max_velocity
)  # Create left wheel object
wheel_right = Wheel(
    robot.getDevice("right wheel motor"), max_velocity
)  # Create right wheel object

# Create objects for all robot sensors
leftDist = robot.getDevice("dist left")
frontDist = robot.getDevice("dist front")
rightDist = robot.getDevice("dist right")
eastDist = robot.getDevice("dist right 2")
westDist = robot.getDevice("dist left 2")
distance = DistanceSensors(
    [westDist, leftDist, frontDist, rightDist, eastDist], timeStep
)

gyroscope = Gyroscope(robot.getDevice("gyro"), 1, timeStep)

cam = robot.getDevice("camera front")
cam.enable(timeStep)

colorSensor = robot.getDevice("color")
color = Color(colorSensor, timeStep)

gps = GPS(robot.getDevice("gps"), timeStep)

emitter = robot.getDevice("emitter")  # Emitter doesn't need enable

movement = Movement(wheel_left, wheel_right, gyroscope)


def delay(ms):
    initTime = robot.getTime()  # Store starting time (in seconds)
    while robot.step(timeStep) != -1:
        if (
            robot.getTime() - initTime
        ) * 1000.0 > ms:  # If time elapsed (converted into ms) is greater than value passed in
            break


def getColor():
    img = colorSensor.getImage()  # Grab color sensor camera's image view
    return colorSensor.imageGetGray(
        img, colorSensor.getWidth(), 0, 0
    )  # Return grayness of the only pixel (0-255)


def checkVic(img):
    img = np.frombuffer(img, np.uint8).reshape(
        (cam.getHeight(), cam.getWidth(), 4)
    )  # Convert img to RGBA format (for OpenCV)
    img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)  # Grayscale image
    img, thresh = cv.threshold(
        img, 80, 255, cv.THRESH_BINARY_INV
    )  # Inverse threshold image (0-80 -> white; 80-255 -> black)
    contours, hierarchy = cv.findContours(
        thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE
    )  # Find all shapes within thresholded image
    for cnt in contours:
        x, y, w, h = cv.boundingRect(cnt)  # Find width and height of contour
        contArea = cv.contourArea(cnt)  # Area covered by the shape
        ratio = w / h  # Calculate width to height ratio of contour
        # if the contour area and width to height ratio are within certain ranges
        if contArea > 300 and contArea < 1000 and ratio > 0.65 and ratio < 0.95:
            return True
    return False


def report(victimType):
    pass
    # Struct package to be sent to supervisor to report victim/hazard
    # First four bytes store robot's x coordinate
    # Second four bytes store robot's z coordinate
    # Last byte stores type of victim
    #     Victims: H, S, U, T
    #     Hazards: F, P, C, O
    # wheel_left.setVelocity(0)  # Stop for 1 second
    # wheel_right.setVelocity(0)
    # delay(1300)
    # victimType = bytes(
    #     victimType, "utf-8"
    # )  # Convert victimType to character for struct.pack
    # posX = int(gps.getValues()[0] * 100)  # Convert from cm to m
    # posZ = int(gps.getValues()[2] * 100)
    # message = struct.pack("i i c", posX, posZ, victimType)
    # emitter.send(message)
    # robot.step(timeStep)


while robot.step(timeStep) != -1:
    gyroscope.update(robot.getTime())
    distance.update()
    color.update()
    gps.update()

    movement_decision(distance.distances, movement, color, gps)

    # speeds[0] = max_velocity
    # speeds[1] = max_velocity

    print(
        " West: "
        + str(distance.distances[0])
        + " | Left: "
        + str(distance.distances[1])
        + " | Front: "
        + str(distance.distances[2])
        + " | Right: "
        + str(distance.distances[3])
        + " | East: "
        + str(distance.distances[4])
    )

    # Check left and right sensor to avoid walls
    # for sensor on the left, either
    # if leftDist.getValue() < 0.05:
    #     turn_right()  # We see a wall on the left, so turn right away from the wall

    # if rightDist.getValue() < 0.05:  # for sensor on the right too
    #     turn_left()

    # # for front sensor
    # if frontDist.getValue() < 0.05:
    #     spin()

    # if on black, turn away
    if getColor() < 80:
        # spin()
        # wheel_left.setVelocity(speeds[0])
        # wheel_right.setVelocity(speeds[1])
        delay(600)

    # if sees victim, report it
    if checkVic(cam.getImage()):
        report("T")  # Cannot determine type of victim, so always try 'T' for now

    # wheel_left.setVelocity(
    #     speeds[0]
    # )  # Send the speed values we have choosen to the robot
    # wheel_right.setVelocity(speeds[1])
