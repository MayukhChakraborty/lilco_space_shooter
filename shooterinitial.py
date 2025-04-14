## Creating a game directly

import serial
import pygame
import random
import sys
from pygame.locals import *

# Initialise pygame
pygame.init()


# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
LIGHT_GREY = (200, 200, 200)
MEDIUM_GREY = (150, 150, 150)
DARK_GREY = (100, 100, 100)



# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Lilco Space Shooter')


# Clock for controlling game speed
clock = pygame.time.Clock()
FPS = 40


# Try to initialize the serial connection (adjust port as needed)
try:
    # Change '/dev/ttyACM0' to your Arduino's serial port (Windows might use COM3, etc.)
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=0.1)
    print("Serial connection established")
except:
    print("Failed to connect to Arduino. Running in keyboard mode.")
    ser = None


# Game classes
class Player(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        # Create a simple triangle for the player ship
        self.image = pygame.Surface((30, 40), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, WHITE, [(15, 0), (0, 40), (30, 40)])
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT-50))
        self.speed = 5
        self.cooldown = 0
        self.big_cooldown = 0

    
    def update(self, x_value=None, y_value=None):
        # Handle movement with controller values
        if x_value is not None and y_value is not None:
            # Horizontal movement
            if x_value > 520:  # Right
                self.rect.x += self.speed
            elif x_value < 490:  # Left
                self.rect.x -= self.speed
            
            # Vertical movement
            if y_value > 520:  # Up (since joystick Y is inverted)
                self.rect.y -= self.speed
            elif y_value < 490:  # Down
                self.rect.y += self.speed
        
        # Alternative keyboard controls
        keys = pygame.key.get_pressed()
        if keys[K_LEFT]:
            self.rect.x -= self.speed
        if keys[K_RIGHT]:
            self.rect.x += self.speed
        if keys[K_UP]:
            self.rect.y -= self.speed
        if keys[K_DOWN]:
            self.rect.y += self.speed
            
        # Keep player on screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            
        # Cooldown timers
        if self.cooldown > 0:
            self.cooldown -= 1
        if self.big_cooldown > 0:
            self.big_cooldown -= 1

    
    def shoot(self, big=False):
        if big and self.big_cooldown == 0:
            self.big_cooldown = 30  # Longer cooldown for big bullets
            return Bullet(self.rect.centerx, self.rect.top, big=True)
        elif not big and self.cooldown == 0:
            self.cooldown = 15
            return Bullet(self.rect.centerx, self.rect.top)
        return None
    

#designing bullets and its controls
class Bullet(pygame.sprite.Sprite):

    def __init__(self, x, y, big=False):
        super().__init__()
        self.big = big
        if big:
            self.image = pygame.Surface((10, 20))
            self.image.fill(RED)
            self.speed = 7
        else:
            self.image = pygame.Surface((5, 10))
            self.image.fill(GREEN)
            self.speed = 10
        self.rect = self.image.get_rect(center=(x, y))

    
    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()


#designing Astroids
class Asteroid(pygame.sprite.Sprite):

    def __init__(self, size=None):
        super().__init__()
        if size is None:
            size = random.choice(['small', 'medium', 'large'])
        
        self.size = size
        
        if size == 'small':
            self.radius = 10
            self.speed = random.uniform(2, 4)
            self.health = 1
            color = LIGHT_GREY               # Light grey
        elif size == 'medium':
            self.radius = 20
            self.speed = random.uniform(1, 3)
            self.health = 2
            color = MEDIUM_GREY            # Medium grey
        else:  # large
            self.radius = 30
            self.speed = random.uniform(0.5, 2)
            self.health = 3
            color = DARK_GREY                # Dark grey
            
        # Create a circular asteroid
        self.image = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (self.radius, self.radius), self.radius)
        
        # Add some crater details
        for _ in range(3):
            crater_pos = (random.randint(5, self.radius*2-5), random.randint(5, self.radius*2-5))
            crater_radius = random.randint(2, 5)
            pygame.draw.circle(self.image, BLACK, crater_pos, crater_radius)
            
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)


    def update(self):
        self.rect.y += self.speed
        
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
    

    def hit(self, damage=1):
        self.health -= damage
        if self.health <= 0:
            # If it's not a small asteroid, spawn smaller ones
            if self.size != 'small':
                return self.break_apart()
            return []
        
        # Change color slightly when hit but not destroyed
        pygame.draw.circle(self.image, (255, 100, 100), (self.radius, self.radius), self.radius)
        return []
    
    def break_apart(self):
        new_asteroids = []
        
        # Determine what size the children should be
        if self.size == 'large':
            child_size = 'medium'
            num_children = 2
        else:  # medium
            child_size = 'small'
            num_children = 2
            
        # Create the child asteroids
        for _ in range(num_children):
            child = Asteroid(child_size)
            child.rect.center = self.rect.center
            # Give the children some velocity in different directions
            child.rect.x += random.randint(-20, 20)
            new_asteroids.append(child)
            
        return new_asteroids
    

