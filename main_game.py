import pygame
import sys
import time
from managers import DBManager


class NPCManager:
    def __init__(self, screen, user):
        self.dbmanager = DBManager()
        self.screen = screen
        self.user = user

    def npc_name(self, npc_id) -> str:
        if npc_id == 0:
            return "Load CSV"
        elif npc_id == 1:
            return "Recommend games by name"
        elif npc_id == 2:
            return "Recommend games by genre"
        elif npc_id == 3:
            return "Rent game"
        elif npc_id == 4:
            return "Return game"

    def npc_loop(self, npc_id) -> None:
        if npc_id == 0:
            self.dbmanager.load_csv()
            self.display(self.screen, "Loaded CSV")
        elif npc_id == 1:
            # favorite_game = self.get_input(self.screen, "Enter favorite game name:")
            result = self.dbmanager.recommend_games_by_name(self.user)
            self.display(self.screen, result)
        elif npc_id == 2:
            # favorite_genre = self.get_input(self.screen, "Enter favorite genre:")
            result = self.dbmanager.recommend_games_by_genre(self.user)
            self.display(self.screen, result)
        elif npc_id == 3:
            game_title = self.get_input(self.screen, "Enter game title:")
            result = self.dbmanager.rent_game(self.user, game_title)
            self.display(self.screen, result)
        elif npc_id == 4:
            game_title = self.get_input(self.screen, "Enter game title:")
            result = self.dbmanager.return_game(self.user, game_title)
            self.display(self.screen, result)

    def get_input(self, screen, prompt) -> str:
        pygame.font.init()
        font = pygame.font.SysFont(None, 24)
        input_box = pygame.Rect(250, 300, 100, 32)
        color_inactive = pygame.Color("lightskyblue3")
        color_active = pygame.Color("dodgerblue2")
        color = color_inactive
        active = False
        text = ""
        done = False

        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if input_box.collidepoint(event.pos):
                        active = not active
                    else:
                        active = False
                    color = color_active if active else color_inactive
                if event.type == pygame.KEYDOWN:
                    if active:
                        if event.key == pygame.K_RETURN:
                            done = True
                        elif event.key == pygame.K_BACKSPACE:
                            text = text[:-1]
                        else:
                            text += event.unicode
            screen.fill((200, 200, 200))
            txt_surface = font.render(text, True, color)
            input_box.w = 350
            screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
            pygame.draw.rect(screen, color, input_box, 2)

            # Draw title
            title_font = pygame.font.Font(None, 48)
            title_text = title_font.render(prompt, True, (0, 0, 0))
            screen.blit(title_text, (400 - title_text.get_width() / 2, 200))

            pygame.display.flip()
        return text

    def display(self, screen, text) -> None:
        pygame.font.init()
        screen.fill((255, 255, 255))
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render(text, True, (0, 0, 0))
        screen.blit(title_text, (0, 200))

        running = True
        while running:
            for event in pygame.event.get():
                if event.type in [pygame.QUIT, pygame.KEYDOWN]:
                    running = False
            pygame.display.flip()


def main(user):
    pygame.init()

    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Simple Pygame")

    white = (255, 255, 255)
    black = (0, 0, 0)

    player_size = 38
    player_x, player_y = width // 2 - player_size // 2, height // 2 - player_size // 2
    player_speed = 10

    npc_positions = [(90, 160), (270, 320), (600, 420), (130, 420), (610, 220)]
    npc_sprite = pygame.image.load("etc\Sprite0.png")
    player_sprite = pygame.image.load("etc\Sprite1.png")
    background = pygame.image.load("etc\Background.png")
    npc_size = 36

    npc_manager = NPCManager(screen, user)

    font = pygame.font.Font(None, 36)
    dialog_box = pygame.Rect(50, height - 100, width - 100, 50)

    running = True
    interacting = False
    current_npc = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and interacting:
                    npc_manager.npc_loop(current_npc)
                    interacting = False

        keys = pygame.key.get_pressed()
        new_x, new_y = player_x, player_y

        if keys[pygame.K_w] and player_y > 0:
            new_y -= player_speed
        if keys[pygame.K_s] and player_y < height:
            new_y += player_speed
        if keys[pygame.K_a] and player_x > 0:
            new_x -= player_speed
        if keys[pygame.K_d] and player_x < width:
            new_x += player_speed

        player_rect = pygame.Rect(new_x, new_y, player_size, player_size)

        can_move = True
        interacting = False
        for i, npc_pos in enumerate(npc_positions):
            npc_rect = pygame.Rect(npc_pos[0], npc_pos[1], npc_size, npc_size)
            if npc_rect.colliderect(player_rect):
                can_move = False
                interacting = True
                current_npc = i

        if can_move:
            player_x, player_y = new_x, new_y

        screen.blit(background, (0, 0))
        screen.blit(player_sprite, (player_x - 13.5, player_y - 13.5))

        for i, npc_pos in enumerate(npc_positions):

            # Blit NPC image at adjusted position
            npc_pos = (npc_pos[0] - 18, npc_pos[1] - 18)
            screen.blit(npc_sprite, npc_pos)

            npc_function_name = font.render(npc_manager.npc_name(i), True, black)
            screen.blit(
                npc_function_name,
                (
                    npc_pos[0]
                    + npc_size // 2
                    - npc_function_name.get_width() // 2
                    + 15,
                    npc_pos[1] + npc_size + 25,
                ),
            )

        if interacting:
            pygame.draw.rect(screen, white, dialog_box)
            text = font.render("Press Enter to interact", True, black)
            screen.blit(text, (width // 2 - text.get_width() // 2, height - 80))

        pygame.display.flip()

        pygame.time.Clock().tick(30)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main(None)
