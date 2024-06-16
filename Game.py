import pyxel

TRANSPARENT_COLOR = 2
SCROLL_BORDER_X = 80
COLLIDING_TILE_X=8
TILE_SPAWN1 = (0, 1)
TILE_SPAWN2 = (1, 1)
TILE_SPAWN3 = (2, 1)
PLAYER_SPEED=2
PLAYER_JUMP_SPEED=6

scroll_x_min = 0
mode=1
player = None
enemies = []


def get_tile(tile_x, tile_y):
    return pyxel.tilemaps[0].pget(tile_x, tile_y)


def is_colliding(x, y, is_falling):
    x1 = int(x // 8)
    y1 = int(y // 8)
    x2 = int((x + 7) // 8)
    y2 = int((y + 7) // 8)
    for yi in range(y1, y2 + 1):
        for xi in range(x1, x2 + 1):
            if get_tile(xi, yi)[0] >= COLLIDING_TILE_X:
                return True
    if is_falling and y % 8 == 1:
        for xi in range(x1, x2 + 1):
            if get_tile(xi, y1 + 1)[0] == COLLIDING_TILE_X:
                return True
    return False


def push_back(x, y, dx, dy):
    abs_dx = abs(dx)
    abs_dy = abs(dy)
    if abs_dx > abs_dy:
        for _ in range(pyxel.ceil(abs_dx)):
            step = max(-1, min(1, dx))
            if is_colliding(x + step, y, dy > 0):
                break
            x += step
            dx -= step
        for _ in range(pyxel.ceil(abs_dy)):
            step = max(-1, min(1, dy))
            if is_colliding(x, y + step, dy > 0):
                break
            y += step
            dy -= step
    else:
        for _ in range(pyxel.ceil(abs_dy)):
            step = max(-1, min(1, dy))
            if is_colliding(x, y + step, dy > 0):
                break
            y += step
            dy -= step
        for _ in range(pyxel.ceil(abs_dx)):
            step = max(-1, min(1, dx))
            if is_colliding(x + step, y, dy > 0):
                break
            x += step
            dx -= step
    return x, y


def is_wall(x, y):
    tile = get_tile(x // 8, y // 8)
    return tile[0] >= COLLIDING_TILE_X

def is_on_floor(x,y):
    x1 = int(x // 8)
    y1 = int((y+8) // 8)
    x2 = int((x + 7) // 8)
    y2 = int((y + 15) // 8)
    for yi in range(y1,y2+1):
        for xi in range(x1, x2 + 1):
                if get_tile(xi, yi)[0]>=COLLIDING_TILE_X:
                    return True


def spawn_enemy(left_x, right_x):
    left_x = pyxel.ceil(left_x / 8)
    right_x = pyxel.floor(right_x / 8)
    for x in range(left_x, right_x + 1):
        for y in range(16):
            tile = get_tile(x, y)
            if tile == TILE_SPAWN1:
                enemies.append(Enemy1(x * 8, y * 8))
            elif tile == TILE_SPAWN2:
                enemies.append(Enemy2(x * 8, y * 8))
            elif tile == TILE_SPAWN3:
                enemies.append(Enemy3(x * 8, y * 8))


def cleanup_entities(entities):
    for i in range(len(entities) - 1, -1, -1):
        if not entities[i].is_alive:
            del entities[i]


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.direction = 1
        self.is_falling = False

    def update(self):
        global scroll_x_min
        global mode # 1 for default mode / -1 for reversed mode
        last_y = self.y
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTX)*mode>=20000:
            self.dx = PLAYER_SPEED
            self.direction = 1
        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTX)*mode<=-20000:
            self.dx = -PLAYER_SPEED
            self.direction = -1
        self.dy = min(self.dy + 1, 3)
        if (pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTY)*mode<=-20000) and is_on_floor(self.x,self.y) :
            self.dy = -PLAYER_JUMP_SPEED
        self.x, self.y = push_back(self.x, self.y, self.dx, self.dy)
        if self.x < scroll_x_min:
            self.x = scroll_x_min
        if self.y < 0:
            self.y = 0
        self.dx = int(self.dx * 0.8)
        self.is_falling = self.y > last_y

        if self.x > scroll_x_min + SCROLL_BORDER_X:
            last_scroll_x_min = scroll_x_min
            scroll_x_min = min(self.x - SCROLL_BORDER_X, 240 * 8)
            # spawn_enemy(last_scroll_x_min + 128, scroll_x_min + 127)
        if self.y >= pyxel.height:
            game_over()

    def draw(self):
        u = (0 if self.is_falling else pyxel.frame_count // 3 % 2) * 8
        w = 8 if self.direction > 0 else -8
        pyxel.blt(self.x, self.y, 0, u, 48, w, 8, TRANSPARENT_COLOR)


class Enemy1:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.direction = -1
        self.is_alive = True

    def update(self):
        self.dx = self.direction
        self.dy = min(self.dy + 1, 3)
        if self.direction < 0 and is_wall(self.x - 1, self.y + 4):
            self.direction = 1
        elif self.direction > 0 and is_wall(self.x + 8, self.y + 4):
            self.direction = -1
        self.x, self.y = push_back(self.x, self.y, self.dx, self.dy)

    def draw(self):
        u = pyxel.frame_count // 4 % 2 * 8
        w = 8 if self.direction > 0 else -8
        pyxel.blt(self.x, self.y, 0, u, 24, w, 8, TRANSPARENT_COLOR)


class Enemy2:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.direction = 1
        self.is_alive = True

    def update(self):
        self.dx = self.direction
        self.dy = min(self.dy + 1, 3)
        if is_wall(self.x, self.y + 8) or is_wall(self.x + 7, self.y + 8):
            if self.direction < 0 and (
                is_wall(self.x - 1, self.y + 4) or not is_wall(self.x - 1, self.y + 8)
            ):
                self.direction = 1
            elif self.direction > 0 and (
                is_wall(self.x + 8, self.y + 4) or not is_wall(self.x + 7, self.y + 8)
            ):
                self.direction = -1
        self.x, self.y = push_back(self.x, self.y, self.dx, self.dy)

    def draw(self):
        u = pyxel.frame_count // 4 % 2 * 8 + 16
        w = 8 if self.direction > 0 else -8
        pyxel.blt(self.x, self.y, 0, u, 24, w, 8, TRANSPARENT_COLOR)


class Enemy3:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.time_to_fire = 0
        self.is_alive = True

    def update(self):
        self.time_to_fire -= 1
        if self.time_to_fire <= 0:
            dx = player.x - self.x
            dy = player.y - self.y
            sq_dist = dx * dx + dy * dy
            if sq_dist < 60**2:
                dist = pyxel.sqrt(sq_dist)
                enemies.append(Enemy3Bullet(self.x, self.y, dx / dist, dy / dist))
                self.time_to_fire = 60

    def draw(self):
        u = pyxel.frame_count // 8 % 2 * 8
        pyxel.blt(self.x, self.y, 0, u, 32, 8, 8, TRANSPARENT_COLOR)


class Enemy3Bullet:
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.is_alive = True

    def update(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self):
        u = pyxel.frame_count // 2 % 2 * 8 + 16
        pyxel.blt(self.x, self.y, 0, u, 32, 8, 8, TRANSPARENT_COLOR)


class App:
    def __init__(self):
        pyxel.init(128, 128, title="Carma Junino")
        pyxel.load("carmaJunino.pyxres")

        # Change enemy spawn tiles invisible
        pyxel.images[0].rect(0, 8, 24, 8, TRANSPARENT_COLOR)

        global player
        player = Player(0, 0)
        # spawn_enemy(0, 127)
        # pyxel.playm(0, loop=True)
        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btn(pyxel.KEY_Q):
            pyxel.quit()

        player.update()
        for enemy in enemies:
            if abs(player.x - enemy.x) < 6 and abs(player.y - enemy.y) < 6:
                game_over()
                return
            enemy.update()
            if enemy.x < scroll_x_min - 8 or enemy.x > scroll_x_min + 160 or enemy.y > 160:
                enemy.is_alive = False
        cleanup_entities(enemies)

    def draw(self):
        pyxel.cls(0)

        # Draw level
        pyxel.camera()
        pyxel.bltm(0, 0, 0, (scroll_x_min // 4) % 128, 128, 128, 128)
        pyxel.bltm(0, 0, 0, scroll_x_min, 0, 128, 128, TRANSPARENT_COLOR)

        # Draw characters
        pyxel.camera(scroll_x_min, 0)
        player.draw()
        for enemy in enemies:
            enemy.draw()


def game_over():
    global scroll_x_min, enemies
    scroll_x_min = 0
    player.x = 0
    player.y = 0
    player.dx = 0
    player.dy = 0
    enemies = []
    # spawn_enemy(0, 127)
    # pyxel.play(3, 9)


App()

