def collision_avoidance(distances):
    collision_zones = [0, 0, 0, 0, 0]

    for i in range(len(distances)):
        if distances[i] < 0.1:
            collision_zones[i] = 2
        elif distances[i] < 0.2:
            collision_zones[i] = 1

    if collision_zones[2] > 0:
        print("Collision in front")
        if collision_zones[0] < 1:
            print("Turning left")
        elif collision_zones[4] < 1:
            print("Turning right")
        else:
            print("Turning back")
