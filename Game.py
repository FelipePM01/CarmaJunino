import pyxel

TILE_SIZE=8
transparent_color = 0
COLLIDING_TILE_X=TILE_SIZE
TILE_SPAWN1 = (1,0)
TILE_SPAWN2 = (2,0)
TILE_SPAWN3 = (3,0)
PLAYER_SPEED=2
PLAYER_JUMP_SPEED=6
TILEMAP_WIDTH=55
TILEMAP_HEIGHT=15
FPS=25
SHOT_FRAME_INTERVAL=25
BULLET_SPEED=4
DEBUG  = False

in_hell = False
image_src = 0
scroll=None
mode=1
player = None
enemies = []
killed_enemies = []
bullets=[]

class rect:
    x: int
    y: int 
    w: int 
    h: int 
    def __init__(self, x: int, y: int, w: int, h: int):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
def get_tile(tile_x, tile_y):
    tilemap=pyxel.tilemap
    return pyxel.tilemaps[0].pget(tile_x, tile_y)

def is_colliding(x,y,k=0, w=8,h=8):

    xmin = x // TILE_SIZE
    ymin = y // TILE_SIZE
    xmax = pyxel.ceil((x+w)/TILE_SIZE)
    ymax = pyxel.ceil((y+h)/TILE_SIZE)
    for i in range(xmin, xmax):
        for j in range(ymin, ymax):
            if get_tile(i, j)[0] >= COLLIDING_TILE_X:
                return True
    return False
def go_to_hell():
    global image_src 
    global in_hell
    global enemies
    global mode
    global killed_enemies
    image_src = 1
    in_hell = True
    enemies =  []
    mode = -1
    for ke in killed_enemies:
          enemies.append(ke)
          ke.is_alive = True
    killed_enemies = []
