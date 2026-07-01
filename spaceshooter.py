import pygame
import random
import math

# Initialize Pygame
pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter: Boss & Particles Edition")

clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
GRAY = (150, 150, 150)
YELLOW = (255, 255, 0)

BULLET_COLORS = [(0, 255, 255), (255, 255, 0), (255, 0, 255), (255, 165, 0), (0, 128, 255)]

# Game Variables
player = pygame.Rect(370, 520, 60, 60)
player_speed = 5

bullets = []
enemies = []
particles = []  # Explosion animation ke liye list

# Gameplay Stats
score = 0
level = 1
enemy_timer = 0
enemy_speed = 2
score_to_next_level = 10

# Boss Variables
boss = None
boss_health = 0
boss_max_health = 0
boss_speed = 2
boss_direction = 1
boss_active = False

font = pygame.font.SysFont(None, 36)
game_over_font = pygame.font.SysFont(None, 72)

running = True
game_over = False

# --- KHOOBSURAT ANIMATION FUNCTION ---
def create_explosion(x, y):
    """Jab boss marega, toh rang-birange particles charo taraf phelein ge"""
    for _ in range(100):  # 100 colorful particles banenge
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 7)
        particle = {
            "x": x,
            "y": y,
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,
            "radius": random.randint(3, 8),
            "color": random.choice(BULLET_COLORS),
            "lifetime": random.randint(30, 60)  # Kitni der tak particle dikhega
        }
        particles.append(particle)

# --- RESTART FUNCTION ---
def restart_game():
    global game_over, score, level, enemy_speed, score_to_next_level, enemy_timer
    global boss, boss_active, bullets, enemies, particles
    game_over = False
    score = 0
    level = 1
    enemy_speed = 2
    score_to_next_level = 10
    enemy_timer = 0
    boss = None
    boss_active = False
    bullets.clear()
    enemies.clear()
    particles.clear()
    player.x = 370

# --- MAIN LOOP ---
while running:
    clock.tick(60)

    # 1. Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                b_color = random.choice(BULLET_COLORS)
                # Triple shot
                bullets.append({"rect": pygame.Rect(player.centerx - 3, player.top, 6, 15), "speed_x": 0, "color": b_color})
                bullets.append({"rect": pygame.Rect(player.centerx - 15, player.top, 6, 15), "speed_x": -2, "color": b_color})
                bullets.append({"rect": pygame.Rect(player.centerx + 9, player.top, 6, 15), "speed_x": 2, "color": b_color})
            
            if game_over and event.key == pygame.K_r:
                restart_game()

    # 2. Game Logic
    if not game_over:
        # Player Move
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.left > 0: player.x -= player_speed
        if keys[pygame.K_RIGHT] and player.right < WIDTH: player.x += player_speed

        # Level Up & Boss Spawn Logic
        if score >= score_to_next_level and not boss_active:
            boss_active = True
            boss_max_health = 5 + (level * 5)  # Har level mein boss ki health barhegi
            boss_health = boss_max_health
            boss = pygame.Rect(WIDTH // 2 - 60, -100, 120, 80) # Bada Boss spawn hua
            enemies.clear() # Boss aane par aam dushman saaf

        # Move Bullets
        for bullet in bullets[:]:
            bullet["rect"].y -= 10
            bullet["rect"].x += bullet["speed_x"]
            if bullet["rect"].bottom < 0 or bullet["rect"].right < 0 or bullet["rect"].left > WIDTH:
                bullets.remove(bullet)

        # Move Particles (Animation Update)
        for p in particles[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["lifetime"] -= 1
            if p["lifetime"] <= 0:
                particles.remove(p)

        # Enemy Spawning (Sirf tab jab boss na ho)
        if not boss_active:
            enemy_timer += 1
            if enemy_timer > max(15, 35 - level * 2): # Level barhne se dushman jaldi aayenge
                enemy_timer = 0
                x = random.randint(0, WIDTH - 40)
                enemies.append(pygame.Rect(x, -40, 40, 40))

            # Move Enemies
            for enemy in enemies[:]:
                enemy.y += enemy_speed
                if enemy.top > HEIGHT: enemies.remove(enemy)
                if enemy.colliderect(player): game_over = True
        else:
            # --- BOSS LOGIC ---
            # Boss entrance animation
            if boss.y < 50:
                boss.y += 2
            else:
                # Boss left-right movement
                boss.x += boss_speed * boss_direction
                if boss.right >= WIDTH or boss.left <= 0:
                    boss_direction *= -1

            if boss.colliderect(player):
                game_over = True

        # Bullet Collisions
        for bullet in bullets[:]:
            # Check collision with Normal Enemies
            if not boss_active:
                for enemy in enemies[:]:
                    if bullet["rect"].colliderect(enemy):
                        if bullet in bullets: bullets.remove(bullet)
                        if enemy in enemies: enemies.remove(enemy)
                        score += 1
                        break
            else:
                # Check collision with Boss
                if boss and bullet["rect"].colliderect(boss):
                    if bullet in bullets: bullets.remove(bullet)
                    boss_health -= 1
                    
                    # Agar Boss Mar Gaya!
                    if boss_health <= 0:
                        create_explosion(boss.centerx, boss.centery) # Khoobsurat Dhamaka!
                        score += 10
                        level += 1
                        score_to_next_level = score + 10 + (level * 5)
                        enemy_speed += 0.5 # Agla level mushkil karne ke liye
                        boss_active = False
                        boss = None
                    break

    # 3. Drawing
    screen.fill(BLACK)

    # Particles animation background mein chalegi
    for p in particles:
        pygame.draw.circle(screen, p["color"], (int(p["x"]), int(p["y"])), p["radius"])

    if not game_over:
        # Draw Player
        pygame.draw.rect(screen, GREEN, player)
        
        # Draw Bullets
        for bullet in bullets:
            pygame.draw.rect(screen, bullet["color"], bullet["rect"])
            
        # Draw Enemies
        if not boss_active:
            for enemy in enemies:
                pygame.draw.rect(screen, RED, enemy)
        else:
            # Draw Boss
            if boss:
                pygame.draw.rect(screen, RED, boss)
                # Boss Health Bar
                health_bar_width = 120
                current_health_bar = (boss_health / boss_max_health) * health_bar_width
                pygame.draw.rect(screen, GRAY, (boss.x, boss.y - 15, health_bar_width, 8))
                pygame.draw.rect(screen, YELLOW, (boss.x, boss.y - 15, current_health_bar, 8))

        # UI Text (Score & Level)
        ui_text = font.render(f"Score: {score}  |  Level: {level}", True, WHITE)
        screen.blit(ui_text, (10, 10))
        
        if boss_active:
            boss_text = font.render("BOSS FIGHT!", True, YELLOW)
            screen.blit(boss_text, (WIDTH // 2 - boss_text.get_width() // 2, 10))
    else:
        # Game Over Screen
        go_text = game_over_font.render("GAME OVER", True, RED)
        score_text = font.render(f"Final Score: {score}  |  Reached Level: {level}", True, WHITE)
        restart_text = font.render("Press 'R' to Restart", True, GRAY)

        screen.blit(go_text, (WIDTH // 2 - go_text.get_width() // 2, HEIGHT // 3))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 1.5))

    pygame.display.flip()

pygame.quit()