from vex import *
import math

# ------------------ BRAIN & CONTROLLER ------------------
brain = Brain()
wait(30, MSEC)
controller = Controller()

# ------------------ DRIVE MOTORS ------------------
left_motor_a = Motor(Ports.PORT1, GearSetting.RATIO_6_1, False)
left_motor_b = Motor(Ports.PORT2, GearSetting.RATIO_6_1, False)
left_motor_c = Motor(Ports.PORT11, GearSetting.RATIO_6_1, False)

right_motor_a = Motor(Ports.PORT6, GearSetting.RATIO_6_1, True)
right_motor_b = Motor(Ports.PORT7, GearSetting.RATIO_6_1, True)
right_motor_c = Motor(Ports.PORT10, GearSetting.RATIO_6_1, True)

left_drive = MotorGroup(left_motor_a, left_motor_b, left_motor_c)
right_drive = MotorGroup(right_motor_a, right_motor_b, right_motor_c)

# ------------------ INTAKE MOTORS ------------------
bottom_motor = Motor(Ports.PORT8, GearSetting.RATIO_18_1, False)
top_motor = Motor(Ports.PORT9, GearSetting.RATIO_18_1, False)

# ------------------ PNEUMATICS ------------------
silo_ramp = DigitalOut(brain.three_wire_port.a)
parking_aid = DigitalOut(brain.three_wire_port.b)

# ------------------ ODOMETRY ------------------
odom_rotation = Rotation(Ports.PORT3, False)

ODOM_WHEEL_DIAMETER = 2.75  # inches
ODOM_OFFSET = 7.0           # inches (wheel is 7 inches behind center)

# ------------------ DRIVETRAIN ------------------
wheel_travel = 239.4
track_width = 317.5
wheel_base = 301.6
external_ratio = 0.6

drivetrain = DriveTrain(
    left_drive,
    right_drive,
    wheel_travel,
    track_width,
    wheel_base,
    MM,
    external_ratio
)

drivetrain.set_turn_velocity(50, PERCENT)

# ------------------ CONSTANTS ------------------
DEADBAND = 5
INTAKE_SPEED = 300
TURN_SPEED_LIMIT = 50

# ------------------ HELPER FUNCTIONS ------------------
def clamp(val, low=-100, high=100):
    if val > high:
        return high
    if val < low:
        return low
    return val

def apply_deadband(value, threshold=DEADBAND):
    return 0 if abs(value) < threshold else value

# ------------------ ODOMETRY FUNCTIONS ------------------
def reset_odom():
    odom_rotation.reset_position()

def get_odom_inches():
    return (odom_rotation.position(DEGREES) / 360) * (math.pi * ODOM_WHEEL_DIAMETER)

def get_turn_degrees():
    side_distance = get_odom_inches()
    return (side_distance / (2 * math.pi * ODOM_OFFSET)) * 360

def odom_turn(target_degrees, speed=30):
    reset_odom()

    direction = RIGHT if target_degrees > 0 else LEFT
    drivetrain.set_turn_velocity(speed, PERCENT)
    drivetrain.turn(direction)

    while abs(get_turn_degrees()) < abs(target_degrees):
        wait(10, MSEC)

    drivetrain.stop()

# ------------------ PRE AUTON ------------------
def pre_autonomous():
    left_motor_a.reset_position()
    right_motor_a.reset_position()
    bottom_motor.reset_position()
    top_motor.reset_position()
    reset_odom()

    silo_ramp.set(False)
    parking_aid.set(False)

    wait(100, MSEC)

# ------------------ AUTONOMOUS ------------------
def autonomous():
    drivetrain.set_drive_velocity(25, PERCENT)

    # Drive back 36 inches
    drivetrain.drive_for(REVERSE, 36, INCHES, wait=True)
    wait(1, SECONDS)

    # Intake forward (L1 behavior)
    bottom_motor.spin(FORWARD, INTAKE_SPEED, PERCENT)
    top_motor.spin(FORWARD, INTAKE_SPEED, PERCENT)
    wait(2, SECONDS)

    bottom_motor.stop()
    top_motor.stop()

    wait(1, SECONDS)

    # Odometry-based turn (same path, more accurate)
    odom_turn(20, speed=30)

    # Drive back 12 inches
    drivetrain.drive_for(REVERSE, 12, INCHES, wait=True)

    # Intake reverse (R1 behavior)
    bottom_motor.spin(REVERSE, INTAKE_SPEED, PERCENT)
    top_motor.spin(REVERSE, INTAKE_SPEED, PERCENT)
    wait(2, SECONDS)

    bottom_motor.stop()
    top_motor.stop()

# ------------------ DRIVER CONTROL ------------------
def user_control():
    while True:
        # Drive
        forward = apply_deadband(controller.axis3.position())
        turn = apply_deadband(controller.axis1.position())
        turn *= (TURN_SPEED_LIMIT / 100.0)

        left_power = clamp(-forward - turn)
        right_power = clamp(-forward + turn)

        left_drive.spin(FORWARD, left_power, PERCENT)
        right_drive.spin(FORWARD, right_power, PERCENT)

        # Intake controls
        if controller.buttonL1.pressing():
            bottom_motor.spin(FORWARD, INTAKE_SPEED, PERCENT)
            top_motor.spin(FORWARD, INTAKE_SPEED, PERCENT)

        elif controller.buttonL2.pressing():
            bottom_motor.spin(FORWARD, INTAKE_SPEED, PERCENT)
            top_motor.spin(REVERSE, INTAKE_SPEED, PERCENT)

        elif controller.buttonR1.pressing():
            bottom_motor.spin(REVERSE, INTAKE_SPEED, PERCENT)
            top_motor.spin(REVERSE, INTAKE_SPEED, PERCENT)

        else:
            bottom_motor.stop()
            top_motor.stop()

        # Pneumatics
        parking_aid.set(controller.buttonX.pressing())
        silo_ramp.set(controller.buttonR2.pressing())

        wait(20, MSEC)

# ------------------ COMPETITION ------------------
comp = Competition(user_control, autonomous)
pre_autonomous()
