from this import d
from typing import Tuple


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
        self.lack_of_progress_counter = 0

    def move(self, left_speed_ratio, right_speed_ratio, bypass_rotating=False):
        if self.rotating and not bypass_rotating:
            return

        self.left_wheel.move(left_speed_ratio)
        self.right_wheel.move(right_speed_ratio)

    def rotate_to_angle(self, angle, speed_ratio):
        self.rotating = True
        self.rotating_angle = angle
        self.rotating_speed = speed_ratio

        current_angle = self.gyro.angle_deg
        angle_diff = current_angle - angle

        print("angle_diff", angle_diff)
        if angle_diff > 360:
            angle_diff = angle_diff - 360
        elif angle_diff < -360:
            angle_diff = angle_diff + 360

        if angle_diff > 10:
            print("angle_diff > 0")
            self.move(speed_ratio, -speed_ratio, bypass_rotating=True)
        elif angle_diff < -10:
            print("angle_diff < 0")
            self.move(-speed_ratio, speed_ratio, bypass_rotating=True)
        else:
            print("stop rotating")
            self.rotating = False
            self.move(0, 0)
            self.rotating_angle = 0
            self.rotating = False

    def rotate_in_angle(self, angle, speed_ratio):
        self.rotate_to_angle(self.gyro.angle_deg + angle, speed_ratio)

    def keep_rotating(self):
        self.rotate_to_angle(self.rotating_angle, self.rotating_speed)


def floor_color_detection(color):
    if color["red"] <= 54 and color["green"] <= 54 and color["blue"] <= 54:
        return "hole"
    elif (
        color["red"] > 230
        and color["red"] < 245
        and color["green"] > 200
        and color["green"] < 220
        and color["blue"] > 120
        and color["blue"] < 140
    ):
        return "swamp"
    else:
        return "normal"


def collision_avoidance(distances) -> Tuple[int, int, int, int, int]:
    collision_zones = [0, 0, 0, 0, 0]

    for i in range(len(distances)):
        if distances[i] < 0.1:
            collision_zones[i] = 2
        elif distances[i] < 0.2:
            collision_zones[i] = 1

    return collision_zones


def movement_decision(distances, movement: Movement, color, gps):
    collision_zones = collision_avoidance(distances)
    floor_area = floor_color_detection(color.rgb)

    lack_of_progress_check = gps.lackOfProgressDetector(0.001)
    if lack_of_progress_check == "yes":
        movement.lack_of_progress_counter += 1
        print("lack_of_progress_counter", movement.lack_of_progress_counter)

        if movement.lack_of_progress_counter > 15:
            print("Moving due to lack of progress")
            movement.move(-0.8, -0.8)
            movement.rotate_in_angle(180, 0.5)
            movement.lack_of_progress_counter = 0

    elif lack_of_progress_check == "no":
        movement.lack_of_progress_counter = 0

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

    if floor_area == "hole":
        if collision_zones[2] < 1:
            movement.rotate_in_angle(180, 0.5)
            print("Moving due to hole")
            return
        else:
            print("Phew! Its not a hole. Its a wall")
    if floor_area == "swamp":
        movement.rotate_in_angle(180, 0.5)
        print("Moving due to swamp")
        return

    # Collision in front
    if collision_zones[2] > 0:
        print("Collision in front")
        # Left is free
        if collision_zones[0] < 1 or collision_zones[1] < 1:
            movement.move(0, 0.5)
            print("Turning left")
        # Right is free
        elif collision_zones[4] < 1 or collision_zones[3] < 1:
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
