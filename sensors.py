import math


class Gyroscope:
    def __init__(self, gyro, axis, time_step):
        self.sensor = gyro
        self.sensor.enable(time_step)

        self.axis = axis

        self.angle = 0

        self.past_exec_time = 0.0

    def update(self, time):
        elapsed_time = time - self.past_exec_time
        # rotation (rad) = angular velocity (rad/s) * time (s)
        rotation_during_timestep = self.sensor.getValues()[self.axis] * elapsed_time

        raw_angle = self.angle + rotation_during_timestep
        self.angle = self.__normalizeRadAngle(raw_angle)

        self.past_exec_time = time

    @property
    def angle_deg(self):
        return self.angle * (180 / math.pi)

    def __normalizeRadAngle(self, angle):
        return angle % (2 * math.pi)


class DistanceSensors:
    def __init__(self, sensors, time_step):
        self.distances = [0, 0, 0, 0, 0]

        self.left_sensor = sensors[0]
        self.front_left_sensor = sensors[1]
        self.front_sensor = sensors[2]
        self.front_right_sensor = sensors[3]
        self.right_sensor = sensors[4]

        self.left_sensor.enable(time_step)
        self.front_left_sensor.enable(time_step)
        self.front_sensor.enable(time_step)
        self.front_right_sensor.enable(time_step)
        self.right_sensor.enable(time_step)

        self.left_distance = 0
        self.front_left_distance = 0
        self.front_distance = 0
        self.front_right_distance = 0
        self.right_distance = 0

    def update(self):
        self.left_distance = self.left_sensor.getValue()
        self.front_left_distance = self.front_left_sensor.getValue()
        self.front_distance = self.front_sensor.getValue()
        self.front_right_distance = self.front_right_sensor.getValue()
        self.right_distance = self.right_sensor.getValue()

        self.distances = [
            self.left_distance,
            self.front_left_distance,
            self.front_distance,
            self.front_right_distance,
            self.right_distance,
        ]


class Color:
    def __init__(self, sensor, time_step):
        self.sensor = sensor
        self.sensor.enable(time_step)

        self.color = {
            "red": None,
            "green": None,
            "blue": None,
        }

    def update(self):
        image = self.sensor.getImage()
        self.color["red"] = self.sensor.imageGetRed(image, 1, 0, 0)
        self.color["green"] = self.sensor.imageGetGreen(image, 1, 0, 0)
        self.color["blue"] = self.sensor.imageGetBlue(image, 1, 0, 0)

    @property
    def red(self):
        return self.color["red"]

    @property
    def green(self):
        return self.color["green"]

    @property
    def blue(self):
        return self.color["blue"]

    @property
    def rgb(self):
        return self.color


class GPS:
    def __init__(self, sensor, time_step):
        self.sensor = sensor
        self.sensor.enable(time_step)

        self.coordinates = {
            "x": None,
            "y": None,
            "z": None,
        }

        self.previousCoordinates = {
            "x": None,
            "y": None,
            "z": None,
        }

        self.lackOfProgressClock = 10

    def update(self):
        coordinates = self.sensor.getValues()

        self.coordinates["x"] = coordinates[0]
        self.coordinates["y"] = coordinates[1]
        self.coordinates["z"] = coordinates[2]

    def lackOfProgressDetector(self, min_delta):
        self.lackOfProgressClock -= 1
        if self.lackOfProgressClock > 0:
            return "clock"

        self.lackOfProgressClock = 10

        if self.coordinates["x"] == None or self.previousCoordinates["x"] == None:
            self.previousCoordinates["x"] = self.coordinates["x"]
            self.previousCoordinates["y"] = self.coordinates["y"]
            self.previousCoordinates["z"] = self.coordinates["z"]
            return "no"

        deltaX = abs(self.coordinates["x"] - self.previousCoordinates["x"])
        deltaY = abs(self.coordinates["y"] - self.previousCoordinates["y"])

        lack_detected = "no"
        if deltaX < min_delta and deltaY < min_delta:
            lack_detected = "yes"

        self.previousCoordinates["x"] = self.coordinates["x"]
        self.previousCoordinates["y"] = self.coordinates["y"]
        self.previousCoordinates["z"] = self.coordinates["z"]

        return lack_detected