class Explosion(pygame.sprite.Sprite):


    def __init__(self, center, size):
        super().__init__()
        self.size = size
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=center)
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50  # How fast the animation plays
        
        # Draw the explosion (a simple expanding circle animation)
        self.max_frame = 5

    
    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == self.max_frame:
                self.kill()
            else:
                radius = int(self.size * (self.frame / self.max_frame) / 2)
                self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
                pygame.draw.circle(self.image, (255, 255, 0), (self.size//2, self.size//2), radius)
                pygame.draw.circle(self.image, (255, 165, 0), (self.size//2, self.size//2), radius-2)
                pygame.draw.circle(self.image, (255, 0, 0), (self.size//2, self.size//2), radius-4)
                self.rect = self.image.get_rect(center=self.rect.center)


class Game:

    def __init__(self):
        self.score = 0
        self.level = 1
        self.game_over = False
        
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        
        # Create player
        self.player = Player()
        self.all_sprites.add(self.player)
        
        # Game variables
        self.asteroid_spawn_timer = 0
        self.x_value = 500  # Default center
        self.y_value = 500  # Default center
        
        # Font for text
        self.font = pygame.font.Font(None, 36)

    
    def process_serial_input(self):
        if ser is None:
            return
            
        if ser.in_waiting > 0:
            try:
                line = ser.readline().decode('utf-8').strip()
                
                # Handle joystick coordinates
                if line.startswith("X:"):
                    self.x_value = int(line.split()[1])
                elif line.startswith("Y:"):
                    self.y_value = int(line.split()[1])
                # Handle button presses
                elif line == "A":
                    self.shoot_bullet()
                elif line == "B":
                    self.shoot_bullet(big=True)
                elif line == "E" and self.game_over:
                    self.__init__()  # Reset the game
                # You can add more button handlers (C, D, E, F) here
            except Exception as e:
                print(f"Serial reading error: {e}")

    
    def process_events(self):
        # Process all pygame events
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return False
                elif event.key == K_SPACE:
                    self.shoot_bullet()
                elif event.key == K_b:
                    self.shoot_bullet(big=True)
                elif event.key == K_r and self.game_over:
                    self.__init__()  # Reset the game
        return True
    

    def shoot_bullet(self, big=False):
        bullet = self.player.shoot(big)
        if bullet:
            self.bullets.add(bullet)
            self.all_sprites.add(bullet)

    def spawn_asteroid(self):
        asteroid = Asteroid()
        self.asteroids.add(asteroid)
        self.all_sprites.add(asteroid)

    def update(self):
        if self.game_over:
            return
            
        # Process serial input from Arduino
        self.process_serial_input()
        
        # Update all game objects
        self.player.update(self.x_value, self.y_value)
        self.bullets.update()
        self.asteroids.update()
        self.all_sprites.update()
        
        # Check for collisions
        self.check_collisions()
        
        # Spawn new asteroids
        self.asteroid_spawn_timer += 1
        if self.asteroid_spawn_timer >= 60 // self.level:
            self.spawn_asteroid()
            self.asteroid_spawn_timer = 0

    def check_collisions(self):
        # Check if bullets hit asteroids
        for bullet in self.bullets:
            hits = pygame.sprite.spritecollide(bullet, self.asteroids, False)
            for asteroid in hits:
                # Bigger bullets do more damage
                damage = 2 if bullet.big else 1
                
                # Get any resulting smaller asteroids
                new_asteroids = asteroid.hit(damage)
                
                # Add points based on asteroid size
                if asteroid.health <= 0:
                    if asteroid.size == 'large':
                        self.score += 20
                    elif asteroid.size == 'medium':
                        self.score += 10
                    else:  # small
                        self.score += 5
                        
                    # Create explosion
                    explosion = Explosion(asteroid.rect.center, asteroid.radius * 3)
                    self.all_sprites.add(explosion)
                    
                    # Remove the destroyed asteroid
                    asteroid.kill()
                    
                    # Add any new smaller asteroids that were created
                    for new_asteroid in new_asteroids:
                        self.asteroids.add(new_asteroid)
                        self.all_sprites.add(new_asteroid)
                
                # Remove the bullet, unless it's a big bullet which can penetrate small asteroids
                if not (bullet.big and asteroid.size == 'small'):
                    bullet.kill()
                    break
        
        # Check if player collides with asteroids
        if pygame.sprite.spritecollide(self.player, self.asteroids, True):
            explosion = Explosion(self.player.rect.center, 100)
            self.all_sprites.add(explosion)
            self.player.kill()
            self.game_over = True

        
    def draw(self):
        # Draw the background
        screen.fill(BLACK)
        
        # Draw some stars in the background
        ##for i in range(100):
        ##   x = random.randint(0, SCREEN_WIDTH)
        ##  y = (random.randint(0, SCREEN_HEIGHT) + pygame.time.get_ticks() // 50) % SCREEN_HEIGHT
        ##  size = random.randint(1, 3)
        ##  pygame.draw.circle(screen, WHITE, (x, y), size)
        
        # Draw all sprites
        self.all_sprites.draw(screen)
        
        # Draw the score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        # Draw level indicator
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        screen.blit(level_text, (10, 50))
        
        # Show game over text
        if self.game_over:
            game_over_text = self.font.render("GAME OVER - Press R (or K on the Gamepad) to Restart", True, RED)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(game_over_text, text_rect)
        
        # Update the display
        pygame.display.flip()


    def increase_level(self):
        # Every 100 points, increase the level (making the game harder)
        new_level = self.score // 100 + 1
        if new_level > self.level:
            self.level = new_level


# Main game loop
def main():
    game = Game()
    running = True

    while running:
        # Process events
        running = game.process_events()
        
        # Update the game
        game.update()
        
        # Increase level based on score
        game.increase_level()
        
        # Draw everything
        game.draw()
        
        # Control the game speed
        clock.tick(FPS)

    # Clean up
    if ser:
        ser.close()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()