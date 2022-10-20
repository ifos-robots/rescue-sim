
import time
from controller import Robot

timeStep = 32  # Set the time step for the simulation
max_velocity = 6.28  # Set a maximum velocity time constant

robot = Robot()

# Initialize devices
## Wheels
wheel_left = Wheel(robot.getDevice("left wheel motor"), max_velocity)
wheel_right = Wheel(robot.getDevice("right wheel motor"), max_velocity)

## Distance Sensors
westDist = robot.getDevice("dist left 2")
leftDist = robot.getDevice("dist left")
frontDist = robot.getDevice("dist front")
rightDist = robot.getDevice("dist right")
eastDist = robot.getDevice("dist right 2")

distance = DistanceSensors(
    [westDist, leftDist, frontDist, rightDist, eastDist], timeStep
)

## Gyroscope
gyroscope = Gyroscope(robot.getDevice("gyro"), 1, timeStep)

## Cameras (yeah it's wrong, don't change pls)
cameras = Cameras(
    [
        robot.getDevice("camera right"),
        robot.getDevice("camera front"),
        robot.getDevice("camera left"),
    ],
    timeStep,
)

## Color Sensor
colorSensor = robot.getDevice("color")
color = Color(colorSensor, timeStep)

## GPS
gps = GPS(robot.getDevice("gps"), timeStep)

## Radio
emitter = robot.getDevice("emitter")
receiver = robot.getDevice("receiver")
radio = Radio(emitter, receiver, timeStep)

# Initialize movement
movement = Movement(wheel_left, wheel_right, gyroscope)

# routines
victimDetection = VictimDetection(cameras, distance)


def update_sensors(robot_time):
    gyroscope.update(robot_time)
    distance.update()
    color.update()
    gps.update()
    radio.updateReceiver()
    cameras.update()

victim_to_be_reported_type = None
can_report = False
wait_sec = None
init_time = None

while robot.step(timeStep) != -1:
    update_sensors(robot.getTime())
    # radio.sendVictim("S", {"x": 0, "z": 0})
    # radio.lackOfProgressHelp()
    
    if can_report:
        print("reported", victim_to_be_reported_pos, victim_to_be_reported_type)
        can_report = False
        victim_to_be_reported_pos = None
        victim_to_be_reported_type = None

    # victim detection (TODO: report victim)
    detections = victimDetection.detectionPipeline()

    if detections["left"][0] == "new":
        type = detections["left"][1]
        if type in ["H", "S", "U"]:
            victim_to_be_reported_type = type
            victim_to_be_reported_pos = gps.coordinates
            wait_sec = 200
            init_time = time.time()
            print("repost at left")
            
    if detections["right"][0] == "new":
        type = detections["right"][1]
        if type in ["H", "S", "U"]:
            victim_to_be_reported_type = type
            victim_to_be_reported_pos = gps.coordinates
            wait_sec = 200
            init_time = time.time()
            print("repost at right")


    movement_decision(distance.distances, movement, color, gps, radio, detections, wait_sec)


    if init_time and victim_to_be_reported_type and (time.time() - init_time) >= 5:
        radio.sendVictim(victim_to_be_reported_type, victim_to_be_reported_pos)
        can_report = True
        wait_sec = 0
        print(init_time, wait_sec, can_report, time.time(), init_time - time.time())
        
    # print(
    #     " West: "
    #     + str(distance.distances[0])
    #     + " | Left: "
    #     + str(distance.distances[1])
    #     + " | Front: "
    #     + str(distance.distances[2])
    #     + " | Right: "
    #     + str(distance.distances[3])
    #     + " | East: "
    #     + str(distance.distances[4])
    # )
