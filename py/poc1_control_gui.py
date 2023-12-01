import pygame
import pygame_gui
import pygame
import pygame_gui

def main():
    try:
        # Pygame setup
        pygame.init()
        pygame.display.set_caption('PID Controller')
        window_surface = pygame.display.set_mode((500, 400))  # Adjust window size

        # GUI Manager
        manager = pygame_gui.UIManager((500, 400))  # Adjust manager size

        # PID Input fields
        label_p = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((10, 50), (80, 30)), text='P:', manager=manager)
        input_p = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((100, 50), (100, 30)), manager=manager)  # Adjust input field size
        input_p.set_text('400')  # Set default value for P

        label_i = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((10, 100), (80, 30)), text='I:', manager=manager)
        input_i = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((100, 100), (100, 30)), manager=manager)  # Adjust input field size
        input_i.set_text('4')  # Set default value for I

        label_d = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((10, 150), (80, 30)), text='D:', manager=manager)
        input_d = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((100, 150), (100, 30)), manager=manager)  # Adjust input field size
        input_d.set_text('0')  # Set default value for D

        label_setpoint = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((10, 200), (80, 30)), text='Setpoint:', manager=manager)
        input_setpoint = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((100, 200), (100, 30)), manager=manager)  # Adjust input field size
        input_setpoint.set_text('5')  # Set default value for Setpoint

        # Motor Control section
        label_speed = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((300, 50), (120, 30)), text='Movement Speed:', manager=manager)  # Adjust label position
        input_speed = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((430, 50), (60, 30)), manager=manager)  # Adjust input field position
        input_speed.set_text('100')  # Set default value for Movement Speed

        button_up = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((430, 100), (60, 30)), text='Up', manager=manager)  # Adjust button position
        button_down = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((430, 140), (60, 30)), text='Down', manager=manager)  # Adjust button position

        label_instructions = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((300, 200), (180, 30)), text='Use arrow keys to move', manager=manager)  # Adjust label position

        # Run Button
        button_run = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 250), (100, 50)), text='Run', manager=manager)
        # Clock
        clock = pygame.time.Clock()
        is_running = True

        while is_running:
            time_delta = clock.tick(60)/1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    is_running = False

                # Handle Pygame GUI events
                manager.process_events(event)

                # Handle button click
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == button_run:
                        p_value = input_p.get_text()
                        i_value = input_i.get_text()
                        d_value = input_d.get_text()
                        print(f"Run with PID: P={p_value}, I={i_value}, D={d_value}")
                    elif event.ui_element == button_up:
                        print("Button Up clicked")
                        # Add your code for button up functionality here
                    elif event.ui_element == button_down:
                        print("Button Down clicked")
                        # Add your code for button down functionality here

            # Update GUI
            manager.update(time_delta)

            # Render everything
            window_surface.fill((66, 66, 66))  # Set background color
            manager.draw_ui(window_surface)
            pygame.display.update()

        pygame.quit()

    except Exception as e:
        print(f"An error occurred: {e}")
        pygame.quit()

if __name__ == "__main__":
    main()
