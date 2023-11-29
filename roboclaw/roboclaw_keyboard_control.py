import sys
import pygame
import time

sys.path.append('/Users/henrywu/Desktop/capstone/roboclaw/lib/python3.7/site-packages/roboclaw_python')

from roboclaw_3 import Roboclaw

dir(Roboclaw)

# Initialize Roboclaw
roboclaw = Roboclaw('/dev/tty.usbmodem2101', 38400)

roboclaw.Open()

# Constants for the motor speed
MOTOR_SPEED = 126
MOTOR_ADDRESS = 0x80

# Initialize Pygame
pygame.init()

# Set up the drawing window
screen = pygame.display.set_mode([100, 100])

# Main loop
running = True
while running:
    # Check all the events in the event queue
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                # Move motor forward when left key is pressed
                roboclaw.ForwardM1(MOTOR_ADDRESS, MOTOR_SPEED)
            elif event.key == pygame.K_RIGHT:
                # Move motor backward when right key is pressed
                roboclaw.BackwardM1(MOTOR_ADDRESS, MOTOR_SPEED)
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                # Stop the motor when either key is released
                roboclaw.ForwardM1(MOTOR_ADDRESS, 0)
                # You can also use roboclaw.BackwardM1(MOTOR_ADDRESS, 0) if that is appropriate for your motor configuration

# Done! Time to quit.
pygame.quit()
