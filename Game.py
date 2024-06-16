import pyxel

TRANSPARENT_COLOR = 2
SCROLL_BORDER_X = 80
COLLIDING_TILE_X=8
TILE_SPAWN1 = (1,0)
TILE_SPAWN2 = (2,0)
TILE_SPAWN3 = (3,0)
PLAYER_SPEED=2
PLAYER_JUMP_SPEED=6
TILEMAP_WIDTH=55
TILEMAP_HEIGHT=15
FPS=25

scroll=None
mode=-1
player = None
enemies = []


def get_tile(tile_x, tile_y):
    tilemap=pyxel.tilemap
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

def is_on_display(x):
    global scroll
    if x<=scroll+pyxel.width//2 and x>=scroll-pyxel.width//2:
        return True
    else:
        return False


def spawn_enemies():
    for x in range(TILEMAP_WIDTH + 1):
        for y in range(TILEMAP_HEIGHT+1):
            tile = get_tile(x, y)
            if tile == TILE_SPAWN1:
                enemies.append(Enemy1(x * 8, y * 8))
            # elif tile == TILE_SPAWN2:
            #     enemies.append(Enemy2(x * 8, y * 8))
            # elif tile == TILE_SPAWN3:
            #     enemies.append(Enemy3(x * 8, y * 8))


def cleanup_entities(entities):
    for i in range(len(entities) - 1, -1, -1):
        if not entities[i].is_alive:
            del entities[i]
def btn_left():
    if pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTX)*mode>=20000:
        return True;
    if mode == 1:
        return pyxel.btn(pyxel.KEY_LEFT)
    else: 
        return pyxel.btn(pyxel.KEY_RIGHT)

def btn_right():
    if pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTX)*mode<=-20000:
        return True;
    if mode == 1:
        return pyxel.btn(pyxel.KEY_RIGHT)
    else:
        return pyxel.btn(pyxel.KEY_LEFT)


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.direction = 1
        self.is_falling = False

    def update(self):
        global mode # 1 for default mode / -1 for reversed mode
        last_y = self.y
        if btn_right():
            self.dx = PLAYER_SPEED
            self.direction = 1
        if btn_left():
            self.dx = -PLAYER_SPEED
            self.direction = -1
        self.dy = min(self.dy + 1, 3)
        if (pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTY)*mode<=-20000) and is_on_floor(self.x,self.y) :
            self.dy = -PLAYER_JUMP_SPEED
        self.x, self.y = push_back(self.x, self.y, self.dx, self.dy)
        if self.y < 0:
            self.y = 0
        self.dx = int(self.dx * 0.8)
        self.is_falling = self.y > last_y

        
        if self.y >= pyxel.height:
            game_over()

    def draw(self):
        if btn_left() ^ btn_right() and not self.is_falling:
            u =  (pyxel.frame_count // 6 % 2) * 8
        else:
            u = 0
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
        move_turn=(pyxel.frame_count//FPS)%4
        if move_turn==0 or move_turn==3:
            self.direction=-1
        else:
            self.direction=1
        self.x, self.y = push_back(self.x, self.y, self.dx, self.dy)

    def draw(self):
        u = pyxel.frame_count // 4 % 2 * 8
        w = 8 if self.direction > 0 else -8
        
        if is_on_display(self.x):
            pyxel.blt(self.x, self.y, 0, u, 40, w, 8)


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
        pyxel.init(128, 128, title="Carma Junino" , fps=FPS)
        pyxel.load("carmaJunino.pyxres")
        global scroll
        scroll=pyxel.width//2

        # Change enemy spawn tiles invisible
        # pyxel.images[0].rect(1, 0, 24, 8, TRANSPARENT_COLOR)

        global player
        player = Player(0, 0)
        spawn_enemies()
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
            # if enemy.x < scroll_x - 8 or enemy.x > scroll_x + 160 or enemy.y > 160:
            #     enemy.is_alive = False
        cleanup_entities(enemies)

    def draw(self):
        pyxel.cls(0)

        # Draw level
        if player!=None:
            scroll=max(min(TILEMAP_WIDTH*8-pyxel.width,player.x-pyxel.width//2),0)
        else:
            scroll=pyxel.width//2
        pyxel.camera()
        pyxel.bltm(0, 0, 0, scroll, 0, pyxel.width, pyxel.height, TRANSPARENT_COLOR)
        # pyxel.bltm(0, 0, 0, scroll, 0, 128, 128, TRANSPARENT_COLOR)

        # Draw characters
        pyxel.camera(scroll, 0)
        player.draw()
        for enemy in enemies:
            enemy.draw()


def game_over():
    global scroll, enemies
    scroll = pyxel.width//2
    player.x = 0
    player.y = 0
    player.dx = 0
    player.dy = 0
    enemies = []
    spawn_enemies()
    # pyxel.play(3, 9)


App()

