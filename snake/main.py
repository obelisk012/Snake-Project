import pygame
import random

pygame.init()

# Animation

class Animation():
    def __init__(self, frames, speed=0.1, sheet=None, frame_width=12, frame_height=12):
        self.frames = frames
        self.speed = speed
        self.current_frame = 0
        self.tick = 0
        self.sheet = sheet
        self.frame_width = frame_width
        self.frame_height = frame_height
        
        self.last_update = 0

    def get_frame(sheet, x, y, width, height):
        frame = pygame.Surface((width, height), pygame.SRCALPHA)
        frame.fill((0, 0, 0, 0))
        frame.blit(sheet, (0, 0), pygame.Rect(x, y, width, height))
        return frame
    
    def extract_frames(sheet, frame_width, frame_height, num_frames):
        frames = []
        for i in range(num_frames):
            frames.append(Animation.get_frame(sheet, i*frame_width, 0, frame_width, frame_height))
        return frames
    


# Background

def draw_background():
    screen.fill(BACKGROUND_COLOR)

    extra_incr = 0

    for i in range(int((screen_size[0]/50)-2)):
        increment = 50*(i+1)
        extra_incr += 1

        for i in range(int((screen_size[1]/50)-2)):
            pygame.draw.rect(screen, (GROUND_COLORS[((i+extra_incr)%2)]), (50*(i+1), increment, 50, 50))

# Food

FOOD_EXTRA_DELAY = 300
FOOD_EXTRA_TICK = 0
class FoodBrain():
    def __init__(self, starting_foods=3):
        self.food_types = [Apple(), Bomb(), Hamburger()]
        self.weights = [food.chance for food in self.food_types]
        self.starting_foods = starting_foods
        self.foods = []

    def spawn_food(self):
        food = random.choices(self.food_types, weights=self.weights, k=1)[0].__class__()  # Create a new instance
        food.x = random.randint(1, 10) * 50
        food.y = random.randint(1, 10) * 50
        food.pos = (food.x, food.y)
        if food.pos == (snake.x, snake.y) or any(cell.pos == food.pos for cell in snake.cells):
            return self.spawn_food()
        for existing_food in self.foods:
            if food.pos == existing_food.pos:
                return self.spawn_food()
        self.foods.append(food)

class Food():
    def __init__(self, chance = 0, image=None, sound=None, max_amount=None):
        self.chance = chance
        self.image = image
        self.sound = sound
        self.x = 0
        self.y = 0
        self.pos = (self.x, self.y)

    def eat(self, snake, food_brain):
        pass

class Apple(Food):
    def __init__(self):
        super().__init__(20, pygame.image.load('snake/sprites/apple.png').convert_alpha(), sound=None)
    
    def eat(self, snake, food_brain):
        snake.grow()
        print("Eat apple")

        if self.sound is not None:
            pygame.mixer.Sound.play(self.sound)

        food_brain.spawn_food()

EXPLOSION = False
EXPLOSION_X = 0
EXPLOSION_Y = 0
EXPLOSION_ANIMATION = None
EXPLOSION_FRAME_INDEX = 0
EXPLOSION_FRAME_TIMER = 0
EXPLOSION_FRAME_DELAY = 2  # Number of frames to wait before advancing explosion frame
class Bomb(Food):
    def __init__(self):
        super().__init__(5, pygame.image.load('snake/sprites/bomb.png').convert_alpha(), sound=None, max_amount=1)
    
    def eat(self, snake, food_brain):
        if self.sound is not None:
            pygame.mixer.Sound.play(self.sound)
        snake.kill(food_brain)
        print("Explode💣💥")
        food_brain.spawn_food()
        global EXPLOSION, EXPLOSION_X, EXPLOSION_Y, EXPLOSION_ANIMATION, EXPLOSION_FRAME_INDEX, EXPLOSION_FRAME_TIMER
        EXPLOSION = True
        EXPLOSION_X = self.x
        EXPLOSION_Y = self.y
        EXPLOSION_ANIMATION = Animation.extract_frames(pygame.image.load('snake/sprites/explosion_sheet.png').convert_alpha(), 12, 12, 9)
        EXPLOSION_FRAME_INDEX = 0
        EXPLOSION_FRAME_TIMER = 0


class Hamburger(Food):
    def __init__(self):
        super().__init__(2, pygame.image.load('snake/sprites/hamburger.png').convert_alpha(), sound=None)
    
    def eat(self, snake, food_brain):
        snake.grow(3)
        print("Eat hamburger")

        if self.sound is not None:
            pygame.mixer.Sound.play(self.sound)

        food_brain.spawn_food()


# Snake

class Cell():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.pos = (self.x, self.y)

class Snake():
    def __init__(self, color, current_direction, speed=6):
        self.x = 150
        self.y = 300
        self.pos = (self.x, self.y)

        self.speed = speed

        self.death_sound = pygame.mixer.Sound('snake/sounds/death_oof_minecraft.wav')

        self.color = color

        self.head = pygame.transform.scale(pygame.image.load('snake/sprites/snake_head.png').convert_alpha(), (50, 50))

        self.current_direction = current_direction

        self.cells = [Cell(self.x, self.y), Cell(self.x-50, self.y)]

        self.current_direction_update = Right()

    def move(self):
        for i in range(len(self.cells) - 1, 0, -1):
            self.cells[i].x = self.cells[i-1].x
            self.cells[i].y = self.cells[i-1].y
            self.cells[i].pos = (self.cells[i].x, self.cells[i].y)
        self.current_direction.move(self)
        self.cells[0].x = self.x
        self.cells[0].y = self.y
        self.cells[0].pos = (self.x, self.y)

    def kill(self, food_brain=None):
        self.cells = [Cell(self.x, self.y), Cell(self.x-50, self.y)]
        self.x = 150
        self.y = 300
        self.current_direction = Right()
        self.current_direction_update = Right()
        global FPS
        FPS = 60
        pygame.mixer.Sound.play(self.death_sound)
        print("You died")
        food_brain.foods = []
        global FOOD_EXTRA_TICK
        FOOD_EXTRA_TICK = 0
        for i in range(food_brain.starting_foods):
            food_brain.spawn_food()
        draw_background()

    def grow(self, amount=1):
        for i in range(amount):
            tail = self.cells[-1]
            self.cells.append(Cell(tail.x, tail.y))

