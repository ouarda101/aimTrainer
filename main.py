import math
import random
import time

import pygame


pygame.init()


WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Aim Trainer")


PASTEL_PINK = (255, 200, 220)
PASTEL_BLUE = (180, 220, 255)
PASTEL_YELLOW = (255, 255, 180)
PASTEL_GREEN = (200, 255, 200)
COZY_BROWN = (160, 82, 45)
DARK_COZY_GRAY = (80, 80, 80)
WHITE = (255, 255, 255)
ACCENT_RED = (255, 120, 120)

BACKGROUND_COLOR = PASTEL_YELLOW


target_increment = 750
target_event = pygame.USEREVENT + 1
target_padding = 30


GAME_DURATION = 30
FPS = 60


FONT = pygame.font.SysFont("gabriola", 35)
LARGE_FONT = pygame.font.SysFont("gabriola", 60)
SMALL_FONT = pygame.font.SysFont("gabriola", 25)


pygame.mouse.set_visible(False)
CURSOR_COLOR = COZY_BROWN
CURSOR_OUTLINE_COLOR = DARK_COZY_GRAY
CURSOR_SIZE = 10
CURSOR_OUTLINE_THICKNESS = 2


HIT_EFFECTS = []
SPARKLE_LIFESPAN = 0.4
SPARKLE_RADIUS_START = 5
SPARKLE_RADIUS_END = 20
SPARKLE_COLOR = WHITE


game_state = "START"
score = 0
targets = []
start_time = 0
misses = 0


class Target:
    MAX_SIZE = 30
    GROWTH_RATE = 0.3
    COLOR = PASTEL_PINK
    SECONDARY_COLOR = PASTEL_BLUE

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 0
        self.grow = True
        self.spawn_time = time.time()

    def update(self):
        if self.grow:
            self.size += self.GROWTH_RATE
            if self.size >= self.MAX_SIZE:
                self.grow = False
        else:
            self.size -= self.GROWTH_RATE
            self.size = max(0, self.size)

    def draw(self, win):
        pygame.draw.circle(win, ACCENT_RED, (self.x, self.y), self.MAX_SIZE, 2)
        pygame.draw.circle(win, self.COLOR, (self.x, self.y), self.size)
        pygame.draw.circle(win, self.SECONDARY_COLOR, (self.x, self.y), self.size * 0.7)
        pygame.draw.circle(win, self.COLOR, (self.x, self.y), self.size * 0.4)

    def collide(self, x, y):
        dis = math.hypot(self.x - x, self.y - y)
        return dis <= self.size



def draw_text(text, font, color, x, y, align="center"):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if align == "center":
        text_rect.center = (x, y)
    elif align == "topleft":
        text_rect.topleft = (x, y)
    elif align == "topright":
        text_rect.topright = (x, y)
    WIN.blit(text_surface, text_rect)

def draw_custom_cursor():
    mouse_x, mouse_y = pygame.mouse.get_pos()
    pygame.draw.circle(WIN, CURSOR_OUTLINE_COLOR, (mouse_x, mouse_y), CURSOR_SIZE + CURSOR_OUTLINE_THICKNESS, CURSOR_OUTLINE_THICKNESS)
    pygame.draw.circle(WIN, CURSOR_COLOR, (mouse_x, mouse_y), CURSOR_SIZE)
    line_length = CURSOR_SIZE + 5
    pygame.draw.line(WIN, CURSOR_OUTLINE_COLOR, (mouse_x - line_length, mouse_y), (mouse_x - CURSOR_SIZE, mouse_y), 2)
    pygame.draw.line(WIN, CURSOR_OUTLINE_COLOR, (mouse_x + CURSOR_SIZE, mouse_y), (mouse_x + line_length, mouse_y), 2)
    pygame.draw.line(WIN, CURSOR_OUTLINE_COLOR, (mouse_x, mouse_y - line_length), (mouse_x, mouse_y - CURSOR_SIZE), 2)
    pygame.draw.line(WIN, CURSOR_OUTLINE_COLOR, (mouse_x, mouse_y + CURSOR_SIZE), (mouse_x, mouse_y + line_length), 2)