def push_back(x, y, dx, dy):
    abs_dx = abs(dx)
    abs_dy = abs(dy)
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
    tile = get_tile(x // TILE_SIZE, y // TILE_SIZE)
    return tile[0] >= COLLIDING_TILE_X

def is_on_floor(x,y):
    x1 = int(x // TILE_SIZE)
    y1 = int((y+TILE_SIZE) // TILE_SIZE)
    x2 = int((x + 7) // TILE_SIZE)
    y2 = int((y + 9) // TILE_SIZE)
    for yi in range(y1,y2+1):
        for xi in range(x1, x2 + 1):
                if get_tile(xi, yi)[0]>=COLLIDING_TILE_X:
                    return True

def is_on_display(x):
    global scroll
    if  -TILE_SIZE <= x -scroll <= pyxel.width:
        return True
    else:
        return False


def spawn_enemies():
    global player
    global enemies
    for x in range(TILEMAP_WIDTH + 1):
        for y in range(TILEMAP_HEIGHT+1):
            tile = get_tile(x, y)
            if tile == TILE_SPAWN1:
                enemies.append(Enemy1(x * TILE_SIZE, y * TILE_SIZE))
            elif tile == TILE_SPAWN2:
                enemies.append(Enemy2(x * TILE_SIZE, y * TILE_SIZE))
            elif tile == TILE_SPAWN3:
               player=Player(x * TILE_SIZE, y * TILE_SIZE)


def cleanup_entities(entities):
    for i in range(len(entities) - 1, -1, -1):
        if not entities[i].is_alive:
            entities.remove(entities[i])
def btn_left():
    if pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTX)*mode<=-20000:
        return True
    
    if mode == 1:
        return pyxel.btn(pyxel.KEY_LEFT)
    else: 
        return pyxel.btn(pyxel.KEY_RIGHT)

def btn_right():
    if pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTX)*mode>=20000:
        return True
    if mode == 1:
        return pyxel.btn(pyxel.KEY_RIGHT)
    else:
        return pyxel.btn(pyxel.KEY_LEFT)
def colision_area_tiles(r):
    
    xmin = r.x // TILE_SIZE
    ymin = r.y // TILE_SIZE
    xmax = pyxel.ceil((r.x+r.w)/TILE_SIZE)
    ymax = pyxel.ceil((r.y+r.h)/TILE_SIZE)
    arr = []
    for i in range(xmin, xmax):
        for j in range(ymin, ymax): 
            arr.append([i,j])
    return arr
def btn_up():
    if in_hell:
        if pyxel.btnp(pyxel.KEY_DOWN):
            return True
    else:
        if pyxel.btnp(pyxel.KEY_UP):
            return True
    if pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTY)*mode<=-20000:
        return True
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.direction = 1
        self.is_falling = False
        self.last_shot=-200
    def get_colision_area(self):
        return rect(self.x+2, self.y+1, 4, 7)
        
    def update(self):
        global mode # 1 for default mode / -1 for reversed mode
        global bullets

        last_y = self.y
        if btn_right():
            self.dx = PLAYER_SPEED
            self.direction = 1
        if btn_left():
            self.dx = -PLAYER_SPEED
            self.direction = -1
        self.dy = min(self.dy + 1, 3)
        if btn_up() and is_on_floor(self.x,self.y) :
            self.dy = -PLAYER_JUMP_SPEED
        self.x, self.y = push_back(self.x, self.y, self.dx, self.dy)
        if self.y < 0:
            self.y = 0
        self.dx = int(self.dx * 0.8)
        self.is_falling = self.y > last_y
        if (pyxel.btnr(pyxel.KEY_SPACE) or pyxel.btnr(pyxel.GAMEPAD1_BUTTON_A)) and self.last_shot+SHOT_FRAME_INTERVAL<pyxel.frame_count and mode==1:
            if self.direction==1:
                bullets.append(PlayerBullet(self.x+TILE_SIZE//2,self.y,1,0))
            else:
                bullets.append(PlayerBullet(self.x,self.y,-1,0))
            self.last_shot=pyxel.frame_count
        
        if self.y >= pyxel.height:
            game_over()

    def draw(self):
        if btn_left() ^ btn_right() and not self.is_falling:
            u =  (pyxel.frame_count // 6 % 2) * TILE_SIZE
        else:
            u = 0
        w = TILE_SIZE if self.direction > 0 else -TILE_SIZE 

        pyxel.blt(self.x, self.y, image_src, u, 48, w, TILE_SIZE, transparent_color)
        if DEBUG:
            r =  player.get_colision_area()
 

            pyxel.rect(r.x, r.y, r.w, r.h, 3)
            pyxel.line(r.x, r.y, r.x+self.dx, r.y+self.dy, 8)


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
        u = pyxel.frame_count // 4 % 2 * TILE_SIZE
        w = TILE_SIZE if self.direction > 0 else -TILE_SIZE
        
        if is_on_display(self.x):
            pyxel.blt(self.x, self.y, image_src, u, 40, w, TILE_SIZE, transparent_color)


class Enemy2:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.direction = -1
        self.is_alive = True
        

    def update(self):
        self.dx = self.direction*2
        self.dy = min(self.dy + 1, 3)
        move_turn=(pyxel.frame_count//FPS)%4
        if move_turn==0 or move_turn==3:
            self.direction=-1
        else:
            self.direction=1
        self.x, self.y = push_back(self.x, self.y, self.dx, self.dy)

    def draw(self):
        u = pyxel.frame_count // 4 % 2 * TILE_SIZE
        w = TILE_SIZE if self.direction > 0 else -TILE_SIZE
        
        if is_on_display(self.x):
            pyxel.blt(self.x, self.y, image_src, u, 40, w, TILE_SIZE, transparent_color)




class PlayerBullet:
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.is_alive = True

    def update(self):
        if self.is_alive and not is_colliding(self.x,self.y):
            self.x += self.dx*BULLET_SPEED
            self.y += self.dy*BULLET_SPEED
        elif is_colliding(self.x,self.y) and self.is_alive:
            self.destroy()

        

    def draw(self):
        global transparent_color
        u=None
        if self.is_alive:
            u=0
        else:
            frame=(pyxel.frame_count-self.start_boom) // 2 % 4
            if frame!=3:
                u = frame * TILE_SIZE + 8 
            else:
                bullets.remove(self)
                return

        pyxel.blt(self.x, self.y, 0, u, 64, TILE_SIZE, TILE_SIZE, transparent_color)
    def destroy(self):
        self.is_alive=False
        self.start_boom=pyxel.frame_count
        


class App:
    def __init__(self):
        pyxel.init(128, 128, title="Carma Junino" , fps=FPS)
        pyxel.load("carmaJunino.pyxres")
        global scroll
        scroll=pyxel.width//2

        #Change enemy spawn tiles invisible
        pyxel.images[0].rect(TILE_SIZE, 0, 24, TILE_SIZE, transparent_color)

        spawn_enemies()
        # pyxel.playm(0, loop=True)
        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btn(pyxel.KEY_Q):
            pyxel.quit()

        player.update()
        del_list=[]
        for enemy in range(len(enemies)):
            if abs(player.x - enemies[enemy].x) < 6 and abs(player.y - enemies[enemy].y) < 6:
                game_over()
                return
            
            for bullet in bullets:
                if abs(bullet.x - enemies[enemy].x) < 6 and abs(bullet.y - enemies[enemy].y) < 6:
                    bullets.remove(bullet)
                    del_list.append(enemies[enemy])
        
        for e in del_list:
            enemies.remove(e)
            killed_enemies.append(e)
            
        for enemy in enemies:
            enemy.update()
            # if enemy.x < scroll_x - TILE_SIZE or enemy.x > scroll_x + 160 or enemy.y > 160:
            #     enemy.is_alive = False
        
        for bullet in bullets:
            bullet.update()
        cleanup_entities(enemies)

    def draw(self):
        global scroll
        global transparent_color
        pyxel.cls(0)
        
        pyxel.blt(scroll, 64, 0, image_src, TILE_SIZE, TILE_SIZE, TILE_SIZE, transparent_color)
        # Draw level
        if player!=None:
            scroll=max(min(player.x-pyxel.width//2, TILEMAP_WIDTH*TILE_SIZE-pyxel.width),0)
        else:
            scroll=pyxel.width//2
        pyxel.camera()
        if mode==1:
            pyxel.bltm(0,0,2,0,0,pyxel.width,pyxel.height)
        pyxel.bltm(0, 0,image_src, scroll, 0, pyxel.width, pyxel.height, transparent_color)
        if DEBUG:
            for i in range(0,32):
                for j in range(0,32):
                    if get_tile(scroll//8+i, j)[0]>=COLLIDING_TILE_X:
                        pyxel.rect(i*TILE_SIZE-scroll%8, j*TILE_SIZE, TILE_SIZE, TILE_SIZE, 1)
                        pyxel.rect(i*TILE_SIZE-scroll%8+1, j*TILE_SIZE+1, TILE_SIZE-2, TILE_SIZE-2, 2)

        # Draw characters
        pyxel.camera(scroll, 0)
        player.draw()
        for enemy in enemies:
            enemy.draw()
        for bullet in bullets:
            bullet.draw()
        if pyxel.btn(pyxel.KEY_L) and not in_hell:
            go_to_hell()
def game_over():
    global scroll, enemies, in_hell, image_src ,mode
    scroll = pyxel.width//2
    player.x = 0
    player.y = 0
    player.dx = 0
    player.dy = 0
    enemies = []
    in_hell = False
    image_src = 0 
    mode=1
    spawn_enemies()
    # pyxel.play(3, 9)


App()

