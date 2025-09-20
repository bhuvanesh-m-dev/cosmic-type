import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cosmic Type")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Fonts
FONT = pygame.font.Font(None, 36)
COMET_FONT = pygame.font.Font(None, 48)

# Game variables
word_list = ["python", "pygame", "space", "comet", "typing", "skill", "cosmic", "galaxy", "star", "planet"]
comets = []
bullets = [] # New: List to store active bullets
score = 0
game_over = False
current_word = ""
active_comet = None # New: The comet the user is currently typing
level = 1
comet_speed_multiplier = 1.0

# Gun variables
GUN_WIDTH = 60
GUN_HEIGHT = 20
GUN_COLOR = BLUE
gun_rect = pygame.Rect((SCREEN_WIDTH - GUN_WIDTH) // 2, SCREEN_HEIGHT - GUN_HEIGHT - 10, GUN_WIDTH, GUN_HEIGHT)

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, start_pos, target_pos, color=RED):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=start_pos)
        self.target_pos = target_pos
        self.speed = 20
        # Calculate direction vector
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        distance = (dx**2 + dy**2)**0.5
        if distance == 0:
            self.velocity = [0, 0]
        else:
            self.velocity = [dx / distance * self.speed, dy / distance * self.speed]

    def update(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # Remove bullet if it passes the target
        if (self.velocity[1] < 0 and self.rect.y <= self.target_pos[1]) or \
           (self.velocity[1] > 0 and self.rect.y >= self.target_pos[1]):
            self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# Comet class
class Comet(pygame.sprite.Sprite):
    def __init__(self, word):
        super().__init__()
        self.original_word = word
        self.typed_letters = [False] * len(word) # Track typed letters
        self.font_surface = COMET_FONT.render(word, True, WHITE)
        self.image = pygame.Surface((self.font_surface.get_width() + 20, self.font_surface.get_height() + 10), pygame.SRCALPHA)
        self.image.blit(self.font_surface, (10, 5))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = -self.rect.height
        self.speed = random.randint(level * 1, level * 2) * comet_speed_multiplier

    def update(self):
        self.rect.y += self.speed
        if self.rect.y > SCREEN_HEIGHT:
            self.kill() # Remove comet if it goes off screen

    def draw(self, surface):
        # Draw the comet background
        surface.blit(self.image, self.rect)
        # Draw letters, changing color for typed ones
        x_offset = 10 # Matches blit offset
        for i, char in enumerate(self.original_word):
            color = GREEN if self.typed_letters[i] else WHITE
            char_surface = COMET_FONT.render(char, True, color)
            surface.blit(char_surface, (self.rect.x + x_offset, self.rect.y + 5))
            x_offset += char_surface.get_width()

    def get_next_untyped_char(self):
        for i, typed in enumerate(self.typed_letters):
            if not typed:
                return self.original_word[i], i
        return None, -1

    def mark_letter_typed(self, index):
        if 0 <= index < len(self.typed_letters):
            self.typed_letters[index] = True

    def is_fully_typed(self):
        return all(self.typed_letters)

    def get_letter_position(self, index):
        # Calculate the position of a specific letter on the comet
        x_offset = 10 # Initial offset
        for i, char in enumerate(self.original_word):
            char_surface = COMET_FONT.render(char, True, WHITE)
            if i == index:
                return (self.rect.x + x_offset + char_surface.get_width() // 2,
                        self.rect.y + 5 + char_surface.get_height() // 2)
            x_offset += char_surface.get_width()
        return self.rect.center # Fallback if index is out of bounds

# Game functions
def spawn_comet():
    word = random.choice(word_list)
    comets.append(Comet(word))

def check_typing(event):
    global current_word, score, game_over, level, comet_speed_multiplier, active_comet

    if event.key == pygame.K_BACKSPACE:
        current_word = current_word[:-1]
    elif event.unicode.isalpha():
        current_word += event.unicode.lower()

        # Find the active comet if not already set
        if active_comet is None:
            for comet in comets:
                if not comet.is_fully_typed():
                    active_comet = comet
                    break
        
        if active_comet:
            next_char, char_index = active_comet.get_next_untyped_char()
            if next_char and current_word[-1] == next_char:
                active_comet.mark_letter_typed(char_index)
                score += 1 # Award point for each correct letter
                
                # Create a bullet
                bullet_start = gun_rect.center
                bullet_target = active_comet.get_letter_position(char_index)
                bullets.append(Bullet(bullet_start, bullet_target))

                if active_comet.is_fully_typed():
                    score += len(active_comet.original_word) * level # Bonus for completing word
                    comets.remove(active_comet)
                    active_comet = None
                    current_word = "" # Reset current word after completing a comet
            else:
                # Incorrect letter typed, reset current_word and active_comet
                current_word = ""
                active_comet = None
                score -= 2 # Penalize for incorrect typing attempt
    
    # If the user types a full word that doesn't match the active comet, clear it
    if active_comet and current_word and not active_comet.original_word.startswith(current_word):
        current_word = ""
        active_comet = None

# Game loop
running = True
clock = pygame.time.Clock()

COMET_SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(COMET_SPAWN_EVENT, 2000) # Spawn a comet every 2 seconds

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if not game_over:
                check_typing(event)
        elif event.type == COMET_SPAWN_EVENT:
            if not game_over:
                spawn_comet()

    if not game_over:
        SCREEN.fill(BLACK) # Background

        # Draw gun
        pygame.draw.rect(SCREEN, GUN_COLOR, gun_rect)

        # Update and draw comets
        for comet in comets:
            comet.update()
            comet.draw(SCREEN)
            if comet.rect.y >= SCREEN_HEIGHT - comet.rect.height: # Comet hit the ground
                game_over = True

        # Update and draw bullets
        for bullet in bullets:
            bullet.update()
            bullet.draw(SCREEN)
            if not bullet.alive(): # Remove bullet if it has reached its target
                bullets.remove(bullet)

        # Draw score and current word
        draw_text(SCREEN, f"Score: {score}", FONT, WHITE, 10, 10)
        draw_text(SCREEN, f"Level: {level}", FONT, WHITE, 10, 50)
        
        display_word = current_word
        if active_comet:
            display_word = active_comet.original_word[:len(current_word)] + "_" * (len(active_comet.original_word) - len(current_word))

        draw_text(SCREEN, f"Type: {display_word}", FONT, GREEN, 10, SCREEN_HEIGHT - 40)

        # Level progression (example: every 100 points)
        if score >= level * 100:
            level += 1
            comet_speed_multiplier += 0.2 # Increase speed
            pygame.time.set_timer(COMET_SPAWN_EVENT, max(500, 2000 - (level * 100))) # Increase spawn rate

    else:
        SCREEN.fill(BLACK)
        draw_text(SCREEN, "GAME OVER", FONT, RED, SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 50)
        draw_text(SCREEN, f"Final Score: {score}", FONT, WHITE, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2)
        draw_text(SCREEN, "Press R to Restart", FONT, WHITE, SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 50)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            # Reset game
            comets = []
            bullets = [] # New: Reset bullets
            score = 0
            game_over = False
            current_word = ""
            active_comet = None # New: Reset active comet
            level = 1
            comet_speed_multiplier = 1.0
            pygame.time.set_timer(COMET_SPAWN_EVENT, 2000)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
