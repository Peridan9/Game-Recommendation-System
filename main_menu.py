import pygame
import sys
from managers import LoginManager


def main():
    # Initialize Pygame
    pygame.init()

    # Constants
    WIDTH, HEIGHT = 800, 600
    WHITE = (255, 255, 255)
    GRAY = (200, 200, 200)
    FPS = 60

    # Create the game window
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Login System")

    # MongoDB connection
    dbmanager = LoginManager()

    # Fonts
    font = pygame.font.Font(None, 36)

    # Text input for username and password
    username_rect = pygame.Rect(WIDTH / 2 - 150, 200, 300, 40)
    password_rect = pygame.Rect(WIDTH / 2 - 150, 300, 300, 40)
    username_text = ""
    password_text = ""
    username_active = False
    password_active = False

    # Buttons
    login_button = pygame.Rect(WIDTH / 2 - 140, 400, 120, 50)
    register_button = pygame.Rect(WIDTH / 2 + 25, 400, 120, 50)

    # Game Loop
    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if username_rect.collidepoint(event.pos):
                    username_active = not username_active
                    password_active = False
                elif password_rect.collidepoint(event.pos):
                    password_active = not password_active
                    username_active = False
                else:
                    username_active = False
                    password_active = False
                register_button_clicked = register_button.collidepoint(event.pos)
                login_button_clicked = login_button.collidepoint(event.pos)
                if register_button_clicked:
                    try:
                        dbmanager.register_user(username_text, password_text)
                    except ValueError as e:
                        print(e)
                elif login_button_clicked:
                    try:
                        user = dbmanager.login_user(username_text, password_text)
                        if user:
                            return user
                    except ValueError as e:
                        print(e)

            if event.type == pygame.KEYDOWN:
                if username_active:
                    if event.key == pygame.K_RETURN:
                        username_active = False
                        password_active = True
                    elif event.key == pygame.K_BACKSPACE:
                        username_text = username_text[:-1]
                    else:
                        username_text += event.unicode
                elif password_active:
                    if event.key == pygame.K_RETURN:
                        try:
                            user = dbmanager.login_user(username_text, password_text)
                            if user:
                                return user
                        except ValueError as e:
                            print(e)
                    elif event.key == pygame.K_BACKSPACE:
                        password_text = password_text[:-1]
                    else:
                        password_text += event.unicode

        screen.fill(WHITE)

        # Draw text input and buttons
        pygame.draw.rect(
            screen, GRAY if not username_active else (0, 0, 0), username_rect, 2
        )
        pygame.draw.rect(
            screen, GRAY if not password_active else (0, 0, 0), password_rect, 2
        )
        username_surface = font.render(username_text, True, (0, 0, 0))
        password_surface = font.render(password_text, True, (0, 0, 0))
        screen.blit(username_surface, (username_rect.x + 5, username_rect.y + 5))
        screen.blit(password_surface, (password_rect.x + 5, password_rect.y + 5))

        pygame.draw.rect(screen, (128, 128, 128), register_button)
        pygame.draw.rect(screen, (128, 128, 128), login_button)
        register_text = font.render("Register", True, (0, 0, 0))
        login_text = font.render("Login", True, (0, 0, 0))
        screen.blit(register_text, (register_button.x + 10, register_button.y + 10))
        screen.blit(login_text, (login_button.x + 20, login_button.y + 10))

        # Draw title
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("Login System", True, (0, 0, 0))
        screen.blit(title_text, (WIDTH / 2 - title_text.get_width() / 2, 50))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
