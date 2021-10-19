import pygame as pg
from random import randrange

cellSize = 30
m = Wight = 130
n = Height = 100
m_window = 41
n_window = 30
padding = 2
m_mini = n_mini = 26
mn_range = 13
m_minimap = 10
n_minimap = 5
cellSize_minimap = 2
n_shift_textlog = 19
fps = base_fps = 15
finish = 0
pause = 0
all_matrix = [[]]
wall_color = 'grey'
score = 0

# ALT - замедление
# SHIFT -ускорение


# todo list
# формировка программы по файлам
# оптимизация рисовки стен
# усиления и ослабления змейки (бусты)
# генерация структур по типу лабиринтов
# генерация яблока в пустой клетке
# целесообразность карты массивом
# целесообразность массива стен (+структур) similar to пункт выше
#
#

def create_matrix():
    global all_matrix
    for i in range(Wight):
        for j in range(Height):
            all_matrix[i].append(0)
        all_matrix.append([])

    for i in range(Wight):
        all_matrix[i][0] = 1
        all_matrix[i][Height - 1] = 1

    for i in range(Height):
        all_matrix[0][i] = 1
        all_matrix[Wight - 1][i] = 1


class Food:

    def __init__(self, x, y, x_r, y_r):
        self.x = x
        self.y = y
        self.x_relative = x_r
        self.y_relative = y_r
        self.m = cellSize
        self.n = cellSize
        self.color = 'green'

    def draw(self, window, snake, isminimap=0, cellSize_apple=cellSize, shift_m=0, shift_n=0):
        if not isminimap and -13 <= snake.x - self.x <= 13 and -13 <= snake.y - self.y <= 13:
            pg.draw.rect(window, self.color,
                         ((self.x - snake.x_relative) * cellSize_apple,
                          (self.y - snake.y_relative) * cellSize_apple,
                          cellSize_apple,
                          cellSize_apple))
        elif isminimap:
            pg.draw.rect(window, self.color,
                         (self.x * cellSize_apple + shift_m * self.m,
                          self.y * cellSize_apple + shift_n * self.n,
                          cellSize_apple,
                          cellSize_apple))


class Snake:
    def __init__(self, x, y, x_r, y_r):
        self.x = x
        self.y = y
        self.x_relative = x_r
        self.y_relative = y_r
        self.m = cellSize
        self.n = cellSize
        self.body = []
        self.color = 'red'
        self.dx = 1
        self.dy = 0

    def draw(self, window, isminimap=0, cellSize_snake=cellSize, shift_m=0, shift_n=0):
        if not isminimap:
            pg.draw.rect(window, self.color,
                         ((self.x - self.x_relative) * cellSize_snake, (self.y - self.y_relative) * cellSize_snake,
                          cellSize_snake, cellSize_snake))
            for i in self.body:
                if -13 + self.x < i[0] < 13 + self.x and -13 + self.y < i[1] < 13 + self.y and not isminimap:
                    pg.draw.rect(window, (randrange(0, 255), randrange(0, 255), randrange(0, 255)),
                                 ((i[0] - self.x_relative) * cellSize_snake, (i[1] - self.y_relative) * cellSize_snake,
                                  cellSize_snake,
                                  cellSize_snake))
        else:
            pg.draw.rect(window, self.color,
                         (self.x * cellSize_snake + shift_m * self.m, self.y * cellSize_snake + shift_n * self.n,
                          cellSize_snake,
                          cellSize_snake))
            for i in self.body:
                pg.draw.rect(window, (randrange(0, 255), randrange(0, 255), randrange(0, 255)),
                             ((i[0]) * cellSize_snake + shift_m * self.m, (i[1]) * cellSize_snake + shift_n * self.n,
                              cellSize_snake,
                              cellSize_snake))

    def move(self, food):
        self.body.insert(0, [self.x, self.y])
        self.x += self.dx
        self.y += self.dy
        self.x_relative += self.dx
        self.y_relative += self.dy
        if not self.eat(food):
            self.body.pop()

    def check(self, all_matrix):
        if all_matrix[self.x][self.y] == 1:
            self.death()

        nextX = self.x + self.dx
        nextY = self.y + self.dy
        for i in self.body:
            if (nextX == i[0]) and (nextY == i[1]):
                self.death()

    def changeDir(self):
        key = pg.key.get_pressed()
        temp_x = self.dx
        temp_y = self.dy
        if key[pg.K_w]:
            temp_x = 0
            temp_y = -1
        if key[pg.K_d]:
            temp_x = 1
            temp_y = 0
        if key[pg.K_a]:
            temp_x = -1
            temp_y = 0
        if key[pg.K_s]:
            temp_x = 0
            temp_y = 1

        if self.body:
            if self.body[0] != [self.x + temp_x, self.y + temp_y]:
                self.dx = temp_x
                self.dy = temp_y
        else:
            self.dx = temp_x
            self.dy = temp_y

    def eat(self, food):
        global base_fps, score
        if (self.x == food.x) and (self.y == food.y):
            food.x = randrange(padding + 1, m - padding - 1)
            food.y = randrange(padding + 1, n - padding - 1)
            food.x_relative = food.x - 13
            food.y_relative = food.y - 13
            base_fps += 1
            score += 1
            return 1
        return 0

    def death(self):
        global base_fps
        base_fps = 15
        self.x = 20
        self.y = 15
        self.x_relative = self.x - mn_range
        self.y_relative = self.y - mn_range
        self.body = []
        self.dx = 1
        self.dy = 0


