from vex import *
brain=Brain()
wait(30, MSEC)

controller = Controller()

#Defining each of our motors and corresponding ports
#(Left is reverse and blue motor cartridges mean 6:1 gear ratio)
left_motor_a = Motor(Ports.PORT1, GearSetting.RATIO_6_1, False)
left_motor_b = Motor(Ports.PORT2, GearSetting.RATIO_6_1, False)
left_motor_c = Motor(Ports.PORT11, GearSetting.RATIO_6_1, False)
right_motor_a = Motor(Ports.PORT6, GearSetting.RATIO_6_1, True)
right_motor_b = Motor(Ports.PORT7, GearSetting.RATIO_6_1, True)
right_motor_c = Motor(Ports.PORT8, GearSetting.RATIO_6_1, True)

#Make each side its own group 
left_drive = MotorGroup(left_motor_a, left_motor_b, left_motor_c)
right_drive = MotorGroup(right_motor_a, right_motor_b, right_motor_c)

#Defining our intake motor (instead of using the built in device function of VexCode)
intake_motor = Motor(Ports.PORT12, GearSetting.RATIO_18_1, False)

# Defining our pnuematics on each side of the intake
intake_lift_1 = DigitalOut(brain.three_wire_port.a)
intake_lift_2 = DigitalOut(brain.three_wire_port.b)

#Defining the drivetrain specs (in mm)
wheel_travel = 239.4
track_width = 317.5
wheel_base = 301.6
external_ratio = 0.6  #(We have a 3:5 gear ratio so you divide 3 and 5)

#Make the drivetrain!
drivetrain = DriveTrain(left_drive, right_drive, wheel_travel, track_width, wheel_base, MM, external_ratio)

#Driver asked for lower turning speed
drivetrain.set_turn_velocity(50, PERCENT)

#Deadband makes the controller less "fidgety"
DEADBAND = 5
#Make the intake speed as fast as possible (we think 300% makes it go fast)
INTAKE_SPEED = 300  
#Driver also asked for a slower turning speed
TURN_SPEED_LIMIT = 50 

#Fixing some of our controller issues:
def clamp(val, low=-100, high=100):
   
    if val > high:
        return high
    if val < low:
        return low
    return val

def apply_deadband(value, threshold=DEADBAND):
    
    return 0 if abs(value) < threshold else value
#Make sure both pnuematics pistons go up at the same time
def set_intake_lift(up):
   
    intake_lift_1.set(up)
    intake_lift_2.set(up)

def pre_autonomous():
    #Make sure everything is reset and ready to go
    left_motor_a.reset_position()
    right_motor_a.reset_position()
    intake_motor.reset_position()
    
    #Make sure intake is down when we start
    set_intake_lift(False)
    
    wait(100, MSEC)

def autonomous():
    #We needed a slower auton speed for better control
    drivetrain.set_drive_velocity(25, PERCENT)
    
    #Auton Program:
    drivetrain.drive_for(REVERSE, 36, INCHES, wait=True)
    wait(1, SECONDS)

    intake_motor.spin(FORWARD, INTAKE_SPEED, PERCENT)

    wait(2, SECONDS)

    intake_motor.stop()
    
    wait(3, SECONDS)
    
    drivetrain.turn_for(RIGHT, 20, DEGREES, wait=True)

    drivetrain.drive_for(REVERSE, 12, INCHES, wait=True)

    intake_motor.spin(REVERSE, INTAKE_SPEED, PERCENT)
    wait(3, SECONDS)
    intake_motor.stop()

def user_control():
    #Drive Code:
    while True:
        #Making the controller work with our 6 motor drive:
        forward = apply_deadband(controller.axis3.position())
        turn = apply_deadband(controller.axis1.position())
        
        #Driver asked for a slower turning speed
        turn = turn * (TURN_SPEED_LIMIT / 100.0)
        
        #Had to reverse the joystick calculations because turning was reversed
        left_power = clamp(-forward - turn)
        right_power = clamp(-forward + turn)
        
        left_drive.spin(FORWARD, left_power, PERCENT)
        right_drive.spin(FORWARD, right_power, PERCENT)
        
       #Putting the intake controlls on the right paddles
        if controller.buttonR1.pressing():
            intake_motor.spin(FORWARD, INTAKE_SPEED, PERCENT)
        elif controller.buttonR2.pressing():
            intake_motor.spin(REVERSE, INTAKE_SPEED, PERCENT)
        else:
            intake_motor.stop()
        
       #Putting the pneumatics contrlls on the left paddles
        if controller.buttonL1.pressing():
            set_intake_lift(True)
        elif controller.buttonL2.pressing():
            set_intake_lift(False)
        wait(20, MSEC)

comp = Competition(user_control, autonomous)
pre_autonomous()