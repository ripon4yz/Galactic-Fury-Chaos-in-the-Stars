import pygame
import random

pygame.init()

# Screen dimensions
WIDTH = 800
HEIGHT = 600

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Initialize screen
display = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galactic Fury: Chaos in the Stars")

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont("bahnschrift", 30)

# Spaceship properties
ship_width = 50
ship_height = 50
ship_speed = 6

# Bullet properties
bullet_width = 5
bullet_height = 10
bullet_speed = -10

# Enemy properties
enemy_width = 40
enemy_height = 40
enemy_speed = 2

# Asteroid properties
asteroid_size = 30
asteroid_speed = 2  # Slowed down from 4 to 2

# Background setup
background_stars = [
    (random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 3)) for _ in range(100)
]
background_asteroids = [
    pygame.Rect(random.randint(0, WIDTH), random.randint(-600, 0), 40, 40) for _ in range(3)  # Reduced to 3
]
background_asteroid_speed = 1

# Boss properties
boss_width = 80
boss_height = 80
boss_speed = 1
boss_spawn_timer = 0
boss_spawn_interval = 500  # Spawn a boss every 500 frames
boss_active = False
boss_health = 10

# --- Particle System ---
class Particle:
    def __init__(self, x, y, color, size, life):
        self.x = x  # Position of the particle
        self.y = y
        self.color = color  # Color of the particle (for explosion, usually bright colors)
        self.size = size  # Initial size of the particle
        self.life = life  # How long the particle lasts before disappearing
        self.speed_x = random.uniform(-1, 1)  # Random horizontal speed
        self.speed_y = random.uniform(-1, 1)  # Random vertical speed

    def update(self):
        """Update the particle's position and size"""
        self.x += self.speed_x  # Move in x direction
        self.y += self.speed_y  # Move in y direction
        self.size *= 0.95  # Shrink the particle slightly each frame
        self.life -= 1  # Decrease the life

    def draw(self):
        """Draw the particle on the screen"""
        pygame.draw.circle(display, self.color, (int(self.x), int(self.y)), int(self.size))


