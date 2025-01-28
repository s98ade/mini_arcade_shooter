import pygame
import random

class Bullet:
    """ 
    This class models each bullet and handles its events.
    
    """
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.speed = 5
        self.direction = direction 
        self.size = 5 
    def update_position(self):
        if self.direction == "right":
            self.x += self.speed
        elif self.direction == "left":
            self.x -= self.speed
        elif self.direction == "down":
            self.y += self.speed
        elif self.direction == "up":
            self.y -= self.speed

    def draw(self, window):
        pygame.draw.rect(window, (255, 255, 0), (self.x, self.y, self.size, self.size))
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)


class Enemy:
    """ 
    This class models each enemy and defines their behavior.
    
    """
    def __init__(self, image, screen_width, screen_height, speed):
        self.image = image
        self.width, self.height = 80, 80
        self.speed = speed 
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.spawn_enemy() 
    def spawn_enemy(self):
        side = random.choice(["left", "right", "top", "bottom"])
        if side == "left":
            self.x = 0
            self.y = random.randint(0, self.screen_height - self.height)
        elif side == "right":
            self.x = self.screen_width - self.width
            self.y = random.randint(0, self.screen_height - self.height)
        elif side == "top":
            self.x = random.randint(0, self.screen_width - self.width)
            self.y = 0
        elif side == "bottom":
            self.x = random.randint(0, self.screen_width - self.width)
            self.y = self.screen_height - self.height
            
    def update_position(self, robot_x, robot_y):
        if self.x < robot_x:
            self.x += self.speed
        elif self.x > robot_x:
            self.x -= self.speed
        if self.y < robot_y:
            self.y += self.speed
        elif self.y > robot_y:
            self.y -= self.speed
    
    def draw(self, window):
        window.blit(self.image, (self.x, self.y))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    

class Robot:
    """ 
    This class models the player and its events.
    """
    def __init__(self, image_path, start_x, start_y):
        self.image = pygame.image.load(image_path)
        self.x = start_x
        self.y = start_y
        self.speed = 3
        self.direction = {"left": False, "right": False, "up": False, "down": False} 
    
    def update_position(self, screen_width, screen_height):
        if self.direction["right"] and self.x + self.image.get_width() < screen_width:
            self.x += self.speed
        if self.direction["left"] and self.x > 0:
            self.x -= self.speed
        if self.direction["down"] and self.y + self.image.get_height() < screen_height:
            self.y += self.speed
        if self.direction["up"] and self.y > 0:
            self.y -= self.speed
    
    def draw(self, window):
        window.blit(self.image, (self.x, self.y))

    def set_direction(self, key, value):
        if key == pygame.K_a:
            self.direction["left"] = value
        elif key == pygame.K_d:
            self.direction["right"] = value
        elif key == pygame.K_s:
            self.direction["down"] = value
        elif key == pygame.K_w:
            self.direction["up"] = value
            
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())


class Game:
    """ 
    Main class handling the game logic.
    """
    def __init__(self, width, height, robot_image_path, enemy_image_path):
        pygame.init() 
        self.font = pygame.font.Font(None, 36)
        self.width = width
        self.height = height
        self.window = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.robot = Robot(robot_image_path, width // 2, height // 2)
        self.enemy_image = pygame.image.load(enemy_image_path)
        self.enemies = [] 
        self.bullets = []
        self.running = True
        self.defeated_monsters = 0
        self.monster_speed = 1.5
        self.spawn_counter = 0
        self.spawn_interval = 60

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                else:
                    self.robot.set_direction(event.key, True)
                
                if event.key == pygame.K_RIGHT:
                    self.shoot_bullet("right")
                elif event.key == pygame.K_LEFT:
                    self.shoot_bullet("left")
                elif event.key == pygame.K_DOWN:
                    self.shoot_bullet("down")
                elif event.key == pygame.K_UP:
                    self.shoot_bullet("up")
            
            elif event.type == pygame.KEYUP:
                self.robot.set_direction(event.key, False)
            
            
    def shoot_bullet(self, direction):
        bullet_x = self.robot.x + self.robot.image.get_width() // 2
        bullet_y = self.robot.y + self.robot.image.get_height() // 2
        bullet = Bullet(bullet_x, bullet_y, direction)
        self.bullets.append(bullet)
        
    def check_collisions(self):
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if bullet.get_rect().colliderect(enemy.get_rect()):
                    self.bullets.remove(bullet)
                    self.enemies.remove(enemy)
                    self.defeated_monsters += 1 

                    if self.defeated_monsters % 10 == 0:
                        self.monster_speed += 0.2 
                    if self.defeated_monsters % 20 == 0:
                        self.spawn_interval -= 10
                    break

        for enemy in self.enemies:
            if self.robot.get_rect().colliderect(enemy.get_rect()):
                print("Game Over!")
                self.running = False
                
    def spawn_enemy(self):
        if self.spawn_counter >= self.spawn_interval:
            enemy = Enemy(self.enemy_image, self.width, self.height, self.monster_speed)
            self.enemies.append(enemy)
            self.spawn_counter = 0
        else:
            self.spawn_counter += 1 

    def update(self):
        self.robot.update_position(self.width, self.height)
        
        for enemy in self.enemies:
            enemy.update_position(self.robot.x, self.robot.y)
        
        for bullet in self.bullets[:]:
            bullet.update_position()
            if bullet.x < 0 or bullet.x > self.width or bullet.y < 0 or bullet.y > self.height:
                self.bullets.remove(bullet)
        
        self.spawn_enemy() 
        self.check_collisions()

    def draw(self):
        self.window.fill((210, 150, 75))
        self.robot.draw(self.window)

        for enemy in self.enemies:
            enemy.draw(self.window)
        
        for bullet in self.bullets:
            bullet.draw(self.window)
            
        counter_text = self.font.render(f"Counter: {self.defeated_monsters}", True, (255, 255, 255))
        self.window.blit(counter_text, (10, 10))
            
        pygame.display.flip()      

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        pygame.quit()


if __name__ == "__main__":
    SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 800
    game = Game(SCREEN_WIDTH, SCREEN_HEIGHT, "./src/robot.png", "./src/monster.png") # change images
    game.run()