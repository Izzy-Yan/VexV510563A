#region VEXcode Generated Robot Configuration
from vex import *
import urandom
import math

# Brain should be defined by default
#Start of Code
brain=Brain()

# Robot configuration code


# wait for rotation sensor to fully initialize
wait(30, MSEC)


# Make random actually random
def initializeRandomSeed():
    wait(100, MSEC)
    random = brain.battery.voltage(MV) + brain.battery.current(CurrentUnits.AMP) * 100 + brain.timer.system_high_res()
    urandom.seed(int(random))
      
# Set random seed 
initializeRandomSeed()


def play_vexcode_sound(sound_name):
    # Helper to make playing sounds from the V5 in VEXcode easier and
    # keeps the code cleaner by making it clear what is happening.
    print("VEXPlaySound:" + sound_name)
    wait(5, MSEC)

# add a small delay to make sure we don't print in the middle of the REPL header
wait(200, MSEC)
# clear the console to make sure we don't have the REPL in the console
print("\033[2J")

#endregion VEXcode Generated Robot Configuration
#region VEXcode Generated Robot Configuration
from vex import *
import urandom
import math

# Brain and Controller
brain = Brain()
controller = Controller()

# ------------------ DRIVE MOTORS ------------------
right_motor_a = Motor(Ports.PORT7, GearSetting.RATIO_6_1, True)
right_motor_b = Motor(Ports.PORT5, GearSetting.RATIO_6_1, True)
right_motor_c = Motor(Ports.PORT6, GearSetting.RATIO_6_1, True)

left_motor_a = Motor(Ports.PORT10, GearSetting.RATIO_6_1, False)
left_motor_b = Motor(Ports.PORT9, GearSetting.RATIO_6_1, False)
left_motor_c = Motor(Ports.PORT8, GearSetting.RATIO_6_1, False)

left_drive = MotorGroup(left_motor_a, left_motor_b, left_motor_c)
right_drive = MotorGroup(right_motor_a, right_motor_b, right_motor_c)

# ------------------ INTAKE MOTORS ------------------
bottom_motor = Motor(Ports.PORT4, GearSetting.RATIO_18_1, False)
top_motor = Motor(Ports.PORT3, GearSetting.RATIO_18_1, False)

# ------------------ PNEUMATICS ------------------
# Silo ramp removed as requested
parking_aid = DigitalOut(brain.three_wire_port.a)

# ------------------ TOGGLE STATES ------------------
# Start with parking deployed = False (Retracted/Up)
parking_deployed = False
last_X_state = False

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
    return max(min(val, high), low)

def apply_deadband(value, threshold=DEADBAND):
    return 0 if abs(value) < threshold else value

# ------------------ PRE AUTON ------------------
def pre_autonomous():
    left_motor_a.reset_position()
    right_motor_a.reset_position()
    bottom_motor.reset_position()
    top_motor.reset_position()

    # FORCE PARKING AID UP (RETRACTED) AT START
    # If this makes it go DOWN instead, change False to True
    parking_aid.set(False) 
    
    wait(100, MSEC)

# ------------------ AUTONOMOUS ------------------
def autonomous():
    parking_deployed = False
    parking_aid.set(False)
    drivetrain.set_drive_velocity(10, PERCENT)
    drivetrain.set_turn_velocity(10, PERCENT)

    drivetrain.drive_for(FORWARD, 16, INCHES)
    drivetrain.turn_for(LEFT, 30, DEGREES)

    drivetrain.drive_for(FORWARD, 18, INCHES)
    drivetrain.turn_for(RIGHT, 55.5, DEGREES)
    drivetrain.drive_for(FORWARD, 30, INCHES)

    bottom_motor.spin(REVERSE, INTAKE_SPEED, PERCENT)
    top_motor.spin(FORWARD, INTAKE_SPEED, PERCENT)
    wait(.3, SECONDS)
    bottom_motor.stop()
    top_motor.stop()

    bottom_motor.spin(FORWARD, INTAKE_SPEED, PERCENT)
    top_motor.spin(REVERSE, INTAKE_SPEED, PERCENT)
    wait(10, SECONDS)
    bottom_motor.stop()
    top_motor.stop()

    drivetrain.drive_for(REVERSE, 15, INCHES)
    drivetrain.turn_for(RIGHT, 26.5, DEGREES)
    drivetrain.drive_for(FORWARD, 21.5, INCHES)
    drivetrain.turn_for(LEFT, 46, DEGREES)
    wait(3, SECONDS)

    drivetrain.set_drive_velocity(80, PERCENT)
    drivetrain.drive_for(REVERSE, 50, INCHES)
    wait(1, SECONDS)
    drivetrain.drive_for(REVERSE, 2, INCHES)


