import sys
import pygame
import time
from arduino_comms import SerialCommunicator
from arduino_commands import Command

# Initialize Pygame
pygame.init()

# Set up the drawing window
screen = pygame.display.set_mode([100, 100])

# Constants for the motor speed
MOTOR_SPEED = 126

# Initialize SerialCommunicator
serial_comm = SerialCommunicator(115200)
serial_comm.connect_id("1A86", "7523")

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
                serial_comm.send_command(Command.SET_MOTOR_SPEED, MOTOR_SPEED)
            elif event.key == pygame.K_RIGHT:
                # Move motor backward when right key is pressed
                serial_comm.send_command(Command.SET_MOTOR_SPEED, -MOTOR_SPEED)
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                # Stop the motor when either key is released
                serial_comm.send_command(Command.SET_MOTOR_SPEED, 0)

# Done! Time to quit.
pygame.quit()
serial_comm.close()
