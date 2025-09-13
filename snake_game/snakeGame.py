import pygame, sys, random, math, time

# Инициализация
pygame.init()
GRID_SIZE, MIN_CELL_SIZE, HEADER_HEIGHT, FPS = 16, 40, 60, 60
BACKGROUND, GRID_COLOR = (15, 30, 15), (30, 60, 30)
SNAKE_COLOR, SNAKE_HEAD_COLOR = (40, 180, 40), (0, 230, 80)
SPEED_COLOR, SPEED_HEAD_COLOR = (255, 215, 0), (255, 235, 100)
FOOD_COLOR, POISON_COLOR, SPEED_POTION_COLOR = (220, 50, 50), (150, 0, 200), (50, 150, 255)
HEADER_COLOR, TEXT_COLOR, ACCENT_COLOR = (20, 40, 20), (220, 240, 220), (0, 180, 150)
UP, DOWN, LEFT, RIGHT = (0, -1), (0, 1), (-1, 0), (1, 0)

class Snake:
    def __init__(self, cell_size):
        self.cell_size = cell_size
        self.reset()
        
    def reset(self):
        self.positions = [(GRID_SIZE//2, GRID_SIZE//2)]
        self.direction = self.next_direction = RIGHT
        self.score = self.grow_to = 0
        self.alive, self.last_move_time, self.move_delay = True, time.time(), 0.15
        self.speed_effect_end = 0
        self.old_positions = self.positions.copy()
        self.move_progress = 0.0
        
    def get_head_position(self): 
        return self.positions[0]
    
    def update(self, delta_time):
        if time.time() - self.last_move_time < self.move_delay: 
            self.move_progress = min(1.0, (time.time() - self.last_move_time) / self.move_delay)
            return True
        
        self.direction = self.next_direction
        self.last_move_time = time.time()
        self.move_progress = 0.0
        self.old_positions = self.positions.copy()
        
        head = self.get_head_position()
        new_pos = (head[0] + self.direction[0], head[1] + self.direction[1])
        
        # Проверка столкновений
        if (new_pos[0] < 0 or new_pos[0] >= GRID_SIZE or 
            new_pos[1] < 0 or new_pos[1] >= GRID_SIZE or
            new_pos in self.positions[1:]):
            self.alive = False
            return False
        
        self.positions.insert(0, new_pos)
        if len(self.positions) > self.grow_to: 
            self.positions.pop()
            
        # Проверяем окончание эффекта скорости
        if self.speed_effect_end > 0 and time.time() > self.speed_effect_end:
            self.speed_effect_end = 0
            self.move_delay = 0.15
            
        return True
    
    def activate_speed_effect(self, duration=3.0):
        self.speed_effect_end = time.time() + duration
        self.move_delay = max(0.05, self.move_delay * 0.5)
    
    def grow(self):
        self.grow_to += 1
        self.score += 10
    
    def shrink(self):
        if self.grow_to > 1:
            self.grow_to -= 1
            self.score = max(0, self.score - 5)
            if len(self.positions) > self.grow_to: 
                self.positions.pop()
    
    def draw(self, surface, offset_x, offset_y):
        # Определяем цвета в зависимости от эффекта скорости
        if time.time() < self.speed_effect_end:
            head_color = SPEED_HEAD_COLOR
            body_color = SPEED_COLOR
            highlight_color = (255, 245, 150)
            scale_color = (255, 215, 100)  # Золотистый цвет точек при скорости
        else:
            head_color = SNAKE_HEAD_COLOR
            body_color = SNAKE_COLOR
            highlight_color = (30, 200, 70)
            scale_color = (30, 160, 30)  # Зелёный цвет точек без скорости
        
        for i, pos in enumerate(self.positions):
            # Плавная интерполяция позиций
            if i < len(self.old_positions):
                old_pos = self.old_positions[i]
                interp_x = old_pos[0] + (pos[0] - old_pos[0]) * self.move_progress
                interp_y = old_pos[1] + (pos[1] - old_pos[1]) * self.move_progress
            else:
                interp_x, interp_y = pos
                
            rect = pygame.Rect(offset_x + interp_x * self.cell_size, 
                               offset_y + interp_y * self.cell_size, 
                               self.cell_size, self.cell_size)
            
            if i == 0:  # Голова
                pygame.draw.rect(surface, head_color, rect, border_radius=8)
                highlight = pygame.Rect(rect.x+2, rect.y+2, rect.width-4, rect.height-4)
                pygame.draw.rect(surface, highlight_color, highlight, border_radius=6)
                
                eye_size, eye_offset = self.cell_size//6, self.cell_size//3
                eye_pos = {
                    RIGHT: [(rect.right - eye_offset, rect.top + eye_offset), 
                           (rect.right - eye_offset, rect.bottom - eye_offset)],
                    LEFT: [(rect.left + eye_offset, rect.top + eye_offset), 
                          (rect.left + eye_offset, rect.bottom - eye_offset)],
                    UP: [(rect.left + eye_offset, rect.top + eye_offset), 
                        (rect.right - eye_offset, rect.top + eye_offset)],
                    DOWN: [(rect.left + eye_offset, rect.bottom - eye_offset), 
                          (rect.right - eye_offset, rect.bottom - eye_offset)]
                }[self.direction]
                
                for eye in eye_pos:
                    pygame.draw.circle(surface, (255, 255, 255), eye, eye_size)
                    pygame.draw.circle(surface, (0, 0, 0), eye, eye_size//2)
                
                if self.direction in (LEFT, RIGHT):
                    tongue_x = rect.centerx + (rect.width//3 if self.direction == RIGHT else -rect.width//3)
                    pygame.draw.rect(surface, (255, 0, 0), (tongue_x-2, rect.centery-3, 4, 6), border_radius=2)
            else:  # Тело
                segment = rect.inflate(-4, -4)
                pygame.draw.rect(surface, body_color, segment, border_radius=6)
                scale_size = self.cell_size//3
                for y in range(segment.top + scale_size//2, segment.bottom, scale_size):
                    for x in range(segment.left + scale_size//2, segment.right, scale_size):
                        pygame.draw.circle(surface, scale_color, (x, y), scale_size//3)

class Food:
    def __init__(self, cell_size):
        self.cell_size, self.position, self.pulse = cell_size, (0, 0), 0
        self.randomize_position()
    
    def randomize_position(self):
        self.position = (random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1))
    
    def update(self): 
        self.pulse = (self.pulse + 0.1) % (2 * math.pi)
    
    def draw(self, surface, offset_x, offset_y, color, highlight_color):
        cx = offset_x + self.position[0]*self.cell_size + self.cell_size//2
        cy = offset_y + self.position[1]*self.cell_size + self.cell_size//2
        radius = self.cell_size//2 - 3 + math.sin(self.pulse)*2
        
        pygame.draw.circle(surface, color, (cx, cy), radius)
        pygame.draw.circle(surface, highlight_color, (cx - radius//3, cy - radius//3), radius//3)
        
        if color == FOOD_COLOR:
            leaf = [(cx, cy - radius), (cx - radius//2, cy - radius - radius//3), 
                   (cx + radius//2, cy - radius - radius//3)]
            pygame.draw.polygon(surface, (80, 200, 80), leaf)
            pygame.draw.line(surface, (100, 70, 30), (cx, cy - radius), (cx, cy - radius//2), 2)

class Poison(Food):
    def __init__(self, cell_size):
        super().__init__(cell_size)
        self.active, self.spawn_timer = False, 0
        
    def update(self, delta_time):
        super().update()
        if not self.active:
            self.spawn_timer += delta_time
            if self.spawn_timer > random.randint(15, 25):
                self.active, self.spawn_timer = True, 0
                self.randomize_position()
    
    def draw(self, surface, offset_x, offset_y):
        if not self.active: return
        cx = offset_x + self.position[0]*self.cell_size + self.cell_size//2
        cy = offset_y + self.position[1]*self.cell_size + self.cell_size//2
        height = self.cell_size//2 + math.sin(self.pulse)*2
        
        bottle = pygame.Rect(cx - self.cell_size//4, cy - height//2, self.cell_size//2, height)
        pygame.draw.rect(surface, POISON_COLOR, bottle, border_radius=8)
        
        neck = pygame.Rect(cx - self.cell_size//8, cy - height//2 - self.cell_size//6, 
                          self.cell_size//4, self.cell_size//6)
        pygame.draw.rect(surface, POISON_COLOR, neck, border_radius=4)
        
        for _ in range(5):
            bubble = (random.randint(bottle.left+5, bottle.right-5), 
                     random.randint(bottle.top+5, bottle.bottom-5))
            pygame.draw.circle(surface, (200, 230, 255), bubble, random.randint(2,4))

class SpeedPotion(Food):
    def __init__(self, cell_size):
        super().__init__(cell_size)
        self.active, self.spawn_timer, self.lifetime = False, 0, 0
        self.rotation = 0
        
    def update(self, delta_time):
        super().update()
        self.rotation = (self.rotation + delta_time * 100) % 360
        
        if not self.active:
            self.spawn_timer += delta_time
            if self.spawn_timer > random.randint(10, 20):
                self.active, self.spawn_timer = True, 0
                self.lifetime = random.uniform(5.0, 8.0)
                self.randomize_position()
        elif self.active:
            self.lifetime -= delta_time
            if self.lifetime <= 0:
                self.active = False
    
    def draw(self, surface, offset_x, offset_y):
        if not self.active: return
        cx = offset_x + self.position[0]*self.cell_size + self.cell_size//2
        cy = offset_y + self.position[1]*self.cell_size + self.cell_size//2
        radius = self.cell_size//3 + math.sin(self.pulse)*3
        
        pygame.draw.circle(surface, SPEED_POTION_COLOR, (cx, cy), radius)
        
        for i in range(4):
            angle = math.radians(self.rotation + i * 90)
            start_x = cx + math.cos(angle) * (radius * 0.7)
            start_y = cy + math.sin(angle) * (radius * 0.7)
            end_x = cx + math.cos(angle) * (radius * 1.2)
            end_y = cy + math.sin(angle) * (radius * 1.2)
            pygame.draw.line(surface, (255, 255, 255), (start_x, start_y), (end_x, end_y), 3)
        
        pygame.draw.circle(surface, (180, 230, 255), (cx - radius//3, cy - radius//3), radius//4)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.screen_width, self.screen_height = self.screen.get_size()
        pygame.display.set_caption("Змейка с ядом и зельем скорости")
        
        self.cell_size = max(MIN_CELL_SIZE, min(
            (self.screen_width-40)//GRID_SIZE, (self.screen_height-HEADER_HEIGHT-100)//GRID_SIZE))
        
        self.grid_width, self.grid_height = GRID_SIZE*self.cell_size, GRID_SIZE*self.cell_size
        self.grid_x = (self.screen_width - self.grid_width)//2
        self.grid_y = (self.screen_height - self.grid_height)//2 + 20
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 36)
        self.title_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 24)
        
        self.snake = Snake(self.cell_size)
        self.food = Food(self.cell_size)
        self.poison = Poison(self.cell_size)
        self.speed_potion = SpeedPotion(self.cell_size)
        self.touch_start, self.game_over, self.paused = None, False, False
        self.last_score, self.start_time, self.last_time = 0, time.time(), time.time()
        self.game_over_alpha = 0
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                pygame.quit()
                sys.exit()
            elif event.type == pygame.FINGERDOWN: 
                self.touch_start = (event.x*self.screen_width, event.y*self.screen_height)
            elif event.type == pygame.FINGERUP: 
                if self.touch_start:
                    self.handle_swipe((event.x*self.screen_width, event.y*self.screen_height))
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: 
                    pygame.quit()
                    sys.exit()
                if self.game_over: 
                    self.reset_game()
                else:
                    if event.key == pygame.K_p: 
                        self.paused = not self.paused
                    elif event.key in (pygame.K_w, pygame.K_UP) and self.snake.direction != DOWN: 
                        self.snake.next_direction = UP
                    elif event.key in (pygame.K_s, pygame.K_DOWN) and self.snake.direction != UP: 
                        self.snake.next_direction = DOWN
                    elif event.key in (pygame.K_a, pygame.K_LEFT) and self.snake.direction != RIGHT: 
                        self.snake.next_direction = LEFT
                    elif event.key in (pygame.K_d, pygame.K_RIGHT) and self.snake.direction != LEFT: 
                        self.snake.next_direction = RIGHT
            elif event.type == pygame.MOUSEBUTTONDOWN and self.game_over: 
                self.reset_game()
    
    def handle_swipe(self, touch_end):
        if not self.touch_start or self.game_over or self.paused: 
            return
            
        dx, dy = touch_end[0]-self.touch_start[0], touch_end[1]-self.touch_start[1]
        if abs(dx) > abs(dy): 
            if dx > 50 and self.snake.direction != LEFT: 
                self.snake.next_direction = RIGHT
            elif dx < -50 and self.snake.direction != RIGHT: 
                self.snake.next_direction = LEFT
        else:
            if dy > 50 and self.snake.direction != UP: 
                self.snake.next_direction = DOWN
            elif dy < -50 and self.snake.direction != DOWN: 
                self.snake.next_direction = UP
                
        self.touch_start = None
    
    def update(self):
        current_time = time.time()
        delta_time = current_time - self.last_time
        self.last_time = current_time
        
        if self.game_over: 
            self.game_over_alpha = min(self.game_over_alpha+5, 180)
            return
        if self.paused: 
            return
            
        self.food.update()
        self.poison.update(delta_time)
        self.speed_potion.update(delta_time)
        
        if not self.snake.update(delta_time):
            self.game_over = True
            self.last_score = self.snake.score
            return
            
        head = self.snake.get_head_position()
        if head == self.food.position:
            while True:
                self.food.randomize_position()
                if (self.food.position != self.poison.position or not self.poison.active) and \
                   self.food.position != self.speed_potion.position and \
                   self.food.position not in self.snake.positions: 
                    break
            self.snake.grow()
        
        if self.poison.active and head == self.poison.position:
            self.snake.shrink()
            self.poison.active = False
            
        if self.speed_potion.active and head == self.speed_potion.position:
            self.snake.activate_speed_effect()
            self.speed_potion.active = False
    
    def draw(self):
        self.screen.fill(BACKGROUND)
        pygame.draw.rect(self.screen, HEADER_COLOR, (0, 0, self.screen_width, HEADER_HEIGHT))
        pygame.draw.line(self.screen, ACCENT_COLOR, (0, HEADER_HEIGHT), (self.screen_width, HEADER_HEIGHT), 3)
        
        score_text = self.font.render(f"Счет: {self.snake.score}", True, TEXT_COLOR)
        self.screen.blit(score_text, (30, 15))
        
        elapsed = int(time.time() - self.start_time)
        time_text = self.font.render(f"Время: {elapsed} сек", True, TEXT_COLOR)
        self.screen.blit(time_text, (self.screen_width - time_text.get_width() - 30, 15))
        
        if self.snake.speed_effect_end > time.time():
            time_left = max(0, self.snake.speed_effect_end - time.time())
            speed_text = self.font.render(f"Скорость: {time_left:.1f}с", True, SPEED_HEAD_COLOR)
            self.screen.blit(speed_text, (self.screen_width//2 - speed_text.get_width()//2, 15))
        
        for x in range(0, self.grid_width, self.cell_size):
            pygame.draw.line(self.screen, GRID_COLOR, (self.grid_x+x, self.grid_y), (self.grid_x+x, self.grid_y+self.grid_height))
        for y in range(0, self.grid_height, self.cell_size):
            pygame.draw.line(self.screen, GRID_COLOR, (self.grid_x, self.grid_y+y), (self.grid_x+self.grid_width, self.grid_y+y))
        
        pygame.draw.rect(self.screen, ACCENT_COLOR, (self.grid_x-4, self.grid_y-4, self.grid_width+8, self.grid_height+8), 4, border_radius=8)
        
        self.food.draw(self.screen, self.grid_x, self.grid_y, FOOD_COLOR, (255, 180, 180))
        self.poison.draw(self.screen, self.grid_x, self.grid_y)
        self.speed_potion.draw(self.screen, self.grid_x, self.grid_y)
        self.snake.draw(self.screen, self.grid_x, self.grid_y)
        
        if self.game_over: 
            self.draw_game_over()
        elif self.paused: 
            self.draw_paused()
        
        controls_text = self.font.render("WASD/Свайпы | P - Пауза", True, (180, 220, 180))
        self.screen.blit(controls_text, (self.screen_width//2 - controls_text.get_width()//2, self.screen_height-40))
    
    def draw_game_over(self):
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, self.game_over_alpha))
        self.screen.blit(overlay, (0, 0))
        
        texts = [
            self.title_font.render("ИГРА ОКОНЧЕНА!", True, (200, 50, 50)),
            self.font.render(f"Ваш счет: {self.last_score}", True, TEXT_COLOR),
            self.font.render("Кликните для новой игры", True, ACCENT_COLOR)
        ]
        
        msg_width = max(t.get_width() for t in texts) + 80
        msg_rect = pygame.Rect(self.screen_width//2-msg_width//2, self.screen_height//2-150, msg_width, 300)
        pygame.draw.rect(self.screen, (30, 50, 30), msg_rect, border_radius=15)
        pygame.draw.rect(self.screen, ACCENT_COLOR, msg_rect, 3, border_radius=15)
        
        for i, text in enumerate(texts):
            self.screen.blit(text, (self.screen_width//2 - text.get_width()//2, 
                                  self.screen_height//2 - 60 + i*60))
    
    def draw_paused(self):
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        paused = self.title_font.render("ПАУЗА", True, TEXT_COLOR)
        self.screen.blit(paused, (self.screen_width//2 - paused.get_width()//2, self.screen_height//2-30))
        continue_text = self.font.render("Нажмите P для продолжения", True, ACCENT_COLOR)
        self.screen.blit(continue_text, (self.screen_width//2 - continue_text.get_width()//2, self.screen_height//2+30))
    
    def reset_game(self):
        self.snake = Snake(self.cell_size)
        self.food = Food(self.cell_size)
        self.poison = Poison(self.cell_size)
        self.speed_potion = SpeedPotion(self.cell_size)
        self.game_over, self.paused, self.game_over_alpha = False, False, 0
        self.start_time, self.last_time = time.time(), time.time()
    
    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()