# ------------------ DRIVER CONTROL ------------------
def user_control():
    global parking_deployed, last_X_state

    # Ensure variable matches the pre-auton state (False = Up)
    parking_deployed = False

    while True:
        # Drive
        forward = apply_deadband(controller.axis3.position())
        turn = apply_deadband(controller.axis1.position())
        turn *= (TURN_SPEED_LIMIT / 100)

        left_drive.spin(FORWARD, clamp(forward - turn), PERCENT)
        right_drive.spin(FORWARD, clamp(forward + turn), PERCENT)

        # Intake
        if controller.buttonR1.pressing():
            bottom_motor.spin(REVERSE, INTAKE_SPEED, PERCENT)
            top_motor.spin(FORWARD, INTAKE_SPEED, PERCENT)
        elif controller.buttonR2.pressing():
            bottom_motor.spin(FORWARD, INTAKE_SPEED, PERCENT)
            top_motor.spin(REVERSE, INTAKE_SPEED, PERCENT)
        elif controller.buttonL1.pressing():
            bottom_motor.spin(REVERSE, INTAKE_SPEED, PERCENT)
            top_motor.spin(REVERSE, INTAKE_SPEED, PERCENT)
        else:
            bottom_motor.stop()
            top_motor.stop()

        # ------------------ PARKING AID TOGGLE (X) ------------------
        # When X is pressed, it toggles to Deployed (True)
        current_X = controller.buttonX.pressing()
        if current_X and not last_X_state:
            parking_deployed = not parking_deployed
            parking_aid.set(parking_deployed)
        last_X_state = current_X

        wait(20, MSEC)

# ------------------ COMPETITION ------------------
comp = Competition(user_control, autonomous)
pre_autonomous()




#Auton that worked:def autonomous():
   # parking_aid.set(False)
    #drivetrain.set_drive_velocity(10, PERCENT)
   # drivetrain.set_turn_velocity(10, PERCENT)

   # drivetrain.drive_for(FORWARD, 40, INCHES)
   # wait(1, SECONDS)

    #drivetrain.turn_for(RIGHT, 27.5, DEGREES)
    #drivetrain.drive_for(FORWARD, 11.5, INCHES)

    #bottom_motor.spin(REVERSE, INTAKE_SPEED, PERCENT)
    #top_motor.spin(FORWARD, INTAKE_SPEED, PERCENT)
    #wait(.5, SECONDS)
    #bottom_motor.stop()
    #top_motor.stop()

    #bottom_motor.spin(FORWARD, INTAKE_SPEED, PERCENT)
    #top_motor.spin(REVERSE, INTAKE_SPEED, PERCENT)
    #wait(10, SECONDS)
    #bottom_motor.stop()
    #top_motor.stop()

   # drivetrain.drive_for(REVERSE, 16, INCHES)
    #drivetrain.turn_for(RIGHT, 26.5, DEGREES)
   # drivetrain.drive_for(FORWARD, 21.5, INCHES)
   # drivetrain.turn_for(RIGHT, 45, DEGREES)
   # wait(3, SECONDS)

    #drivetrain.set_drive_velocity(100, PERCENT)
    #drivetrain.drive_for(FORWARD, 50, INCHES)
   # wait(1, SECONDS)
   # drivetrain.drive_for(FORWARD, 10, INCHES)