# Directions

class Direction():
    def __init__(self, angle=0):
        self.angle = angle
    def move(self, snake):
        raise NotImplementedError("Invalid direction")
    
class Up(Direction):
    def __init__(self):
        super().__init__(180)
    def move(self, snake):
        print("Move up")
        snake.y -= 50
    
class Down(Direction):
    def __init__(self):
        super().__init__(0)
    def move(self, snake):
        print("Move down")
        snake.y += 50
    
class Left(Direction):
    def __init__(self):
        super().__init__(90)
    def move(self, snake):
        print("Move left")
        snake.x -= 50

class Right(Direction):
    def __init__(self):
        super().__init__(-90)
    def move(self, snake):
        print("Move right")
        snake.x += 50

# Background

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

SNAKE_COLOR = (47, 53, 153)

BACKGROUND_COLOR = (1, 82, 22)
GROUND_COLOR_0 = (34, 177, 76)
GROUND_COLOR_1 = (168, 230, 29)

GROUND_COLORS = [GROUND_COLOR_0, GROUND_COLOR_1]

color_switch = 0

# Screen

clock = pygame.time.Clock()
FPS = 60

screen_size = (600, 600)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("Snake")

img = pygame.image.load('snake/sprites/snake_logo.png')
pygame.display.set_icon(img)

# Game Loop

snake = Snake(SNAKE_COLOR, Right())
food_brain = FoodBrain()
food_initialized = False
move_tick = 0
key_clicked = False
paused = False

running = True
while running:
    if paused:
        continue
    move_tick += 1
    if not food_initialized:
        for i in range(food_brain.starting_foods):
            food_brain.spawn_food()
        food_initialized = True
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                if not isinstance(snake.current_direction, Down) and not key_clicked:
                    snake.current_direction_update = Up()
                    key_clicked = True
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                if not isinstance(snake.current_direction, Right) and not key_clicked:
                    snake.current_direction_update = Left()
                    key_clicked = True
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                if not isinstance(snake.current_direction, Left) and not key_clicked:
                    snake.current_direction_update = Right()
                    key_clicked = True
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                if not isinstance(snake.current_direction, Up) and not key_clicked:
                    snake.current_direction_update = Down()
                    key_clicked = True
    
    draw_background()

    if FOOD_EXTRA_TICK >= FOOD_EXTRA_DELAY:
        FOOD_EXTRA_TICK = 0
        food_brain.spawn_food()
    else:
        FOOD_EXTRA_TICK += 1

    for food in food_brain.foods[:]:
        screen.blit(pygame.transform.scale(food.image, (50, 50)), food.pos)
        if snake.cells[0].pos == food.pos:
            food.eat(snake, food_brain)
            if food in food_brain.foods:
                food_brain.foods.remove(food)
    for cell in snake.cells:
        if cell.pos == snake.cells[0].pos and cell != snake.cells[0]:
            snake.kill(food_brain)

    if move_tick == int((60//snake.speed)):
        move_tick = 0
        key_clicked = False
        snake.current_direction = snake.current_direction_update
        snake.move()

    for cell in snake.cells:
        pygame.draw.rect(screen, snake.color, (cell.x, cell.y, 50, 50))

    if snake.y > screen_size[1]-100 or snake.y < 50 or snake.x > screen_size[0]-100 or snake.x < 50:
        snake.kill(food_brain)
 
    print(f"{snake.x}, {snake.y}")

    screen.blit(pygame.transform.rotate(snake.head, snake.current_direction.angle), snake.cells[0].pos)

    if EXPLOSION and EXPLOSION_ANIMATION is not None:
        move_tick = 0
        draw_background()
        for food in food_brain.foods:
            screen.blit(pygame.transform.scale(food.image, (50, 50)), food.pos)
        for cell in snake.cells:
            pygame.draw.rect(screen, snake.color, (cell.x, cell.y, 50, 50))
        screen.blit(pygame.transform.rotate(snake.head, snake.current_direction.angle), snake.cells[0].pos)
        frame = EXPLOSION_ANIMATION[EXPLOSION_FRAME_INDEX]
        screen.blit(pygame.transform.scale(frame, (150, 150)), (EXPLOSION_X-50, EXPLOSION_Y-50))
        EXPLOSION_FRAME_TIMER += 1
        if EXPLOSION_FRAME_TIMER >= EXPLOSION_FRAME_DELAY:
            EXPLOSION_FRAME_TIMER = 0
            EXPLOSION_FRAME_INDEX += 1
            if EXPLOSION_FRAME_INDEX >= len(EXPLOSION_ANIMATION):
                EXPLOSION = False
                EXPLOSION_ANIMATION = None
                EXPLOSION_FRAME_INDEX = 0
                EXPLOSION_FRAME_TIMER = 0

    pygame.display.flip()

    clock.tick(FPS)

pygame.quit()