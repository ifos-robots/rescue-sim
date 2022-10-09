from this import d
from typing import Tuple

from cv2 import rotate


class Wheel:
    def __init__(self, wheel, max_speed: float):
        self.wheel = wheel
        self.max_speed = max_speed
        self.speed = 0

        self.wheel.setPosition(float("inf"))
        self.wheel.setVelocity(0)

    def move(self, speed_ratio: float):
        if speed_ratio > 1:
            speed_ratio = 1
        elif speed_ratio < -1:
            speed_ratio = -1

        self.speed = speed_ratio * self.max_speed
        self.wheel.setVelocity(self.speed)


class Movement:
    def __init__(self, left_wheel, right_wheel, gyro):
        self.left_wheel = left_wheel
        self.right_wheel = right_wheel
        self.gyro = gyro
        self.rotating = False

    def move(self, left_speed_ratio, right_speed_ratio, bypass_rotating=False):
        if self.rotating and not bypass_rotating:
            return

        self.left_wheel.move(left_speed_ratio)
        self.right_wheel.move(right_speed_ratio)

    def rotate_to_angle(self, angle, speed_ratio):
        pass
        # self.rotating = True
        # self.rotating_angle_to_rotate = angle
        # self.rotating_speed = speed_ratio
        # initial_angle = self.gyro.angle_deg
        # angle_diff = initial_angle - angle
        # print("angle_diff", angle_diff)
        # rotation_diff = max(initial_angle, angle) - min(round(initial_angle), angle)
        # print("rotation_diff", rotation_diff)
        # if angle_diff > 180 or angle_diff < -180:
        #     rotation_diff = 360 - rotation_diff
        #     print("rotation_diff 2", rotation_diff)

        # if angle_diff > 0:
        #     print("angle_diff > 0")
        #     self.move(speed_ratio, -speed_ratio, bypass_rotating=True)
        # else:
        #     print("angle_diff < 0")
        #     self.move(-speed_ratio, speed_ratio, bypass_rotating=True)

        # if rotation_diff > 5:
        #     print("rotation_diff > 5")
        #     rotation_diff = max(self.gyro.angle_deg, angle) - min(
        #         round(self.gyro.angle_deg), angle
        #     )
        #     if rotation_diff > 180:
        #         print("rotation_diff > 180")
        #         rotation_diff = 360 - rotation_diff

        # else:
        #     print("rotation_diff < 5")
        #     print("stop rotating")
        #     self.move(0, 0)
        #     self.angle_to_rotate = 0
        #     self.rotating = False

    def rotate_in_angle(self, angle, speed_ratio):
        self.rotating = True
        self.rotating_angle = angle
        self.rotating_speed = speed_ratio

        initial_angle = self.gyro.angle_deg
        print("Current angle: ", initial_angle)
        print("Rotation angle: ", angle)

        angle_diff = initial_angle - angle
        rotation_diff = max(initial_angle, angle) - min(round(initial_angle), angle)
        if angle_diff > 180 or angle_diff < -180:
            rotation_diff = 360 - rotation_diff

        if angle_diff > 0:
            print("Rotating right")
            self.move(speed_ratio, -speed_ratio, bypass_rotating=True)
        else:
            print("Rotating left")
            self.move(-speed_ratio, speed_ratio, bypass_rotating=True)

        if rotation_diff > 5:
            print("Angle difference: ", rotation_diff)
            rotation_diff = max(self.gyro.angle_deg, angle) - min(
                round(self.gyro.angle_deg), angle
            )
            if rotation_diff > 180:
                rotation_diff = 360 - rotation_diff

            self.rotating_angle = rotation_diff

        else:
            print("Stop rotating")
            self.move(0, 0)
            self.angle_to_rotate = 0
            self.rotating = False

    def keep_rotating(self):
        if self.rotating:
            self.rotate_in_angle(self.rotating_angle, self.rotating_speed)


def coliision_avoidance(distances) -> Tuple[int, int, int, int, int]:
    collision_zones = [0, 0, 0, 0, 0]

    for i in range(len(distances)):
        if distances[i] < 0.1:
            collision_zones[i] = 2
        elif distances[i] < 0.2:
            collision_zones[i] = 1

    return collision_zones


def movement_decision(distances, movement: Movement):
    collision_zones = coliision_avoidance(distances)

    if movement.rotating:
        movement.keep_rotating()
        if (
            collision_zones[0] > 1
            and collision_zones[1] > 1
            or collision_zones[3] > 1
            and collision_zones[4] > 1
        ):
            print("Collision on side")
            movement.move(-0.5, -0.5)
            print("Backward")
        # Free way
        return

    # Collision in front
    if collision_zones[2] > 0:
        print("Collision in front")
        # Left is free
        if collision_zones[0] < 1:
            movement.move(0, 0.5)
            print("Turning left")
        # Right is free
        elif collision_zones[4] < 1:
            movement.move(0.5, 0)
            print("Turning right")
        # Both sides are blocked
        else:
            movement.rotate_in_angle(180, 0.5)
            print("Turning back")
    # No collision in front but left is blocked
    elif collision_zones[0] > 1 and collision_zones[1] > 1:
        print("Collision on left")
        movement.move(0.5, -0.5)
        print("Turning right")
    # No collision in front but right is blocked
    elif collision_zones[3] > 1 and collision_zones[4] > 1:
        print("Collision on right")
        movement.move(-0.5, 0.5)
        print("Turning left")
    # Free way
    else:
        movement.move(1, 1)
        print("No collision")