# Initialize player
def create_player():
    return pygame.Rect(WIDTH // 2 - ship_width // 2, HEIGHT - ship_height - 20, ship_width, ship_height)

# Draw text
def draw_text(text, color, x, y, font_size=30):
    font = pygame.font.SysFont("bahnschrift", font_size)
    message = font.render(text, True, color)
    display.blit(message, (x, y))

# Draw background
def draw_background():
    display.fill(BLACK)
    # Draw stars
    for star in background_stars:
        pygame.draw.circle(display, WHITE, (star[0], star[1]), star[2])
    # Draw moving background asteroids
    for asteroid in background_asteroids:
        pygame.draw.rect(display, YELLOW, asteroid)

# Show start screen
def start_screen():
    display.fill(BLACK)

    # Center the text on the screen
    title_text = "Galactic Fury: Chaos in the Stars"
    dev_text = "This game was Developed by Ripon R. Rahman"
    start_text = "Press any key to start"

    # Adjust for responsive positioning
    title_x = WIDTH // 2 - font.size(title_text)[0] // 2
    title_y = HEIGHT // 2 - 60
    dev_x = WIDTH // 2 - font.size(dev_text)[0] // 2
    dev_y = HEIGHT // 2 + 20
    start_x = WIDTH // 2 - font.size(start_text)[0] // 2
    start_y = HEIGHT // 2 + 60

    # Draw the text
    draw_text(title_text, WHITE, title_x, title_y, font_size=40)
    draw_text(dev_text, WHITE, dev_x, dev_y, font_size=30)
    draw_text(start_text, WHITE, start_x, start_y, font_size=30)

    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                waiting = False

# Weapon class for managing different weapon types
class Weapon:
    def __init__(self, player):
        self.player = player
        self.weapon_type = 1  # 1 is normal, 2 is stronger gun, 3 is wing weapon
        self.bullets = []

    def fire(self):
        if self.weapon_type == 1:  # Normal shot
            self.bullets.append(
                pygame.Rect(self.player.x + ship_width // 2 - bullet_width // 2, self.player.y, bullet_width, bullet_height)
            )
        elif self.weapon_type == 2:  # Stronger shot (spread shot)
            self.bullets.append(pygame.Rect(self.player.x, self.player.y, bullet_width, bullet_height))
            self.bullets.append(pygame.Rect(self.player.x + ship_width // 4, self.player.y, bullet_width, bullet_height))
            self.bullets.append(pygame.Rect(self.player.x + ship_width // 2, self.player.y, bullet_width, bullet_height))
            self.bullets.append(pygame.Rect(self.player.x + ship_width - ship_width // 4, self.player.y, bullet_width, bullet_height))
        elif self.weapon_type == 3:  # Wing weapon (automatic asteroid targeting)
            for i in range(3):
                self.bullets.append(pygame.Rect(self.player.x + i * 20, self.player.y, bullet_width, bullet_height))

    def update(self):
        for bullet in self.bullets[:]:
            bullet.y += bullet_speed
            if bullet.y < 0:
                self.bullets.remove(bullet)

    def draw(self):
        for bullet in self.bullets:
            pygame.draw.rect(display, WHITE, bullet)

# Game loop
def game_loop():
    # Player setup
    player = create_player()

    # Weapon setup
    weapon = Weapon(player)

    # Bullets
    bullets = []

    # Enemies
    enemies = [
        pygame.Rect(random.randint(0, WIDTH - enemy_width), random.randint(-150, -40), enemy_width, enemy_height)
        for _ in range(5)
    ]

    # Asteroids
    asteroids = [
        pygame.Rect(random.randint(0, WIDTH - asteroid_size), random.randint(-300, -50), asteroid_size, asteroid_size)
        for _ in range(3)  # Reduced to 3
    ]

    # Boss setup
    boss = pygame.Rect(WIDTH // 2 - boss_width // 2, -boss_height, boss_width, boss_height)

    # Particle effects setup
    explosion_particles = []

    # Game variables
    running = True
    score = 0
    boss_kills = 0  # Track how many bosses defeated in a row
    global boss_active, boss_health, boss_spawn_timer

    while running:
        draw_background()

        # Handle particle effects (explosions)
        for particle in explosion_particles[:]:
            particle.update()
            particle.draw()
            if particle.life <= 0:
                explosion_particles.remove(particle)

        # Move background asteroids
        for asteroid in background_asteroids:
            asteroid.y += background_asteroid_speed
            if asteroid.y > HEIGHT:
                asteroid.y = random.randint(-600, 0)
                asteroid.x = random.randint(0, WIDTH - 40)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x > 0:
            player.x -= ship_speed
        if keys[pygame.K_RIGHT] and player.x < WIDTH - ship_width:
            player.x += ship_speed

        # Fire bullets
        if keys[pygame.K_SPACE]:
            weapon.fire()

        # Update bullets
        weapon.update()

        # Spawn and update enemies
        for enemy in enemies[:]:
            enemy.y += enemy_speed

            # Check collision with bullets
            for bullet in weapon.bullets[:]:
                if enemy.colliderect(bullet):
                    enemies.remove(enemy)
                    weapon.bullets.remove(bullet)
                    score += 10
                    break

            # Remove enemies that go off-screen
            if enemy.y > HEIGHT:
                enemies.remove(enemy)

        # Spawn more enemies if needed
        while len(enemies) < 5:
            enemies.append(
                pygame.Rect(random.randint(0, WIDTH - enemy_width), random.randint(-150, -40), enemy_width, enemy_height)
            )

        # Update asteroids
        for asteroid in asteroids[:]:
            asteroid.y += asteroid_speed

            # Check collision with player
            if player.colliderect(asteroid):
                draw_text("Game Over!", RED, WIDTH // 2 - 100, HEIGHT // 2)
                pygame.display.update()
                pygame.time.delay(2000)
                running = False

            # Remove asteroids that go off-screen
            if asteroid.y > HEIGHT:
                asteroids.remove(asteroid)

        # Spawn more asteroids if needed
        while len(asteroids) < 3:  # Reduced to 3
            asteroids.append(
                pygame.Rect(random.randint(0, WIDTH - asteroid_size), random.randint(-300, -50), asteroid_size, asteroid_size)
            )

        # Handle boss
        if boss_active:
            boss.y += boss_speed
            pygame.draw.rect(display, RED, boss)
            draw_text(f"Boss HP: {boss_health}", WHITE, WIDTH // 2 - 50, 10)
            for bullet in weapon.bullets[:]:
                if boss.colliderect(bullet):
                    weapon.bullets.remove(bullet)
                    boss_health -= 1

            if boss_health <= 0:
                score += 50
                boss_kills += 1
                if boss_kills % 5 == 0:  # After 5 bosses, unlock wing weapon
                    weapon.weapon_type = 3
                boss_active = False
                boss_health = 10
                # --- Trigger explosion when boss dies ---
                for _ in range(100):
                    explosion_particles.append(Particle(boss.x + boss_width // 2, boss.y + boss_height // 2, RED, random.randint(5, 10), random.randint(30, 60)))
                # --- End explosion trigger ---
                bullets.extend([
                    pygame.Rect(player.x + ship_width // 2 - bullet_width // 2, player.y, bullet_width, bullet_height)
                    for _ in range(3)
                ])

        else:
            boss_spawn_timer += 1
            if boss_spawn_timer >= boss_spawn_interval:
                boss_active = True
                boss_spawn_timer = 0
                boss.y = -boss_height

        # Draw player
        pygame.draw.polygon(
            display, BLUE, [(player.x, player.y + ship_height), (player.x + ship_width, player.y + ship_height), (player.x + ship_width // 2, player.y)]
        )

        # Draw bullets
        weapon.draw()

        # Draw enemies
        for enemy in enemies:
            pygame.draw.rect(display, GREEN, enemy)

        # Draw asteroids
        for asteroid in asteroids:
            pygame.draw.rect(display, YELLOW, asteroid)

        # Draw score
        draw_text(f"Score: {score}", WHITE, 10, 10)

        pygame.display.update()
        clock.tick(60)

    pygame.quit()

# Show start screen before starting game
start_screen()

# Run the game
game_loop()