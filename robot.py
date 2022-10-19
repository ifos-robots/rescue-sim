import random
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
        self.is_in_swamp = False
        self.getting_victim = False
        self.getting_victim_steps = 0
        self.getting_victim_dir = None

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

        # print("angle_diff", angle_diff)
        if angle_diff > 360:
            angle_diff = angle_diff - 360
        elif angle_diff < -360:
            angle_diff = angle_diff + 360

        if angle_diff > 2:
            # print("angle_diff > 0")
            self.move(speed_ratio, -speed_ratio, bypass_rotating=True)
        elif angle_diff < -2:
            # print("angle_diff < 0")
            self.move(-speed_ratio, speed_ratio, bypass_rotating=True)
        else:
            # print("stop rotating")
            self.rotating = False
            self.move(0, 0)
            self.rotating_angle = 0
            self.rotating = False

    def rotate_in_angle(self, angle, speed_ratio):
        self.rotate_to_angle(self.gyro.angle_deg + angle, speed_ratio)

    def keep_rotating(self):
        self.rotate_to_angle(self.rotating_angle, self.rotating_speed)

    def abort_rotation(self):
        self.rotating = False
        self.move(0, 0)

    def distantiate_to_get_victim(self, dir):
        self.getting_victim = True
        self.getting_victim_steps = 25
        self.getting_victim_dir = dir
        if self.getting_victim_dir == "left":
            self.rotate_in_angle(-90, 0.5)
            print("rotating -90deg")
        elif self.getting_victim_dir == "right":
            self.rotate_in_angle(90, 0.5)
            print("rotating 90deg")
        self.getting_victim_steps -= 1

    def keep_getting_victim(self):
        if self.rotating:
            self.keep_rotating()
            return
        if self.getting_victim_steps > 9:
            self.move(0.5, 0.5)
            print("forward")
        elif self.getting_victim_steps == 9:
            if self.getting_victim_dir == "left":
                self.rotate_in_angle(90, 0.5)
                print("rotating 90deg")
            elif self.getting_victim_dir == "right":
                self.rotate_in_angle(-90, 0.5)
                print("rotating -90deg")
        elif self.getting_victim_steps > 1:
            self.move(-0.5, -0.5)
            print("backward")
        elif self.getting_victim_steps == 0:
            self.getting_victim = False

        self.getting_victim_steps -= 1


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
            collision_zones[i] = 5
        elif distances[i] < 0.2:
            collision_zones[i] = 4
        elif distances[i] < 0.3:
            collision_zones[i] = 3
        elif distances[i] < 0.4:
            collision_zones[i] = 2
        elif distances[i] < 0.5:
            collision_zones[i] = 1
        else:
            collision_zones[i] = 0

    return collision_zones


def which_way_to_turn(distances):
    return "left" if distances[0] >= distances[4] else "right"


def turn_to_freest_way(distances, movement, lock_rotation=True):
    if not lock_rotation:
        if which_way_to_turn(distances) == "left":
            movement.move(-0.5, 0.5)
        else:
            movement.move(0.5, -0.5)
    if which_way_to_turn(distances) == "left":
        movement.rotate_in_angle(90, 0.5)
    else:
        movement.rotate_in_angle(-90, 0.5)


def random_dir(pos):
    random.seed()
    print(pos, len(pos))
    if len(pos) == 1:
        print(0)
        return 0

    dir = random.randint(0, len(pos) - 1)

    print(dir)

    return dir


def movement_decision(
    distances, movement: Movement, color, gps, radio, victim_status, wait_sec
):
    if wait_sec is not None and wait_sec > 1:
        movement.move(0, 0, True)
        return

    collision_zones = collision_avoidance(distances)
    floor_area = floor_color_detection(color.rgb)

    if movement.getting_victim:
        movement.keep_getting_victim()
        return
    elif victim_status:
        if victim_status["left"][0] == "new" and victim_status["left"][1] == "Near":
            movement.distantiate_to_get_victim("left")
            return
        elif victim_status["right"][0] == "new" and victim_status["right"][1] == "Near":
            movement.distantiate_to_get_victim("right")
            return

    lack_of_progress_check = gps.lackOfProgressDetector(0.006)
    if lack_of_progress_check == "yes":
        movement.lack_of_progress_counter += 1
        # print("lack_of_progress_counter", movement.lack_of_progress_counter)

        if movement.lack_of_progress_counter == 15:
            # print("Moving due to lack of progress")
            movement.move(-0.8, -0.8)
            movement.rotate_in_angle(180, 0.5)
        elif movement.lack_of_progress_counter > 25:
            print("Oh no, I'm stuck!")
            movement.abort_rotation()
            movement.lack_of_progress_counter = 0
            radio.lackOfProgressHelp()
    elif lack_of_progress_check == "no":
        movement.lack_of_progress_counter = 0

    if movement.rotating:
        movement.keep_rotating()
        if (
            collision_zones[0] > 4
            and collision_zones[1] > 4
            or collision_zones[3] > 4
            and collision_zones[4] > 4
        ):
            # print("Collision on side")
            # print("Backward")
            movement.move(-0.5, -0.5)
        # Free way
        return

    if floor_area == "hole":
        if collision_zones[2] < 4:
            turn_to_freest_way(distances, movement)
            print("Moving due to hole")
            return
        else:
            print("Phew! Its not a hole. Its a wall")
    elif floor_area == "swamp":
        if not movement.is_in_swamp:
            movement.is_in_swamp = True
            print("Okay. Take a deep breath and lets go!")
    elif floor_area == "normal":
        if movement.is_in_swamp:
            movement.is_in_swamp = False
            print("I'm out of the swamp")

    # Collision in front
    if collision_zones[2] > 4:
        # print("Collision in front")
        left_free = collision_zones[0] < 4 or collision_zones[1] < 4
        right_free = collision_zones[3] < 4 or collision_zones[4] < 4
        # Both sides are free
        if left_free and right_free:
            turn_to_freest_way(distances, movement)

        elif left_free:
            movement.move(0, 0.5)
            # print("Turning left")
        elif right_free:
            movement.move(0.5, 0)
            # print("Turning right")
        # Both sides are blocked
        else:
            movement.rotate_in_angle(180, 0.5)
            # print("Turning back")
    # No collision in front but left is blocked
    elif collision_zones[0] > 4 and collision_zones[1] > 4:
        # print("Collision on left")
        # print("Turning right")
        movement.move(0.5, -0.5)
    # No collision in front but right is blocked
    elif collision_zones[3] > 4:
        # print("Collision on right")
        # print("Turning left")
        movement.move(-0.2, 0.2)
    # Free way
    else:
        movement.move(1, 1)