def changeAll(snake, food, all_matrix):
    snake.changeDir()
    snake.check(all_matrix)
    snake.move(food)


def drawAll(window, food, snake):
    window.fill(pg.Color('black'))

    food.draw(window, snake)
    snake.draw(window)

    draw_mini_workspace(snake, window)
    draw_text_log(window, snake)
    draw_minimap(snake, food, window)


def draw_minimap(snake, food, window):
    pg.draw.rect(window, wall_color,
                 ((3 * padding + m_mini) * cellSize, (2 * padding + n_shift_textlog) * cellSize, m * cellSize_minimap,
                  cellSize_minimap))
    pg.draw.rect(window, wall_color,
                 ((3 * padding + m_mini) * cellSize, (2 * padding + n_shift_textlog) * cellSize, cellSize_minimap,
                  n * cellSize_minimap))
    pg.draw.rect(window, wall_color,
                 ((3 * padding + m_mini) * cellSize, (2 * padding + n_shift_textlog) * cellSize + n * cellSize_minimap,
                  m * cellSize_minimap, cellSize_minimap))
    pg.draw.rect(window, wall_color,
                 ((3 * padding + m_mini) * cellSize + m * cellSize_minimap, (2 * padding + n_shift_textlog) * cellSize,
                  cellSize_minimap, (n + 1) * cellSize_minimap))

    snake.draw(window, 1, cellSize_minimap, 3 * padding + m_mini, 2 * padding + n_shift_textlog)
    food.draw(window, snake, 1, cellSize_minimap, 3 * padding + m_mini, 2 * padding + n_shift_textlog)


# оптимизировать нам надо
def draw_mini_workspace(snake, window):
    # левый верхний угол
    if snake.y <= mn_range and snake.x <= mn_range:
        for i in range(m_mini):
            for j in range(n_mini):
                if all_matrix[i][j] == 1 \
                        and -mn_range <= snake.x - i <= mn_range and -mn_range <= snake.y - j <= mn_range:
                    pg.draw.rect(window, wall_color,
                                 ((i - snake.x_relative) * cellSize,
                                  (j - snake.y_relative) * cellSize, cellSize, cellSize))

    # правый верхний угол
    elif snake.y <= mn_range and snake.x >= m - mn_range:
        for i in range(m - m_mini, m):
            for j in range(n_mini):
                if all_matrix[i][j] == 1 \
                        and -mn_range <= snake.x - i <= mn_range and -mn_range <= snake.y - j <= mn_range:
                    pg.draw.rect(window, wall_color,
                                 ((i - snake.x_relative) * cellSize,
                                  (j - snake.y_relative) * cellSize, cellSize, cellSize))

    # левый нижний угол
    elif snake.y >= n - mn_range and snake.x <= mn_range:
        for i in range(m_mini):
            for j in range(n - n_mini, n):
                if all_matrix[i][j] == 1 \
                        and -mn_range <= snake.x - i <= mn_range and -mn_range <= snake.y - j <= mn_range:
                    pg.draw.rect(window, wall_color,
                                 ((i - snake.x_relative) * cellSize,
                                  (j - snake.y_relative) * cellSize, cellSize, cellSize))

    # правый нижий угол
    elif snake.y >= n - mn_range and snake.x >= m - mn_range:
        for i in range(m - m_mini, m):
            for j in range(n - n_mini, n):
                if all_matrix[i][j] == 1 \
                        and -mn_range <= snake.x - i <= mn_range and -mn_range <= snake.y - j <= mn_range:
                    pg.draw.rect(window, wall_color,
                                 ((i - snake.x_relative) * cellSize,
                                  (j - snake.y_relative) * cellSize, cellSize, cellSize))

    # левая стена
    elif snake.x <= mn_range:
        for i in range(m_mini):
            for j in range(snake.y - mn_range, snake.y + mn_range):
                if all_matrix[i][j] == 1 \
                        and -mn_range <= snake.x - i <= mn_range and -mn_range <= snake.y - j <= mn_range:
                    pg.draw.rect(window, wall_color,
                                 ((i - snake.x_relative) * cellSize,
                                  (j - snake.y_relative) * cellSize, cellSize, cellSize))

    # верхняя стена
    elif snake.y <= mn_range:
        for i in range(snake.x - mn_range, snake.x + mn_range):
            for j in range(n_mini):
                if all_matrix[i][j] == 1 \
                        and -mn_range <= snake.x - i <= mn_range and -mn_range <= snake.y - j <= mn_range:
                    pg.draw.rect(window, wall_color,
                                 ((i - snake.x_relative) * cellSize,
                                  (j - snake.y_relative) * cellSize, cellSize, cellSize))

    # правая стена
    elif snake.x >= m - mn_range:
        for i in range(m - m_mini, m):
            for j in range(snake.y - mn_range, snake.y + mn_range):
                if all_matrix[i][j] == 1 \
                        and -mn_range <= snake.x - i <= mn_range and -mn_range <= snake.y - j <= mn_range:
                    pg.draw.rect(window, wall_color,
                                 ((i - snake.x_relative) * cellSize,
                                  (j - snake.y_relative) * cellSize, cellSize, cellSize))

    # нижняя стена
    elif snake.y >= n - mn_range:
        for i in range(snake.x - mn_range, snake.x + mn_range):
            for j in range(n - n_mini, n):
                if all_matrix[i][j] == 1 \
                        and -mn_range <= snake.x - i <= mn_range and -mn_range <= snake.y - j <= mn_range:
                    pg.draw.rect(window, wall_color,
                                 ((i - snake.x_relative) * cellSize,
                                  (j - snake.y_relative) * cellSize, cellSize, cellSize))

    else:
        for i in range(snake.x - mn_range, snake.x + mn_range):
            for j in range(snake.y - mn_range, snake.y + mn_range):
                if all_matrix[i][j] == 1 \
                        and -mn_range <= snake.x - i <= mn_range and -mn_range <= snake.y - j <= mn_range:
                    pg.draw.rect(window, wall_color,
                                 ((i - snake.x_relative) * cellSize,
                                  (j - snake.y_relative) * cellSize, cellSize, cellSize))


