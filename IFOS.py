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
cameras = Cameras([robot.getDevice("camera right"), robot.getDevice("camera front"), robot.getDevice("camera left")], timeStep)

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


while robot.step(timeStep) != -1:
    update_sensors(robot.getTime())
    status, detections = victimDetection.detectionPipeline()
    # victim detection (TODO: report victim)
    if status == 'new':
        print(detections)
        

    movement_decision(distance.distances, movement, color, gps, radio, status, detections)


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