def draw_hit_effect(effect):
    current_time = time.time()
    elapsed = current_time - effect["start_time"]
    if elapsed < SPARKLE_LIFESPAN:
        alpha = max(0, 255 - int((elapsed / SPARKLE_LIFESPAN) * 255))
        radius = SPARKLE_RADIUS_START + (SPARKLE_RADIUS_END - SPARKLE_RADIUS_START) * (elapsed / SPARKLE_LIFESPAN)
        s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (SPARKLE_COLOR[0], SPARKLE_COLOR[1], SPARKLE_COLOR[2], alpha), (radius, radius), radius)
        WIN.blit(s, (effect["pos"][0] - radius, effect["pos"][1] - radius))
        return True
    return False


def main():
    
    global game_state, score, misses, targets, start_time, HIT_EFFECTS

    run = True
    clock = pygame.time.Clock()

    
    def reset_game():
        
        global score, misses, targets, start_time, HIT_EFFECTS, game_state
        score = 0
        misses = 0
        targets = []
        HIT_EFFECTS = []
        start_time = time.time()
        
        x = random.randint(target_padding, WIDTH - target_padding)
        y = random.randint(target_padding, HEIGHT - target_padding)
        targets.append(Target(x, y))
        pygame.time.set_timer(target_event, target_increment) # Restart target spawning timer

    
    reset_game() 
    game_state = "START" 

    while run:
        clock.tick(FPS)
        current_time = time.time()
        mouse_pos = pygame.mouse.get_pos()

        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_state == "START":
                    game_state = "PLAYING"
                    reset_game()
                elif game_state == "GAME_OVER":
                    game_state = "PLAYING"
                    reset_game()
                elif game_state == "PLAYING":
                    hit_a_target = False
                    for target in targets[:]:
                        if target.collide(*mouse_pos):
                            score += 1
                            targets.remove(target)
                            HIT_EFFECTS.append({"pos": mouse_pos, "start_time": current_time})
                            hit_a_target = True
                            break

                    if not hit_a_target:
                        misses += 1

            if event.type == target_event and game_state == "PLAYING":
                x = random.randint(target_padding, WIDTH - target_padding)
                y = random.randint(target_padding, HEIGHT - target_padding)
                targets.append(Target(x, y))

       
        if game_state == "PLAYING":
            elapsed_time = current_time - start_time
            remaining_time = max(0, GAME_DURATION - elapsed_time)

            targets_to_remove = []
            for target in targets:
                target.update()
                if target.size <= 0:
                    targets_to_remove.append(target)
                    misses += 1

            for target in targets_to_remove:
                targets.remove(target)

            HIT_EFFECTS = [effect for effect in HIT_EFFECTS if draw_hit_effect(effect)]

            if remaining_time <= 0:
                game_state = "GAME_OVER"
                pygame.time.set_timer(target_event, 0)
                targets = []

        
        WIN.fill(BACKGROUND_COLOR)

        if game_state == "START":
            draw_text("Aim Trainer", LARGE_FONT, DARK_COZY_GRAY, WIDTH // 2, HEIGHT // 2 - 80)
            draw_text("Click to Start", FONT, COZY_BROWN, WIDTH // 2, HEIGHT // 2 + 20)
            draw_text("Try not to miss !", SMALL_FONT, DARK_COZY_GRAY, WIDTH // 2, HEIGHT // 2 + 70)
        elif game_state == "PLAYING":
            for target in targets:
                target.draw(WIN)

            for effect in HIT_EFFECTS:
                draw_hit_effect(effect)

            draw_text(f"Berries Picked: {score}", FONT, DARK_COZY_GRAY, WIDTH - 50, 30, align="topright")
            draw_text(f"Time Left: {int(remaining_time)}s", FONT, DARK_COZY_GRAY, 50, 30, align="topleft")

        elif game_state == "GAME_OVER":
            draw_text("Time's Up! Game Over!", LARGE_FONT, DARK_COZY_GRAY, WIDTH // 2, HEIGHT // 2 - 80)
            draw_text(f"Total Berries Picked: {score}", FONT, COZY_BROWN, WIDTH // 2, HEIGHT // 2 - 20)
            draw_text(f"Total Misses: {misses}", FONT, COZY_BROWN, WIDTH // 2, HEIGHT // 2 + 20)
            draw_text("Click to Play Again!", FONT, DARK_COZY_GRAY, WIDTH // 2, HEIGHT // 2 + 80)

        draw_custom_cursor()
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()