def draw_text_log(window, snake):
    global score
    pg.draw.rect(window, wall_color,
                 ((3 * padding + m_mini) * cellSize, padding * cellSize, m * cellSize_minimap,
                  cellSize_minimap))
    pg.draw.rect(window, wall_color,
                 ((3 * padding + m_mini) * cellSize, padding * cellSize, cellSize_minimap,
                  3 * n * cellSize_minimap))
    pg.draw.rect(window, wall_color,
                 ((3 * padding + m_mini) * cellSize, padding * cellSize + 3 * n * cellSize_minimap,
                  m * cellSize_minimap, cellSize_minimap))
    pg.draw.rect(window, wall_color,
                 ((3 * padding + m_mini) * cellSize + m * cellSize_minimap, padding * cellSize,
                  cellSize_minimap, (3 * n + 1) * cellSize_minimap))

    myfont = pg.font.SysFont("monospace", 25)
    text1 = myfont.render("Score: {}".format(score), True, (255, 255, 255))
    text2 = myfont.render("Speed: {}".format(fps), True, (255, 255, 255))
    text3 = myfont.render("Snake({}, {})".format(snake.x, snake.y), True, (255, 255, 255))
    window.blit(text1, (1020, 80))
    window.blit(text2, (1020, 120))
    window.blit(text3, (990, 160))


def menu_buttons():
    global finish, pause, fps
    key = pg.key.get_pressed()
    if key[pg.K_p]:
        pause = 1
    if key[pg.K_c]:
        pause = 0
    if key[pg.K_ESCAPE]:
        finish = 1
    if key[pg.K_LSHIFT]:
        fps *= 2
    if key[pg.K_LALT]:
        fps = int(fps / 2)


def pause_game(window):
    menu_buttons()
    myfont = pg.font.SysFont("monospace", 50)
    text1 = myfont.render("Pause!", True, (randrange(0, 255), randrange(0, 255), randrange(0, 255)))
    window.blit(text1, (500, 400))
    pg.display.update()
    pg.time.delay(50)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            exit()


def continue_dame(snake, food, window, clock, all_matrix):
    global fps, base_fps
    menu_buttons()
    changeAll(snake, food, all_matrix)
    drawAll(window, food, snake)

    pg.display.update()
    clock.tick(fps)
    fps = base_fps
    for event in pg.event.get():
        if event.type == pg.QUIT:
            exit()


def main():
    pg.init()
    create_matrix()
    window = pg.display.set_mode([m_window * cellSize, n_window * cellSize])
    x_food = randrange(padding + 1, m - padding - 1)
    y_food = randrange(padding + 1, n - padding - 1)
    food = Food(x_food, y_food, x_food - mn_range, y_food - mn_range)
    snake = Snake(50, 50, 50 - mn_range, 50 - mn_range)
    clock = pg.time.Clock()

    while not finish:
        if pause:
            pause_game(window)
        else:
            continue_dame(snake, food, window, clock, all_matrix)
    pg.quit()


main()
