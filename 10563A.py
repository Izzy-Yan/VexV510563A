#region VEXcode Generated Robot Configuration
from vex import *
# Brain should be defined by default
brain=Brain()
# Robot configuration code
# wait for rotation sensor to fully initialize
wait(30, MSEC)
#endregion VEXcode Generated Robot Configuration
# ------------------------------------------
#
#   Project: Push Back Competition Robot
#   Author:
#   Created:
#   Configuration: 6-motor drive, intake on port 11, pneumatic lift
#
# ------------------------------------------
# Library imports
from vex import *

# Begin project code

# ========================================
# ROBOT CONFIGURATION
# ========================================

# Controller
controller = Controller()

# Drivetrain Motors
left_motor_a = Motor(Ports.PORT1, GearSetting.RATIO_6_1, False)
left_motor_b = Motor(Ports.PORT2, GearSetting.RATIO_6_1, False)
left_motor_c = Motor(Ports.PORT11, GearSetting.RATIO_6_1, False)
right_motor_a = Motor(Ports.PORT6, GearSetting.RATIO_6_1, True)
right_motor_b = Motor(Ports.PORT7, GearSetting.RATIO_6_1, True)
right_motor_c = Motor(Ports.PORT8, GearSetting.RATIO_6_1, True)

# Motor groups
left_drive = MotorGroup(left_motor_a, left_motor_b, left_motor_c)
right_drive = MotorGroup(right_motor_a, right_motor_b, right_motor_c)

# Intake Motor (Port 12)
intake_motor = Motor(Ports.PORT12, GearSetting.RATIO_18_1, False)

# Pneumatics for Intake Lift (Two pneumatics that move together)
intake_lift_1 = DigitalOut(brain.three_wire_port.a)
intake_lift_2 = DigitalOut(brain.three_wire_port.b)

# Drivetrain parameters (mm)
wheel_travel = 239.4
track_width = 317.5
wheel_base = 301.6
external_ratio = 0.6  # 3:5 gear ratio (3/5 = 0.6)

# Create drivetrain
drivetrain = DriveTrain(left_drive, right_drive, wheel_travel, track_width, wheel_base, MM, external_ratio)

# Set turning speed to 50% for autonomous
drivetrain.set_turn_velocity(50, PERCENT)

# ========================================
# CONSTANTS
# ========================================

DEADBAND = 5
INTAKE_SPEED = 100  # Adjust for optimal intake speed
TURN_SPEED_LIMIT = 50  # Limit turning speed to 50%

# ========================================
# UTILITY FUNCTIONS
# ========================================

def clamp(val, low=-100, high=100):
    """Clamp value between low and high"""
    if val > high:
        return high
    if val < low:
        return low
    return val

def apply_deadband(value, threshold=DEADBAND):
    """Return 0 if value is within deadband threshold"""
    return 0 if abs(value) < threshold else value

def set_intake_lift(up):
    """Control both pneumatics together for intake lift"""
    intake_lift_1.set(up)
    intake_lift_2.set(up)

# ========================================
# COMPETITION FUNCTIONS
# ========================================

def pre_autonomous():
    # actions to do when the program starts
    # Reset motor positions
    left_motor_a.reset_position()
    right_motor_a.reset_position()
    intake_motor.reset_position()
    
    # Make sure lift starts in down position
    set_intake_lift(False)
    
    wait(100, MSEC)

def autonomous():
    # place autonomous code here
    
    # Set drive velocity to 50%
    drivetrain.set_drive_velocity(25, PERCENT)
    
    # Move forward 36 inches
    drivetrain.drive_for(REVERSE, 36, INCHES, wait=True)

    wait(1, SECONDS)
    
    # Run intake forward for 2 seconds
    intake_motor.spin(FORWARD, INTAKE_SPEED, PERCENT)
    wait(2, SECONDS)
    intake_motor.stop()
    
    # Pause for 3 seconds
    wait(3, SECONDS)
    
    # Turn 45 degrees
    drivetrain.turn_for(RIGHT, 20, DEGREES, wait=True)
    
    # Move forward 12 inches
    drivetrain.drive_for(REVERSE, 12, INCHES, wait=True)
    
    # Intake reverse for 3 seconds
    intake_motor.spin(REVERSE, INTAKE_SPEED, PERCENT)
    wait(3, SECONDS)
    intake_motor.stop()

def user_control():
    # place driver control in this while loop
    while True:
        # ========================================
        # DRIVETRAIN CONTROL (Joysticks)
        # ========================================
        # Left stick vertical (Axis3) = forward/backward
        # Right stick horizontal (Axis1) = turning
        
        forward = apply_deadband(controller.axis3.position())
        turn = apply_deadband(controller.axis1.position())
        
        # Limit turn speed to 50%
        turn = turn * (TURN_SPEED_LIMIT / 100.0)
        
        # Arcade drive calculation (reversed for correct direction)
        left_power = clamp(-forward - turn)
        right_power = clamp(-forward + turn)
        
        # Apply to motors
        left_drive.spin(FORWARD, left_power, PERCENT)
        right_drive.spin(FORWARD, right_power, PERCENT)
        
        # ========================================
        # INTAKE CONTROL (R1 = forward, R2 = reverse)
        # ========================================
        
        if controller.buttonR1.pressing():
            # R1 pressed - intake forward (collect blocks)
            intake_motor.spin(FORWARD, INTAKE_SPEED, PERCENT)
        elif controller.buttonR2.pressing():
            # R2 pressed - intake reverse (spit out blocks)
            intake_motor.spin(REVERSE, INTAKE_SPEED, PERCENT)
        else:
            # No button pressed - stop intake
            intake_motor.stop()
        
        # ========================================
        # INTAKE LIFT CONTROL (L1 = up, L2 = down)
        # ========================================
        
        if controller.buttonL1.pressing():
            # L1 pressed - lift up (add air to both pneumatics)
            set_intake_lift(True)
        elif controller.buttonL2.pressing():
            # L2 pressed - lift down (remove air from both pneumatics)
            set_intake_lift(False)
        
        wait(20, MSEC)

# create competition instance
comp = Competition(user_control, autonomous)
pre_autonomous()