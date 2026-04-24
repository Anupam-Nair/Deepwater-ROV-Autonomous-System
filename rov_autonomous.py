import time
import random
import math

# -------------------------------
# ENVIRONMENT + OBJECTS
# -------------------------------

class Object:
    def __init__(self, id):
        self.id = id
        self.position = [
            random.randint(5, 15),
            random.randint(5, 15),
            random.randint(3, 10)
        ]
        self.picked = False

# -------------------------------
# ROV SYSTEM
# -------------------------------

class ROV:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.yaw = 0
        self.holding = None
        self.battery = 100
        self.max_depth = 15

    def move_towards(self, target):
        if self.x < target[0]:
            self.x += 1
        elif self.x > target[0]:
            self.x -= 1

        if self.y < target[1]:
            self.y += 1
        elif self.y > target[1]:
            self.y -= 1

        if self.z < target[2] and self.z < self.max_depth:
            self.z += 1
        elif self.z > target[2]:
            self.z -= 1

        self.consume_battery()

    def consume_battery(self):
        self.battery -= 0.5

    def distance_to(self, target):
        return math.sqrt(
            (self.x - target[0])**2 +
            (self.y - target[1])**2 +
            (self.z - target[2])**2
        )

    def status(self):
        print(f"ROV -> Pos({self.x},{self.y},{self.z}) | Battery:{self.battery:.1f}% | Holding:{self.holding}")

# -------------------------------
# GRIPPER SYSTEM
# -------------------------------

class Gripper:
    def pick(self, rov, obj):
        if rov.distance_to(obj.position) < 1:
            rov.holding = obj.id
            obj.picked = True
            print(f"Picked Object {obj.id}")

    def release(self, rov):
        print(f"Released Object {rov.holding}")
        rov.holding = None

# -------------------------------
# AUTONOMOUS CONTROLLER
# -------------------------------

class AutonomousController:
    def __init__(self, rov, objects):
        self.rov = rov
        self.objects = objects
        self.state = "SEARCH"
        self.current_target = None
        self.gripper = Gripper()

    def find_next_object(self):
        for obj in self.objects:
            if not obj.picked:
                return obj
        return None

    def step(self):
        if self.rov.battery <= 10:
            self.state = "RETURN"

        if self.state == "SEARCH":
            print("[STATE] SEARCH")
            self.current_target = self.find_next_object()
            if self.current_target:
                print(f"Targeting Object {self.current_target.id}")
                self.state = "NAVIGATE"

        elif self.state == "NAVIGATE":
            print("[STATE] NAVIGATE")
            self.rov.move_towards(self.current_target.position)
            dist = self.rov.distance_to(self.current_target.position)
            print(f"Distance to target: {dist:.2f}")

            if dist < 1:
                self.state = "PICK"

        elif self.state == "PICK":
            print("[STATE] PICK")
            self.gripper.pick(self.rov, self.current_target)
            self.state = "RETURN"

        elif self.state == "RETURN":
            print("[STATE] RETURN TO BASE")
            base = [0, 0, 0]
            self.rov.move_towards(base)

            if self.rov.distance_to(base) < 1:
                if self.rov.holding:
                    self.gripper.release(self.rov)
                self.state = "SEARCH"

# -------------------------------
# MANUAL CONTROL
# -------------------------------

def manual_control(rov, objects):
    gripper = Gripper()
    print("\nManual Mode Controls:")
    print("w/s/a/d = move | q/e = up/down | p = pick | x = exit")

    while True:
        cmd = input("Command: ")

        if cmd == 'x':
            break
        elif cmd == 'w':
            rov.x += 1
        elif cmd == 's':
            rov.x -= 1
        elif cmd == 'a':
            rov.y += 1
        elif cmd == 'd':
            rov.y -= 1
        elif cmd == 'q':
            rov.z += 1
        elif cmd == 'e':
            rov.z -= 1
        elif cmd == 'p':
            for obj in objects:
                if not obj.picked:
                    gripper.pick(rov, obj)

        rov.consume_battery()
        rov.status()

# -------------------------------
# MAIN EXECUTION
# -------------------------------

def main():
    rov = ROV()
    objects = [Object(i) for i in range(3)]

    print("\nObjects in Environment:")
    for obj in objects:
        print(f"Object {obj.id} at {obj.position}")

    mode = input("\nSelect Mode (manual/autonomous): ")

    if mode == "manual":
        manual_control(rov, objects)

    elif mode == "autonomous":
        controller = AutonomousController(rov, objects)

        print("\nAutonomous Mission Started...\n")

        while True:
            controller.step()
            rov.status()

            if all(obj.picked for obj in objects) and rov.distance_to([0,0,0]) < 1:
                print("\nMission Complete: All objects retrieved.")
                break

            time.sleep(0.5)

if __name__ == "__main__":
    main()
