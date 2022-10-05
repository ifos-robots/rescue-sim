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
    def angle_dg(self):
        return self.angle * (180 / math.pi)

    def __normalizeRadAngle(self, angle):
        return angle % (2 * math.pi)
