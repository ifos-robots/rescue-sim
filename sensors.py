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
