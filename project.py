from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

import math
import random
import time


WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
fovY = 75

GRID_LENGTH = 600
GRID_CELLS = 20
TILE_SIZE = (2 * GRID_LENGTH) / GRID_CELLS


camera_pos = (0, 500, 500)
camera_angle = 0.0
camera_height = 560.0
camera_distance = 850.0
camera_mode = "third_person"

CAMERA_ROTATION_STEP = 5.0
CAMERA_HEIGHT_STEP = 20.0
MIN_CAMERA_HEIGHT = 150.0
MAX_CAMERA_HEIGHT = 900.0


player_x = 0.0
player_y = 0.0
player_angle = 90.0
gun_angle = 90.0

player_speed = 12.0
turn_step = 5.0
PLAYER_SCALE = 1.4
PLAYER_COLLISION_RADIUS = 25.0

player_life = 6
MAX_LIFE = 6
game_score = 0

weapon_level = 1
shield_count = 0
power_boost_end = 0.0
boost_ready = False


game_mode = "stage1"

STAGE1_SCORE_TARGET = 10
WAVE_SCORE_STEP = 10

missed_bullets_since_bonus = 0
BONUS_MISS_TARGET = 20
BONUS_LIFE_TRIGGER = 4
bonus_life_trigger_armed = True

bonus_origin = "stage1"
bonus_started_at = 0.0
BONUS_DURATION = 30.0


bullets = []

BULLET_SPEED = 430.0
BOOSTED_BULLET_SPEED = 600.0
BULLET_SIZE = 6.0
BULLET_START_DISTANCE = 46.0 * PLAYER_SCALE + BULLET_SIZE / 2.0
BULLET_Z = 31.0 * PLAYER_SCALE
SIDE_FIRE_COOLDOWN = 0.30
last_side_shot_time = 0.0


monsters = []
MONSTER_COUNT = 5

MONSTER_NORMAL = 0
MONSTER_FAST = 1
MONSTER_HEAVY = 2
MONSTER_BOSS = 3

NORMAL_MONSTER_SPEED = 34.0
FAST_MONSTER_SPEED = 52.0
HEAVY_MONSTER_SPEED = 24.0
BOSS_MONSTER_SPEED = 18.0

MONSTER_PULSE_AMOUNT = 3.0
MONSTER_PULSE_SPEED = 3.5


STAGE2_FLOOR_Z = [0.0, 160.0, 320.0]
STAGE2_STAIR_X = [410.0, -410.0]
STAGE2_HALF_WIDTH = 470.0
STAGE2_MOVE_STEP = 16.0
STAIR_TRIGGER_DISTANCE = 65.0
STAIR_TRAVEL_TIME = 0.60
STAGE2_SPEED_MULTIPLIERS = [0.95, 1.05, 1.15]
STAGE2_NORMAL_HEALTH = 2
STAGE2_FAST_HEALTH = 2
STAGE2_HEAVY_HEALTH = 5

stage2_floor_enemies = [[], [], []]
active_floor = 0
stage2_player_x = -360.0
stage2_facing = 1

stair_transition = None


BOSS_MAX_HEALTH = 36
boss_health = BOSS_MAX_HEALTH
boss_master = None
boss_minions = []
BOSS_PLAYER_START_X = -400.0
BOSS_PLAYER_START_Y = -350.0
BOSS_PLAYER_START_ANGLE = 45.0
BOSS_MASTER_START_X = 330.0
BOSS_MASTER_START_Y = 300.0
boss_player_x = BOSS_PLAYER_START_X
boss_player_y = BOSS_PLAYER_START_Y
boss_aim_angle = BOSS_PLAYER_START_ANGLE
BOSS_ARENA_HALF_WIDTH = 600.0
BOSS_ARENA_HALF_DEPTH = 600.0
BOSS_ARENA_MARGIN = 55.0
BOSS_ARENA_TILE_COUNT = 20
BOSS_NORMAL_MINION_HEALTH = 3
BOSS_FAST_MINION_HEALTH = 2
BOSS_HEAVY_MINION_HEALTH = 6
BOSS_MINION_CYCLE = (MONSTER_NORMAL, MONSTER_FAST, MONSTER_HEAVY)
boss_minion_cycle_index = 0

boss_projectiles = []
last_boss_shot_time = 0.0
last_boss_projectile_hit_time = -100.0
BOSS_SHOT_INTERVAL = 1.80
BOSS_BULLET_SPEED = 200.0
BOSS_PROJECTILE_RADIUS = 9.0
BOSS_PROJECTILE_DAMAGE = 2
BOSS_PROJECTILE_HIT_COOLDOWN = 0.75


runner_lane = 1
RUNNER_LANES = [-120.0, 0.0, 120.0]
RUNNER_PLAYER_Y = -40.0
RUNNER_OBJECT_SPEED = 225.0

bonus_objects = []
last_bonus_spawn = 0.0
BONUS_SPAWN_DELAY = 0.75

ITEM_LIFE = 0
ITEM_WEAPON = 1
ITEM_SHIELD = 2
ITEM_BOOST = 3
OBSTACLE_ROCK = 4
OBSTACLE_LOG = 5


tree_positions = [
    (-530, -500, 46), (-520, -330, 40), (-535, -140, 50),
    (-525, 80, 44), (-535, 280, 52), (-520, 470, 42),
    (530, -470, 45), (520, -270, 52), (535, -70, 41),
    (520, 150, 48), (535, 350, 43), (520, 500, 50),
    (-420, 520, 45), (-230, 530, 50), (-20, 525, 42),
    (190, 530, 48), (390, 520, 44),
    (-430, -520, 48), (-220, -530, 43), (0, -525, 50),
    (220, -530, 45), (430, -520, 49),
]

jungle_rocks = [
    (-370, -270, 25), (-300, 340, 22), (-150, -390, 28),
    (180, 400, 24), (330, -300, 30), (390, 250, 21),
]

temple_blocks = [
    (-260, 40, 50), (260, 110, 60), (-260, 250, 42),
    (260, 340, 55), (-260, 490, 62), (260, 575, 45),
]


last_update_time = time.time()


def normalize_angle(angle):
    return angle % 360.0


def get_distance(x1, y1, x2, y2):
    dx = x1 - x2
    dy = y1 - y2
    return math.sqrt(dx * dx + dy * dy)


def get_wave():
    return 1 + int(game_score / WAVE_SCORE_STEP)


def boost_is_active(current_time):
    return current_time < power_boost_end


def monster_score(monster_type):
    if monster_type == MONSTER_FAST:
        return 2
    if monster_type == MONSTER_HEAVY:
        return 3
    return 1


def origin_label():
    if bonus_origin == "stage1":
        return "STAGE 1"
    if bonus_origin == "stage2":
        return "STAGE 2 - FLOOR " + str(active_floor + 1)
    if bonus_origin == "boss":
        return "BOSS ARENA"
    return bonus_origin.upper()


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18, color=(1, 1, 1)):
    glColor3f(color[0], color[1], color[2])

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)

    for ch in text:
        glutBitmapCharacter(font, ord(ch))

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_box(x, y, z, size_x, size_y, size_z, color):
    glColor3f(color[0], color[1], color[2])
    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(size_x, size_y, size_z)
    glutSolidCube(1)
    glPopMatrix()


def draw_jungle_ground():
    for i in range(GRID_CELLS):
        for j in range(GRID_CELLS):
            x0 = -GRID_LENGTH + i * TILE_SIZE
            y0 = -GRID_LENGTH + j * TILE_SIZE
            x1 = x0 + TILE_SIZE
            y1 = y0 + TILE_SIZE

            if (i + j) % 2 == 0:
                glColor3f(0.18, 0.34, 0.07)
            else:
                glColor3f(0.34, 0.27, 0.07)

            glBegin(GL_QUADS)
            glVertex3f(x0, y0, 0)
            glVertex3f(x1, y0, 0)
            glVertex3f(x1, y1, 0)
            glVertex3f(x0, y1, 0)
            glEnd()

    for path_index in range(11):
        path_y = -520.0 + path_index * 104.0
        path_x = -18.0 if path_index % 2 == 0 else 18.0
        if path_index % 3 == 0:
            stone_color = (0.52, 0.49, 0.34)
        else:
            stone_color = (0.42, 0.41, 0.30)
        draw_box(path_x, path_y, 2.0, 125, 72, 4, stone_color)


def draw_jungle_ruins():
    draw_box(0, GRID_LENGTH + 35, 185,
             1320, 38, 430, (0.035, 0.13, 0.04))

    for canopy_x in (-520, -350, -175, 0, 175, 350, 520):
        glColor3f(0.05, 0.36, 0.07)
        glPushMatrix()
        glTranslatef(canopy_x, GRID_LENGTH + 5, 330)
        glScalef(1.8, 0.75, 0.85)
        gluSphere(gluNewQuadric(), 55, 10, 10)
        glPopMatrix()

    for ruin_x in (-455.0, 455.0):
        draw_box(ruin_x, 250, 70, 42, 58, 140, (0.42, 0.40, 0.29))
        draw_box(ruin_x, 400, 52, 48, 58, 104, (0.34, 0.34, 0.27))
        draw_box(ruin_x, 325, 132, 48, 205, 32, (0.46, 0.43, 0.31))

        glColor3f(0.08, 0.48, 0.10)
        glPushMatrix()
        glTranslatef(ruin_x, 320, 158)
        glScalef(0.75, 1.35, 0.60)
        gluSphere(gluNewQuadric(), 34, 9, 9)
        glPopMatrix()

    for column_x, column_y, column_height in (
        (-360, -180, 90), (360, -80, 120),
        (-390, 80, 115), (385, 155, 82),
    ):
        draw_box(column_x, column_y, column_height / 2.0,
                 34, 34, column_height, (0.38, 0.37, 0.29))
        draw_box(column_x, column_y, column_height + 8,
                 48, 48, 16, (0.48, 0.45, 0.32))


def draw_jungle_boundaries():
    wall_height = 55.0
    wall_thickness = 12.0
    wall_length = 2.0 * GRID_LENGTH
    wall_color = (0.12, 0.25, 0.08)

    draw_box(GRID_LENGTH, 0, wall_height / 2.0,
             wall_thickness, wall_length, wall_height, wall_color)
    draw_box(-GRID_LENGTH, 0, wall_height / 2.0,
             wall_thickness, wall_length, wall_height, wall_color)
    draw_box(0, GRID_LENGTH, wall_height / 2.0,
             wall_length, wall_thickness, wall_height, wall_color)
    draw_box(0, -GRID_LENGTH, wall_height / 2.0,
             wall_length, wall_thickness, wall_height, wall_color)


def draw_one_tree(x, y, size):
    glColor3f(0.34, 0.18, 0.07)
    glPushMatrix()
    glTranslatef(x, y, 0)
    gluCylinder(gluNewQuadric(), size * 0.18, size * 0.14,
                size * 1.45, 10, 5)
    glPopMatrix()

    glColor3f(0.05, 0.40, 0.10)
    glPushMatrix()
    glTranslatef(x, y, size * 1.55)
    gluSphere(gluNewQuadric(), size * 0.65, 10, 10)
    glPopMatrix()

    glColor3f(0.08, 0.50, 0.12)
    glPushMatrix()
    glTranslatef(x + size * 0.30, y, size * 1.40)
    gluSphere(gluNewQuadric(), size * 0.45, 10, 10)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(x - size * 0.30, y, size * 1.42)
    gluSphere(gluNewQuadric(), size * 0.45, 10, 10)
    glPopMatrix()


def draw_jungle_trees():
    for x, y, size in tree_positions:
        draw_one_tree(x, y, size)


def draw_jungle_rocks():
    glColor3f(0.30, 0.28, 0.22)
    for x, y, size in jungle_rocks:
        glPushMatrix()
        glTranslatef(x, y, size * 0.55)
        glScalef(1.25, 1.0, 0.80)
        gluSphere(gluNewQuadric(), size, 10, 10)
        glPopMatrix()


def draw_player_model(x, y, z, angle, fallen=False):
    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(PLAYER_SCALE, PLAYER_SCALE, PLAYER_SCALE)
    glRotatef(angle, 0, 0, 1)

    if fallen:
        glTranslatef(0, 0, 8)
        glRotatef(90, 1, 0, 0)

    draw_box(0, 0, 22, 17, 21, 30, (0.28, 0.25, 0.10))

    glColor3f(0.18, 0.10, 0.06)
    glPushMatrix()
    glTranslatef(0, 0, 45)
    gluSphere(gluNewQuadric(), 8, 12, 12)
    glPopMatrix()

    draw_box(0, 0, 52, 18, 18, 3, (0.22, 0.18, 0.07))

    glColor3f(0.12, 0.16, 0.08)
    for leg_y in (-6, 6):
        glPushMatrix()
        glTranslatef(0, leg_y, 0)
        gluCylinder(gluNewQuadric(), 3, 3, 11, 10, 5)
        glPopMatrix()

    glColor3f(0.70, 0.48, 0.30)
    for arm_y in (-13, 13):
        glPushMatrix()
        glTranslatef(0, arm_y, 31)
        glRotatef(90, 0, 1, 0)
        gluCylinder(gluNewQuadric(), 2.5, 2.5, 16, 10, 5)
        glPopMatrix()

    if weapon_level == 1:
        gun_color = (0.20, 0.20, 0.20)
    elif weapon_level == 2:
        gun_color = (0.65, 0.38, 0.10)
    else:
        gun_color = (0.75, 0.12, 0.08)

    draw_box(17, 0, 31, 34, 5, 5, gun_color)
    glColor3f(gun_color[0], gun_color[1], gun_color[2])
    glPushMatrix()
    glTranslatef(34, 0, 31)
    glRotatef(90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 2.3, 2.3, 14, 10, 5)
    glPopMatrix()

    glPopMatrix()


def choose_monster_type():
    wave = get_wave()
    number = random.randint(1, 100)

    if wave <= 1:
        return MONSTER_NORMAL
    if wave == 2:
        if number <= 25:
            return MONSTER_FAST
        return MONSTER_NORMAL
    if number <= 25:
        return MONSTER_HEAVY
    if number <= 55:
        return MONSTER_FAST
    return MONSTER_NORMAL


def monster_settings(monster_type):
    if monster_type == MONSTER_FAST:
        return 13.0, FAST_MONSTER_SPEED, 1
    if monster_type == MONSTER_HEAVY:
        return 23.0, HEAVY_MONSTER_SPEED, 3
    if monster_type == MONSTER_BOSS:
        return 48.0, BOSS_MONSTER_SPEED, BOSS_MAX_HEALTH
    return 17.0, NORMAL_MONSTER_SPEED, 1


def make_monster_at(x, y, monster_type):
    radius, speed, health = monster_settings(monster_type)
    return [x, y, monster_type, health,
            random.uniform(0.0, 2.0 * math.pi), radius, speed]


def random_stage1_monster_position():
    margin = 55.0
    side = random.randint(0, 3)

    if side == 0:
        return -GRID_LENGTH + margin, random.uniform(-480, 480)
    if side == 1:
        return GRID_LENGTH - margin, random.uniform(-480, 480)
    if side == 2:
        return random.uniform(-480, 480), -GRID_LENGTH + margin
    return random.uniform(-480, 480), GRID_LENGTH - margin


def make_stage1_monster(monster_type=None):
    if monster_type is None:
        monster_type = choose_monster_type()
    x, y = random_stage1_monster_position()
    return make_monster_at(x, y, monster_type)


def reset_stage1_monsters():
    monsters.clear()
    for _ in range(MONSTER_COUNT):
        monsters.append(make_stage1_monster())


def get_monster_size(monster, current_time):
    pulse = 5.0 if monster[2] == MONSTER_BOSS else MONSTER_PULSE_AMOUNT
    return monster[5] + pulse * math.sin(
        current_time * MONSTER_PULSE_SPEED + monster[4]
    )


def draw_monster(monster, radius, base_z=0.0):
    x = monster[0]
    y = monster[1]
    monster_type = monster[2]

    if monster_type == MONSTER_FAST:
        body_color = (0.95, 0.06, 0.38)
    elif monster_type == MONSTER_HEAVY:
        body_color = (0.06, 0.66, 0.92)
    elif monster_type == MONSTER_BOSS:
        body_color = (0.78, 0.06, 0.03)
    else:
        body_color = (1.00, 0.48, 0.04)

    glPushMatrix()
    glTranslatef(x, y, base_z)

    glColor3f(body_color[0], body_color[1], body_color[2])
    glPushMatrix()
    glTranslatef(0, 0, radius)
    gluSphere(gluNewQuadric(), radius, 12, 12)
    glPopMatrix()

    glColor3f(0.10, 0.08, 0.12)
    glPushMatrix()
    glTranslatef(0, 0, 2.0 * radius + radius * 0.45)
    gluSphere(gluNewQuadric(), radius * 0.55, 12, 12)
    glPopMatrix()

    glColor3f(1.0, 0.85, 0.05)
    for eye_y in (-radius * 0.18, radius * 0.18):
        glPushMatrix()
        glTranslatef(radius * 0.42, eye_y,
                     2.0 * radius + radius * 0.52)
        gluSphere(gluNewQuadric(), radius * 0.10, 7, 7)
        glPopMatrix()

    glColor3f(0.75, 0.68, 0.45)
    for horn_y in (-radius * 0.30, radius * 0.30):
        glPushMatrix()
        glTranslatef(0, horn_y, 2.7 * radius)
        gluCylinder(gluNewQuadric(), radius * 0.10, 0,
                    radius * 0.55, 8, 4)
        glPopMatrix()

    if monster_type == MONSTER_FAST:
        glColor3f(1.0, 0.85, 0.12)
        for spike_y in (-radius * 0.72, radius * 0.72):
            glPushMatrix()
            glTranslatef(0, spike_y, radius * 1.35)
            gluCylinder(gluNewQuadric(), radius * 0.16, 0,
                        radius * 0.75, 8, 4)
            glPopMatrix()

    elif monster_type == MONSTER_HEAVY:
        armor_color = (0.80, 0.92, 1.0)
        draw_box(0, -radius * 0.86, radius * 1.35,
                 radius * 1.15, radius * 0.42, radius * 0.65,
                 armor_color)
        draw_box(0, radius * 0.86, radius * 1.35,
                 radius * 1.15, radius * 0.42, radius * 0.65,
                 armor_color)

    elif monster_type == MONSTER_NORMAL:
        glColor3f(1.0, 0.92, 0.12)
        glPushMatrix()
        glTranslatef(radius * 0.82, 0, radius * 1.05)
        gluSphere(gluNewQuadric(), radius * 0.24, 8, 8)
        glPopMatrix()

    glPopMatrix()


def damage_player(amount=1):
    global player_life
    global shield_count

    if shield_count > 0:
        shield_count -= 1
    else:
        player_life -= amount


def draw_bullet(bullet):
    draw_box(bullet[0], bullet[1], bullet[2],
             BULLET_SIZE, BULLET_SIZE, BULLET_SIZE,
             (1.0, 0.75, 0.05))


def add_stage1_bullet(angle):
    angle_rad = math.radians(angle)
    dx = math.cos(angle_rad)
    dy = math.sin(angle_rad)
    bullets.append([
        player_x + dx * BULLET_START_DISTANCE,
        player_y + dy * BULLET_START_DISTANCE,
        BULLET_Z, dx, dy, "stage1"
    ])


def add_side_bullet(scene, player_position, floor_z, facing, damage):
    bullets.append([
        player_position + facing * BULLET_START_DISTANCE,
        0.0,
        floor_z + BULLET_Z,
        float(facing),
        0.0,
        scene,
        damage,
    ])


def boss_aim_direction():
    angle_rad = math.radians(boss_aim_angle)
    return math.cos(angle_rad), math.sin(angle_rad)


def add_boss_player_bullet():
    if boss_master is None:
        return
    dx, dy = boss_aim_direction()
    bullets.append([
        boss_player_x + dx * BULLET_START_DISTANCE,
        boss_player_y + dy * BULLET_START_DISTANCE,
        BULLET_Z,
        dx,
        dy,
        "boss",
        weapon_level,
    ])


def fire_bullet():
    global last_side_shot_time

    if game_mode == "stage1":
        if weapon_level == 1:
            add_stage1_bullet(gun_angle)
        elif weapon_level == 2:
            add_stage1_bullet(gun_angle - 8.0)
            add_stage1_bullet(gun_angle)
            add_stage1_bullet(gun_angle + 8.0)
        else:
            for offset in (-12.0, -6.0, 0.0, 6.0, 12.0):
                add_stage1_bullet(gun_angle + offset)

    elif game_mode == "stage2" and stair_transition is None:
        current_time = time.time()
        if current_time - last_side_shot_time < SIDE_FIRE_COOLDOWN:
            return
        last_side_shot_time = current_time
        floor_z = STAGE2_FLOOR_Z[active_floor]
        add_side_bullet("stage2", stage2_player_x,
                        floor_z, stage2_facing, weapon_level)

    elif game_mode == "boss":
        current_time = time.time()
        if current_time - last_side_shot_time < SIDE_FIRE_COOLDOWN:
            return
        last_side_shot_time = current_time
        add_boss_player_bullet()


def side_bullet_damage(bullet):
    if len(bullet) > 6:
        return bullet[6]
    return 1


def swept_circle_hit_fraction(start_x, start_y, end_x, end_y,
                              target_x, target_y, target_radius,
                              projectile_radius=BULLET_SIZE / 2.0):
    segment_x = end_x - start_x
    segment_y = end_y - start_y
    offset_x = start_x - target_x
    offset_y = start_y - target_y
    combined_radius = target_radius + projectile_radius

    c_value = (
        offset_x * offset_x
        + offset_y * offset_y
        - combined_radius * combined_radius
    )
    if c_value <= 0.0:
        return 0.0

    a_value = segment_x * segment_x + segment_y * segment_y
    if a_value <= 0.000001:
        return None

    b_value = 2.0 * (
        offset_x * segment_x + offset_y * segment_y
    )
    discriminant = b_value * b_value - 4.0 * a_value * c_value
    if discriminant < 0.0:
        return None

    root = math.sqrt(discriminant)
    first_fraction = (-b_value - root) / (2.0 * a_value)
    second_fraction = (-b_value + root) / (2.0 * a_value)

    if 0.0 <= first_fraction <= 1.0:
        return first_fraction
    if 0.0 <= second_fraction <= 1.0:
        return second_fraction
    return None


def nearest_2d_target(start_x, start_y, end_x, end_y,
                      candidates, current_time):
    nearest = None
    nearest_fraction = None

    for candidate in candidates:
        enemy = candidate[2]
        radius = get_monster_size(enemy, current_time)
        fraction = swept_circle_hit_fraction(
            start_x, start_y, end_x, end_y,
            enemy[0], enemy[1], radius
        )
        if fraction is not None and (
            nearest_fraction is None or fraction < nearest_fraction
        ):
            nearest = candidate
            nearest_fraction = fraction

    return nearest


def start_bonus_mode(current_time=None):
    global game_mode
    global bonus_origin
    global bonus_started_at
    global runner_lane
    global last_bonus_spawn
    global missed_bullets_since_bonus
    global bonus_life_trigger_armed
    global camera_mode

    if game_mode not in ("stage1", "stage2", "boss"):
        return

    if current_time is None:
        current_time = time.time()

    bonus_origin = game_mode
    game_mode = "bonus"
    bonus_started_at = current_time
    runner_lane = 1
    last_bonus_spawn = current_time
    missed_bullets_since_bonus = 0
    bonus_life_trigger_armed = False
    camera_mode = "third_person"

    bonus_objects.clear()
    bullets.clear()
    boss_projectiles.clear()


def check_bonus_transition(current_time):
    global bonus_life_trigger_armed

    if player_life > BONUS_LIFE_TRIGGER:
        bonus_life_trigger_armed = True

    life_triggered = (
        player_life <= BONUS_LIFE_TRIGGER
        and bonus_life_trigger_armed
    )
    misses_triggered = missed_bullets_since_bonus >= BONUS_MISS_TARGET

    if (
        game_mode in ("stage1", "stage2", "boss")
        and (life_triggered or misses_triggered)
    ):
        start_bonus_mode(current_time)
        return True
    return False


def record_missed_bullet(current_time):
    global missed_bullets_since_bonus
    missed_bullets_since_bonus += 1
    return check_bonus_transition(current_time)


def end_game_if_needed():
    global game_mode
    if player_life <= 0:
        game_mode = "game_over"
        bullets.clear()
        boss_projectiles.clear()
        return True
    return False


def update_stage1_monsters(delta_time, current_time):
    for index in range(len(monsters)):
        monster = monsters[index]
        radius = get_monster_size(monster, current_time)
        dx = player_x - monster[0]
        dy = player_y - monster[1]
        distance = math.sqrt(dx * dx + dy * dy)
        speed = monster[6] + get_wave() * 2.0

        if distance > 0.0001:
            monster[0] += (dx / distance) * speed * delta_time
            monster[1] += (dy / distance) * speed * delta_time

        if get_distance(monster[0], monster[1], player_x, player_y) <= (
            PLAYER_COLLISION_RADIUS + radius
        ):
            damage_player(1)
            monsters[index] = make_stage1_monster()
            if end_game_if_needed():
                return
            if check_bonus_transition(current_time):
                return


def update_stage1_bullets(delta_time, current_time):
    global game_score
    global missed_bullets_since_bonus

    speed = BOOSTED_BULLET_SPEED if boost_is_active(current_time) else BULLET_SPEED
    new_bullets = []

    for bullet in bullets:
        start_x = bullet[0]
        start_y = bullet[1]
        end_x = start_x + bullet[3] * speed * delta_time
        end_y = start_y + bullet[4] * speed * delta_time
        bullet[0] = end_x
        bullet[1] = end_y

        candidates = [
            ("stage1", index, monster)
            for index, monster in enumerate(monsters)
        ]
        target = nearest_2d_target(
            start_x, start_y, end_x, end_y,
            candidates, current_time
        )

        if target is not None:
            target_index = target[1]
            monster = target[2]
            monster[3] -= 1
            if monster[3] <= 0:
                game_score += monster_score(monster[2])
                monsters[target_index] = make_stage1_monster()
            continue

        if abs(bullet[0]) > GRID_LENGTH or abs(bullet[1]) > GRID_LENGTH:
            if record_missed_bullet(current_time):
                return
            continue

        new_bullets.append(bullet)

    bullets[:] = new_bullets


def make_stage2_enemy(monster_type, x):
    enemy = make_monster_at(x, 0.0, monster_type)
    if monster_type == MONSTER_FAST:
        enemy[3] = STAGE2_FAST_HEALTH
    elif monster_type == MONSTER_HEAVY:
        enemy[3] = STAGE2_HEAVY_HEALTH
    else:
        enemy[3] = STAGE2_NORMAL_HEALTH
    return enemy


def reset_stage2():
    global active_floor
    global stage2_player_x
    global stage2_facing
    global stair_transition

    floor_types = [
        [MONSTER_NORMAL, MONSTER_NORMAL, MONSTER_NORMAL,
         MONSTER_FAST, MONSTER_FAST],
        [MONSTER_NORMAL, MONSTER_NORMAL, MONSTER_FAST,
         MONSTER_FAST, MONSTER_HEAVY],
        [MONSTER_NORMAL, MONSTER_FAST, MONSTER_FAST,
         MONSTER_HEAVY, MONSTER_HEAVY],
    ]
    positions = [-250.0, -120.0, 20.0, 160.0, 290.0]

    for floor_index in range(3):
        stage2_floor_enemies[floor_index] = []
        for enemy_index in range(5):
            stage2_floor_enemies[floor_index].append(
                make_stage2_enemy(
                    floor_types[floor_index][enemy_index],
                    positions[enemy_index]
                )
            )

    active_floor = 0
    stage2_player_x = -360.0
    stage2_facing = 1
    stair_transition = None


def start_stage2():
    global game_mode
    global camera_mode
    global last_side_shot_time
    game_mode = "stage2"
    camera_mode = "third_person"
    last_side_shot_time = 0.0
    bullets.clear()
    boss_projectiles.clear()
    monsters.clear()
    reset_stage2()


def draw_stage2_world():
    draw_box(0, 185, 220, 1180, 35, 520, (0.045, 0.14, 0.045))
    draw_box(0, 70, -28, 1120, 520, 55, (0.10, 0.24, 0.075))
    draw_box(-535, 40, 220, 45, 430, 500, (0.10, 0.22, 0.07))
    draw_box(535, 40, 220, 45, 430, 500, (0.10, 0.22, 0.07))

    for column_x in (-455, -230, 0, 230, 455):
        draw_box(column_x, 160, 205, 34, 40, 410, (0.23, 0.25, 0.16))
        glColor3f(0.06, 0.38, 0.08)
        glPushMatrix()
        glTranslatef(column_x, 135, 430)
        glScalef(1.7, 0.75, 0.75)
        gluSphere(gluNewQuadric(), 42, 10, 10)
        glPopMatrix()

    for floor_index, floor_z in enumerate(STAGE2_FLOOR_Z):
        if floor_index == active_floor:
            floor_color = (0.38, 0.34, 0.13)
        else:
            floor_color = (0.22, 0.25, 0.13)

        draw_box(0, 0, floor_z - 12, 980, 330, 24, floor_color)

        tile_width = 98.0
        for tile_index in range(10):
            tile_x = -441.0 + tile_index * tile_width
            if (tile_index + floor_index) % 2 == 0:
                tile_color = (0.20, 0.38, 0.10)
            else:
                tile_color = (0.29, 0.43, 0.12)
            draw_box(tile_x, -8, floor_z + 1,
                     tile_width - 3, 300, 3, tile_color)

        for support_x in (-440, -220, 0, 220, 440):
            if floor_index > 0:
                draw_box(support_x, 105, floor_z - 80,
                         26, 26, 140, (0.24, 0.22, 0.14))

        draw_box(0, 142, floor_z + 24,
                 980, 12, 45, (0.12, 0.25, 0.075))

    draw_stage2_stairs(0)
    draw_stage2_stairs(1)
    draw_boss_door()


def draw_stage2_stairs(lower_floor):
    stair_x = STAGE2_STAIR_X[lower_floor]
    direction = 1.0 if stair_x > 0 else -1.0
    lower_z = STAGE2_FLOOR_Z[lower_floor]
    unlocked = len(stage2_floor_enemies[lower_floor]) == 0

    if unlocked:
        color = (0.55, 0.43, 0.20)
    else:
        color = (0.30, 0.20, 0.12)

    for step in range(8):
        step_x = stair_x - direction * (7 - step) * 12.0
        step_z = lower_z + 10.0 + step * 20.0
        draw_box(step_x, 0, step_z, 38, 180, 20, color)


def draw_boss_door():
    floor_z = STAGE2_FLOOR_Z[2]
    unlocked = all(len(enemy_list) == 0 for enemy_list in stage2_floor_enemies)
    door_color = (0.10, 0.65, 0.48) if unlocked else (0.35, 0.12, 0.08)

    draw_box(420, 0, floor_z + 58, 18, 110, 115, (0.33, 0.30, 0.24))
    draw_box(350, 0, floor_z + 58, 18, 110, 115, (0.33, 0.30, 0.24))
    draw_box(385, 0, floor_z + 120, 90, 110, 18, (0.33, 0.30, 0.24))
    draw_box(385, 0, floor_z + 55, 45, 18, 92, door_color)


def stage2_player_height(current_time):
    if stair_transition is None:
        return STAGE2_FLOOR_Z[active_floor]

    from_floor = stair_transition[0]
    to_floor = stair_transition[1]
    progress = (current_time - stair_transition[2]) / STAIR_TRAVEL_TIME
    progress = max(0.0, min(1.0, progress))
    return (
        STAGE2_FLOOR_Z[from_floor]
        + (STAGE2_FLOOR_Z[to_floor] - STAGE2_FLOOR_Z[from_floor]) * progress
    )


def stage2_player_position(current_time):
    if stair_transition is None:
        return stage2_player_x
    progress = (current_time - stair_transition[2]) / STAIR_TRAVEL_TIME
    progress = max(0.0, min(1.0, progress))
    return stair_transition[3] + (
        stair_transition[4] - stair_transition[3]
    ) * progress


def begin_stair_transition(to_floor):
    global stair_transition
    connector_index = min(active_floor, to_floor)
    connector_x = STAGE2_STAIR_X[connector_index]
    target_x = 360.0 if connector_x > 0 else -360.0
    bullets.clear()
    stair_transition = [
        active_floor, to_floor, time.time(), stage2_player_x, target_x
    ]


def try_stage2_up():
    if stair_transition is not None:
        return

    if active_floor < 2:
        stair_x = STAGE2_STAIR_X[active_floor]
        if (
            len(stage2_floor_enemies[active_floor]) == 0
            and abs(stage2_player_x - stair_x) <= STAIR_TRIGGER_DISTANCE
        ):
            begin_stair_transition(active_floor + 1)
    else:
        door_unlocked = all(
            len(enemy_list) == 0 for enemy_list in stage2_floor_enemies
        )
        if door_unlocked and stage2_player_x >= 330.0:
            start_boss()


def try_stage2_down():
    if stair_transition is not None or active_floor <= 0:
        return
    stair_x = STAGE2_STAIR_X[active_floor - 1]
    if abs(stage2_player_x - stair_x) <= STAIR_TRIGGER_DISTANCE:
        begin_stair_transition(active_floor - 1)


def update_stair_transition(current_time):
    global active_floor
    global stage2_player_x
    global stair_transition

    if stair_transition is None:
        return False

    if current_time - stair_transition[2] >= STAIR_TRAVEL_TIME:
        active_floor = stair_transition[1]
        stage2_player_x = stair_transition[4]
        stair_transition = None
    return True


def move_side_enemy_to_edge(enemy, player_position, half_width):
    if player_position >= 0:
        enemy[0] = -half_width + 35.0
    else:
        enemy[0] = half_width - 35.0


def update_stage2_enemies(delta_time, current_time):
    enemies = stage2_floor_enemies[active_floor]
    speed_multiplier = STAGE2_SPEED_MULTIPLIERS[active_floor]

    for enemy in enemies:
        radius = get_monster_size(enemy, current_time)
        distance = stage2_player_x - enemy[0]
        direction = 1.0 if distance > 0 else -1.0
        enemy[0] += direction * enemy[6] * speed_multiplier * delta_time

        if abs(enemy[0] - stage2_player_x) <= PLAYER_COLLISION_RADIUS + radius:
            damage_player(1)
            move_side_enemy_to_edge(enemy, stage2_player_x, STAGE2_HALF_WIDTH)
            if end_game_if_needed():
                return
            if check_bonus_transition(current_time):
                return


def update_stage2_bullets(delta_time, current_time):
    global game_score
    global missed_bullets_since_bonus

    speed = BOOSTED_BULLET_SPEED if boost_is_active(current_time) else BULLET_SPEED
    enemies = stage2_floor_enemies[active_floor]
    new_bullets = []

    for bullet in bullets:
        start_x = bullet[0]
        start_y = bullet[1]
        end_x = start_x + bullet[3] * speed * delta_time
        end_y = start_y + bullet[4] * speed * delta_time
        bullet[0] = end_x
        bullet[1] = end_y

        candidates = [
            ("stage2", index, enemy)
            for index, enemy in enumerate(enemies)
        ]
        target = nearest_2d_target(
            start_x, start_y, end_x, end_y,
            candidates, current_time
        )

        if target is not None:
            enemy = target[2]
            enemy[3] -= side_bullet_damage(bullet)
            if enemy[3] <= 0:
                game_score += monster_score(enemy[2])
                enemies.remove(enemy)
            continue

        if abs(bullet[0]) > STAGE2_HALF_WIDTH:
            if record_missed_bullet(current_time):
                return
            continue

        new_bullets.append(bullet)

    bullets[:] = new_bullets


def update_stage2(delta_time, current_time):
    was_climbing = update_stair_transition(current_time)
    if was_climbing:
        return
    update_stage2_enemies(delta_time, current_time)
    if game_mode == "stage2":
        update_stage2_bullets(delta_time, current_time)


def random_boss_edge_position():
    side = random.randint(0, 3)
    edge_x = BOSS_ARENA_HALF_WIDTH - BOSS_ARENA_MARGIN
    edge_y = BOSS_ARENA_HALF_DEPTH - BOSS_ARENA_MARGIN
    if side == 0:
        return -edge_x, random.uniform(-edge_y, edge_y)
    if side == 1:
        return edge_x, random.uniform(-edge_y, edge_y)
    if side == 2:
        return random.uniform(-edge_x, edge_x), -edge_y
    return random.uniform(-edge_x, edge_x), edge_y


def make_boss_minion(monster_type):
    x, y = random_boss_edge_position()
    minion = make_monster_at(x, y, monster_type)
    if monster_type == MONSTER_FAST:
        minion[3] = BOSS_FAST_MINION_HEALTH
    elif monster_type == MONSTER_HEAVY:
        minion[3] = BOSS_HEAVY_MINION_HEALTH
    else:
        minion[3] = BOSS_NORMAL_MINION_HEALTH
    return minion


def start_boss():
    global game_mode
    global boss_health
    global boss_master
    global boss_player_x
    global boss_player_y
    global boss_aim_angle
    global boss_minion_cycle_index
    global last_side_shot_time
    global last_boss_shot_time
    global last_boss_projectile_hit_time

    game_mode = "boss"
    boss_health = BOSS_MAX_HEALTH
    boss_master = make_monster_at(
        BOSS_MASTER_START_X, BOSS_MASTER_START_Y, MONSTER_BOSS
    )
    boss_master[3] = BOSS_MAX_HEALTH

    boss_minions.clear()
    boss_minion_cycle_index = 0
    boss_minions.append(make_boss_minion(
        BOSS_MINION_CYCLE[boss_minion_cycle_index]
    ))

    boss_player_x = BOSS_PLAYER_START_X
    boss_player_y = BOSS_PLAYER_START_Y
    boss_aim_angle = BOSS_PLAYER_START_ANGLE
    last_side_shot_time = 0.0
    last_boss_shot_time = time.time()
    last_boss_projectile_hit_time = -100.0
    bullets.clear()
    boss_projectiles.clear()


def draw_boss_arena():
    arena_width = BOSS_ARENA_HALF_WIDTH * 2.0
    arena_depth = BOSS_ARENA_HALF_DEPTH * 2.0
    tile_width = arena_width / BOSS_ARENA_TILE_COUNT
    tile_depth = arena_depth / BOSS_ARENA_TILE_COUNT

    draw_box(0, 0, -18, arena_width, arena_depth, 36,
             (0.16, 0.10, 0.055))
    for tile_x_index in range(BOSS_ARENA_TILE_COUNT):
        for tile_y_index in range(BOSS_ARENA_TILE_COUNT):
            tile_x = -BOSS_ARENA_HALF_WIDTH + tile_x_index * tile_width
            tile_y = -BOSS_ARENA_HALF_DEPTH + tile_y_index * tile_depth
            if (tile_x_index + tile_y_index) % 2 == 0:
                glColor3f(0.24, 0.14, 0.055)
            else:
                glColor3f(0.34, 0.20, 0.07)
            glBegin(GL_QUADS)
            glVertex3f(tile_x, tile_y, 1)
            glVertex3f(tile_x + tile_width, tile_y, 1)
            glVertex3f(tile_x + tile_width, tile_y + tile_depth, 1)
            glVertex3f(tile_x, tile_y + tile_depth, 1)
            glEnd()

    trench_offset = 10.0
    for trench_y in (
        -BOSS_ARENA_HALF_DEPTH - trench_offset,
        BOSS_ARENA_HALF_DEPTH + trench_offset,
    ):
        draw_box(0, trench_y, 5, arena_width + 30.0, 18, 8,
                 (0.88, 0.10, 0.02))
        draw_box(0, trench_y, 10, arena_width + 30.0, 6, 5,
                 (1.0, 0.62, 0.04))

    for trench_x in (
        -BOSS_ARENA_HALF_WIDTH - trench_offset,
        BOSS_ARENA_HALF_WIDTH + trench_offset,
    ):
        draw_box(trench_x, 0, 5, 18, arena_depth + 30.0, 8,
                 (0.88, 0.10, 0.02))

    wall_x = BOSS_ARENA_HALF_WIDTH + 35.0
    wall_y = BOSS_ARENA_HALF_DEPTH + 35.0
    draw_box(-wall_x, 0, 75, 30, arena_depth + 70.0, 150,
             (0.28, 0.25, 0.16))
    draw_box(wall_x, 0, 75, 30, arena_depth + 70.0, 150,
             (0.28, 0.25, 0.16))
    draw_box(0, wall_y, 165, arena_width + 70.0, 30, 330,
             (0.10, 0.025, 0.018))
    draw_box(0, -wall_y, 35, arena_width + 70.0, 30, 70,
             (0.30, 0.28, 0.18))

    for pillar_x in (-450, -150, 150, 450):
        pillar_y = BOSS_ARENA_HALF_DEPTH - 35.0
        draw_box(pillar_x, pillar_y, 82, 42, 42, 164,
                 (0.36, 0.32, 0.24))
        glColor3f(0.55, 0.15, 0.05)
        glPushMatrix()
        glTranslatef(pillar_x, pillar_y, 180)
        gluSphere(gluNewQuadric(), 22, 10, 10)
        glPopMatrix()

        glColor3f(0.06, 0.38, 0.08)
        glPushMatrix()
        glTranslatef(pillar_x, pillar_y + 20.0, 245)
        glScalef(1.45, 0.80, 0.80)
        gluSphere(gluNewQuadric(), 34, 10, 10)
        glPopMatrix()

    for ruin_y in (-360, -80, 200, 430):
        draw_box(-570, ruin_y, 38, 55, 48, 76,
                 (0.38, 0.33, 0.23))
        draw_box(570, ruin_y, 38, 55, 48, 76,
                 (0.38, 0.33, 0.23))


def draw_fire_titan(monster, current_time):
    facing_angle = math.degrees(math.atan2(
        boss_player_y - monster[1],
        boss_player_x - monster[0]
    ))
    core_pulse = 2.5 * math.sin(current_time * 7.0)

    glPushMatrix()
    glTranslatef(monster[0], monster[1], 0)
    glRotatef(facing_angle, 0, 0, 1)

    for leg_y in (-25.0, 25.0):
        draw_box(-8, leg_y, 28, 28, 28, 56, (0.10, 0.08, 0.09))
        draw_box(12, leg_y, 8, 48, 32, 16, (0.26, 0.08, 0.04))

    draw_box(0, 0, 64, 78, 78, 92, (0.12, 0.10, 0.12))
    draw_box(18, 0, 68, 34, 88, 62, (0.30, 0.08, 0.04))

    glColor3f(0.18, 0.14, 0.15)
    glPushMatrix()
    glTranslatef(5, 0, 112)
    gluSphere(gluNewQuadric(), 31, 12, 12)
    glPopMatrix()

    glColor3f(1.0, 0.10, 0.02)
    glPushMatrix()
    glTranslatef(42, 0, 72)
    gluSphere(gluNewQuadric(), 13 + core_pulse, 12, 12)
    glPopMatrix()
    glColor3f(1.0, 0.72, 0.05)
    glPushMatrix()
    glTranslatef(49, 0, 72)
    gluSphere(gluNewQuadric(), 6, 9, 9)
    glPopMatrix()

    glColor3f(1.0, 0.75, 0.03)
    for eye_y in (-10.0, 10.0):
        glPushMatrix()
        glTranslatef(31, eye_y, 118)
        gluSphere(gluNewQuadric(), 5, 8, 8)
        glPopMatrix()

    glColor3f(0.88, 0.78, 0.56)
    for horn_y in (-20.0, 20.0):
        glPushMatrix()
        glTranslatef(0, horn_y, 132)
        glRotatef(-28, 0, 1, 0)
        gluCylinder(gluNewQuadric(), 8, 0, 48, 9, 5)
        glPopMatrix()

    for cannon_y in (-47.0, 47.0):
        draw_box(0, cannon_y, 92, 38, 28, 30, (0.08, 0.07, 0.08))
        glColor3f(0.52, 0.10, 0.035)
        glPushMatrix()
        glTranslatef(10, cannon_y, 94)
        glRotatef(90, 0, 1, 0)
        gluCylinder(gluNewQuadric(), 9, 7, 50, 10, 5)
        glPopMatrix()

    glColor3f(0.58, 0.13, 0.045)
    for claw_y in (-38.0, 38.0):
        glPushMatrix()
        glTranslatef(30, claw_y, 42)
        glRotatef(90, 0, 1, 0)
        gluCylinder(gluNewQuadric(), 9, 2, 48, 9, 5)
        glPopMatrix()

    glPopMatrix()


def boss_is_in_rage_phase():
    return boss_health <= BOSS_MAX_HEALTH / 2.0


def spawn_boss_projectiles(current_time):
    global last_boss_shot_time

    if boss_master is None or boss_projectiles:
        return

    if current_time - last_boss_shot_time < BOSS_SHOT_INTERVAL:
        return

    shot_angle = math.atan2(
        boss_player_y - boss_master[1],
        boss_player_x - boss_master[0]
    )
    dx = math.cos(shot_angle)
    dy = math.sin(shot_angle)
    boss_projectiles.append([
        boss_master[0] + dx * 62.0,
        boss_master[1] + dy * 62.0,
        62.0,
        dx,
        dy,
        BOSS_BULLET_SPEED,
    ])

    last_boss_shot_time = current_time


def draw_boss_projectile(projectile):
    glColor3f(0.95, 0.08, 0.015)
    glPushMatrix()
    glTranslatef(projectile[0], projectile[1], projectile[2])
    gluSphere(gluNewQuadric(), BOSS_PROJECTILE_RADIUS, 9, 9)
    glPopMatrix()

    glColor3f(1.0, 0.72, 0.04)
    glPushMatrix()
    glTranslatef(projectile[0], projectile[1], projectile[2])
    gluSphere(gluNewQuadric(), BOSS_PROJECTILE_RADIUS * 0.48, 8, 8)
    glPopMatrix()


def update_boss_projectiles(delta_time, current_time):
    global last_boss_projectile_hit_time

    spawn_boss_projectiles(current_time)
    new_projectiles = []

    for projectile in boss_projectiles:
        start_x = projectile[0]
        start_y = projectile[1]
        end_x = start_x + projectile[3] * projectile[5] * delta_time
        end_y = start_y + projectile[4] * projectile[5] * delta_time
        projectile[0] = end_x
        projectile[1] = end_y

        hit_fraction = swept_circle_hit_fraction(
            start_x, start_y, end_x, end_y,
            boss_player_x, boss_player_y,
            PLAYER_COLLISION_RADIUS,
            BOSS_PROJECTILE_RADIUS,
        )

        if hit_fraction is not None:
            if (
                current_time - last_boss_projectile_hit_time
                >= BOSS_PROJECTILE_HIT_COOLDOWN
            ):
                damage_player(BOSS_PROJECTILE_DAMAGE)
                last_boss_projectile_hit_time = current_time
                if end_game_if_needed():
                    return
                if check_bonus_transition(current_time):
                    return
            continue

        if (
            abs(projectile[0]) > BOSS_ARENA_HALF_WIDTH + 30.0
            or abs(projectile[1]) > BOSS_ARENA_HALF_DEPTH + 30.0
        ):
            continue

        new_projectiles.append(projectile)

    boss_projectiles[:] = new_projectiles


def move_boss_enemy_to_edge(enemy):
    enemy[0], enemy[1] = random_boss_edge_position()


def update_boss_enemies(delta_time, current_time):
    global boss_health

    all_enemies = []
    if boss_master is not None:
        all_enemies.append((boss_master, 2, BOSS_ARENA_HALF_WIDTH))
    for minion in boss_minions:
        all_enemies.append((minion, 1, BOSS_ARENA_HALF_WIDTH))

    health_ratio = max(0.0, min(1.0, boss_health / BOSS_MAX_HEALTH))
    speed_multiplier = 1.0 + 0.5 * (1.0 - health_ratio)

    for enemy, damage, half_width in all_enemies:
        radius = get_monster_size(enemy, current_time)
        dx = boss_player_x - enemy[0]
        dy = boss_player_y - enemy[1]
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 0.0001:
            movement = enemy[6] * speed_multiplier * delta_time
            enemy[0] += (dx / distance) * movement
            enemy[1] += (dy / distance) * movement

        if get_distance(
            enemy[0], enemy[1], boss_player_x, boss_player_y
        ) <= PLAYER_COLLISION_RADIUS + radius:
            damage_player(damage)
            move_boss_enemy_to_edge(enemy)
            if enemy[2] == MONSTER_BOSS:
                boss_health = enemy[3]
            if end_game_if_needed():
                return
            if check_bonus_transition(current_time):
                return


def update_boss_bullets(delta_time, current_time):
    global game_score
    global missed_bullets_since_bonus
    global boss_health
    global game_mode
    global boss_minion_cycle_index

    speed = BOOSTED_BULLET_SPEED if boost_is_active(current_time) else BULLET_SPEED
    new_bullets = []

    for bullet in bullets:
        start_x = bullet[0]
        start_y = bullet[1]
        end_x = start_x + bullet[3] * speed * delta_time
        end_y = start_y + bullet[4] * speed * delta_time
        bullet[0] = end_x
        bullet[1] = end_y

        candidates = [
            ("minion", index, minion)
            for index, minion in enumerate(boss_minions)
        ]
        if boss_master is not None:
            candidates.append(("master", -1, boss_master))

        target = nearest_2d_target(
            start_x, start_y, end_x, end_y,
            candidates, current_time
        )

        if target is not None:
            target_kind = target[0]
            target_index = target[1]
            enemy = target[2]
            enemy[3] -= side_bullet_damage(bullet)

            if target_kind == "minion" and enemy[3] <= 0:
                minion_type = enemy[2]
                game_score += monster_score(minion_type)
                boss_minion_cycle_index = (
                    boss_minion_cycle_index + 1
                ) % len(BOSS_MINION_CYCLE)
                next_type = BOSS_MINION_CYCLE[boss_minion_cycle_index]
                boss_minions[target_index] = make_boss_minion(next_type)

            elif target_kind == "master":
                boss_health = enemy[3]
                if enemy[3] <= 0:
                    game_score += 20
                    boss_minions.clear()
                    bullets.clear()
                    boss_projectiles.clear()
                    game_mode = "win"
                    return

            continue

        if (
            abs(bullet[0]) > BOSS_ARENA_HALF_WIDTH
            or abs(bullet[1]) > BOSS_ARENA_HALF_DEPTH
        ):
            if record_missed_bullet(current_time):
                return
            continue

        new_bullets.append(bullet)

    bullets[:] = new_bullets


def update_boss(delta_time, current_time):
    update_boss_enemies(delta_time, current_time)
    if game_mode == "boss":
        update_boss_bullets(delta_time, current_time)
    if game_mode == "boss":
        update_boss_projectiles(delta_time, current_time)


def choose_bonus_object():
    number = random.randint(1, 100)
    if number <= 18:
        return ITEM_LIFE
    if number <= 30:
        return ITEM_WEAPON
    if number <= 40:
        return ITEM_SHIELD
    if number <= 50:
        return ITEM_BOOST
    if number <= 75:
        return OBSTACLE_ROCK
    return OBSTACLE_LOG


def spawn_bonus_object(current_time):
    global last_bonus_spawn
    if current_time - last_bonus_spawn < BONUS_SPAWN_DELAY:
        return
    bonus_objects.append([
        random.randint(0, 2),
        650.0,
        choose_bonus_object(),
    ])
    last_bonus_spawn = current_time


def draw_bonus_track():
    glColor3f(0.30, 0.24, 0.13)
    glBegin(GL_QUADS)
    glVertex3f(-190, -180, 0)
    glVertex3f(190, -180, 0)
    glVertex3f(190, 720, 0)
    glVertex3f(-190, 720, 0)
    glEnd()

    glColor3f(0.05, 0.20, 0.07)
    glBegin(GL_QUADS)
    glVertex3f(-GRID_LENGTH, -180, -2)
    glVertex3f(-190, -180, -2)
    glVertex3f(-190, 720, -2)
    glVertex3f(-GRID_LENGTH, 720, -2)
    glVertex3f(190, -180, -2)
    glVertex3f(GRID_LENGTH, -180, -2)
    glVertex3f(GRID_LENGTH, 720, -2)
    glVertex3f(190, 720, -2)
    glEnd()

    glColor3f(0.70, 0.58, 0.25)
    for x in (-60.0, 60.0):
        glBegin(GL_QUADS)
        glVertex3f(x - 2, -180, 1)
        glVertex3f(x + 2, -180, 1)
        glVertex3f(x + 2, 720, 1)
        glVertex3f(x - 2, 720, 1)
        glEnd()


def draw_bonus_sides():
    for x, y, size in temple_blocks:
        draw_box(x, y, size / 2.0, 55, 70, size, (0.32, 0.31, 0.25))
        glColor3f(0.06, 0.42, 0.10)
        glPushMatrix()
        glTranslatef(x, y - 18, size + 10)
        gluSphere(gluNewQuadric(), 12, 8, 8)
        glPopMatrix()


def draw_bonus_player(current_time):
    bounce = 2.5 * math.sin(current_time * 8.0)
    draw_player_model(
        RUNNER_LANES[runner_lane],
        RUNNER_PLAYER_Y,
        bounce,
        90.0,
    )


def draw_bonus_object(item):
    x = RUNNER_LANES[item[0]]
    y = item[1]
    object_type = item[2]

    glPushMatrix()
    glTranslatef(x, y, 20)

    if object_type == ITEM_LIFE:
        draw_box(0, 0, 0, 12, 32, 12, (0.85, 0.08, 0.08))
        draw_box(0, 0, 0, 32, 12, 12, (0.85, 0.08, 0.08))
        glColor3f(1.0, 0.35, 0.35)
        gluSphere(gluNewQuadric(), 7, 8, 8)

    elif object_type == ITEM_WEAPON:
        draw_box(-6, 0, 0, 24, 12, 12, (0.95, 0.62, 0.05))
        draw_box(-13, 0, -8, 8, 10, 16, (0.45, 0.24, 0.06))
        glColor3f(0.95, 0.62, 0.05)
        glPushMatrix()
        glTranslatef(6, 0, 0)
        glRotatef(90, 0, 1, 0)
        gluCylinder(gluNewQuadric(), 4, 3, 25, 10, 5)
        glPopMatrix()

    elif object_type == ITEM_SHIELD:
        glColor3f(0.10, 0.42, 0.95)
        glPushMatrix()
        glScalef(0.45, 1.0, 1.20)
        gluSphere(gluNewQuadric(), 18, 12, 12)
        glPopMatrix()
        glColor3f(0.65, 0.82, 1.0)
        glPushMatrix()
        glTranslatef(-8, 0, 0)
        gluSphere(gluNewQuadric(), 6, 8, 8)
        glPopMatrix()

    elif object_type == ITEM_BOOST:
        glColor3f(0.90, 0.18, 0.72)
        glPushMatrix()
        glTranslatef(-6, 0, 0)
        gluSphere(gluNewQuadric(), 12, 10, 10)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(6, 0, 0)
        gluSphere(gluNewQuadric(), 12, 10, 10)
        glPopMatrix()
        glColor3f(0.10, 0.55, 0.12)
        glPushMatrix()
        glTranslatef(0, 0, 9)
        gluCylinder(gluNewQuadric(), 2.5, 1.5, 16, 8, 4)
        glPopMatrix()

    elif object_type == OBSTACLE_ROCK:
        glColor3f(0.35, 0.33, 0.28)
        for rock_x, rock_y, rock_z, scale_x, scale_y, scale_z in (
            (-8, 0, 0, 1.0, 0.9, 0.8),
            (8, 4, -2, 0.8, 1.0, 0.7),
            (1, -5, 7, 0.7, 0.7, 0.9),
        ):
            glPushMatrix()
            glTranslatef(rock_x, rock_y, rock_z)
            glScalef(scale_x, scale_y, scale_z)
            gluSphere(gluNewQuadric(), 17, 10, 10)
            glPopMatrix()

    else:
        glColor3f(0.38, 0.18, 0.06)
        glPushMatrix()
        glTranslatef(-22, 0, 0)
        glRotatef(90, 0, 1, 0)
        gluCylinder(gluNewQuadric(), 10, 10, 44, 10, 5)
        glPopMatrix()
        for branch_y in (-7, 7):
            glPushMatrix()
            glTranslatef(0, branch_y, 0)
            glRotatef(65, 1, 0, 0)
            gluCylinder(gluNewQuadric(), 3, 1, 18, 8, 4)
            glPopMatrix()

    glPopMatrix()


def apply_bonus_object(object_type):
    global player_life
    global weapon_level
    global shield_count
    global boost_ready

    if object_type == ITEM_LIFE:
        player_life = min(MAX_LIFE, player_life + 1)
    elif object_type == ITEM_WEAPON:
        weapon_level = min(3, weapon_level + 1)
    elif object_type == ITEM_SHIELD:
        shield_count = min(2, shield_count + 1)
    elif object_type == ITEM_BOOST:
        boost_ready = True
    else:
        damage_player(1)


def return_from_bonus(current_time):
    global game_mode
    global power_boost_end
    global boost_ready
    global last_side_shot_time
    global last_boss_shot_time

    game_mode = bonus_origin
    last_side_shot_time = 0.0
    last_boss_shot_time = current_time
    boss_projectiles.clear()
    bonus_objects.clear()

    if boost_ready:
        power_boost_end = current_time + 15.0
        boost_ready = False


def update_bonus(delta_time, current_time):
    spawn_bonus_object(current_time)
    new_objects = []

    for item in bonus_objects:
        item[1] -= RUNNER_OBJECT_SPEED * delta_time
        same_lane = item[0] == runner_lane
        close_y = abs(item[1] - RUNNER_PLAYER_Y) <= 32.0

        if same_lane and close_y:
            apply_bonus_object(item[2])
            if end_game_if_needed():
                bonus_objects.clear()
                return
            continue

        if item[1] >= -160.0:
            new_objects.append(item)

    bonus_objects[:] = new_objects

    if current_time - bonus_started_at >= BONUS_DURATION:
        return_from_bonus(current_time)


def reset_game():
    global player_x
    global player_y
    global player_angle
    global gun_angle
    global player_life
    global game_score
    global weapon_level
    global shield_count
    global power_boost_end
    global boost_ready
    global game_mode
    global missed_bullets_since_bonus
    global bonus_life_trigger_armed
    global bonus_origin
    global bonus_started_at
    global boss_health
    global boss_master
    global boss_player_x
    global boss_player_y
    global boss_aim_angle
    global boss_minion_cycle_index
    global last_boss_shot_time
    global last_boss_projectile_hit_time
    global camera_angle
    global camera_height
    global camera_mode
    global runner_lane
    global last_update_time
    global last_side_shot_time

    player_x = 0.0
    player_y = 0.0
    player_angle = 90.0
    gun_angle = 90.0

    player_life = MAX_LIFE
    game_score = 0
    weapon_level = 1
    shield_count = 0
    power_boost_end = 0.0
    boost_ready = False

    game_mode = "stage1"
    missed_bullets_since_bonus = 0
    bonus_life_trigger_armed = True
    bonus_origin = "stage1"
    bonus_started_at = 0.0

    boss_health = BOSS_MAX_HEALTH
    boss_master = None
    boss_minions.clear()
    boss_player_x = BOSS_PLAYER_START_X
    boss_player_y = BOSS_PLAYER_START_Y
    boss_aim_angle = BOSS_PLAYER_START_ANGLE
    boss_minion_cycle_index = 0
    last_boss_shot_time = 0.0
    last_boss_projectile_hit_time = -100.0
    boss_projectiles.clear()

    camera_angle = 0.0
    camera_height = 560.0
    camera_mode = "third_person"
    runner_lane = 1
    last_side_shot_time = 0.0

    bullets.clear()
    bonus_objects.clear()
    reset_stage1_monsters()
    reset_stage2()
    last_update_time = time.time()


def keyboardListener(key, x, y):
    global player_x
    global player_y
    global player_angle
    global gun_angle
    global runner_lane
    global stage2_player_x
    global stage2_facing
    global boss_player_x
    global boss_player_y
    global boss_aim_angle

    key = key.lower()

    if key == b'r':
        if game_mode in ("game_over", "win"):
            reset_game()
            glutPostRedisplay()
        return

    if game_mode in ("game_over", "win"):
        return

    if game_mode == "stage1":
        if key == b'w':
            angle_rad = math.radians(player_angle)
            player_x += math.cos(angle_rad) * player_speed
            player_y += math.sin(angle_rad) * player_speed
        elif key == b's':
            angle_rad = math.radians(player_angle)
            player_x -= math.cos(angle_rad) * player_speed
            player_y -= math.sin(angle_rad) * player_speed
        elif key == b'a':
            player_angle = normalize_angle(player_angle + turn_step)
            gun_angle = player_angle
        elif key == b'd':
            player_angle = normalize_angle(player_angle - turn_step)
            gun_angle = player_angle

        minimum = -GRID_LENGTH + 55.0
        maximum = GRID_LENGTH - 55.0
        player_x = max(minimum, min(maximum, player_x))
        player_y = max(minimum, min(maximum, player_y))

    elif game_mode == "stage2":
        if stair_transition is None:
            if key == b'a':
                stage2_player_x -= STAGE2_MOVE_STEP
                stage2_facing = -1
            elif key == b'd':
                stage2_player_x += STAGE2_MOVE_STEP
                stage2_facing = 1
            elif key == b'w':
                try_stage2_up()
            elif key == b's':
                try_stage2_down()
            stage2_player_x = max(
                -STAGE2_HALF_WIDTH + 25.0,
                min(STAGE2_HALF_WIDTH - 25.0, stage2_player_x)
            )

    elif game_mode == "boss":
        if key == b'a':
            boss_aim_angle = normalize_angle(boss_aim_angle + turn_step)
        elif key == b'd':
            boss_aim_angle = normalize_angle(boss_aim_angle - turn_step)
        elif key == b'w':
            angle_rad = math.radians(boss_aim_angle)
            boss_player_x += math.cos(angle_rad) * player_speed
            boss_player_y += math.sin(angle_rad) * player_speed
        elif key == b's':
            angle_rad = math.radians(boss_aim_angle)
            boss_player_x -= math.cos(angle_rad) * player_speed
            boss_player_y -= math.sin(angle_rad) * player_speed
        boss_player_x = max(
            -BOSS_ARENA_HALF_WIDTH + BOSS_ARENA_MARGIN,
            min(BOSS_ARENA_HALF_WIDTH - BOSS_ARENA_MARGIN,
                boss_player_x)
        )
        boss_player_y = max(
            -BOSS_ARENA_HALF_DEPTH + BOSS_ARENA_MARGIN,
            min(BOSS_ARENA_HALF_DEPTH - BOSS_ARENA_MARGIN,
                boss_player_y)
        )

    elif game_mode == "bonus":
        if key == b'a':
            runner_lane = max(0, runner_lane - 1)
        elif key == b'd':
            runner_lane = min(2, runner_lane + 1)

    glutPostRedisplay()


def specialKeyListener(key, x, y):
    global camera_angle
    global camera_height
    global runner_lane

    if game_mode == "stage1" and camera_mode == "third_person":
        if key == GLUT_KEY_UP:
            camera_height = min(MAX_CAMERA_HEIGHT,
                                camera_height + CAMERA_HEIGHT_STEP)
        elif key == GLUT_KEY_DOWN:
            camera_height = max(MIN_CAMERA_HEIGHT,
                                camera_height - CAMERA_HEIGHT_STEP)
        elif key == GLUT_KEY_LEFT:
            camera_angle = normalize_angle(camera_angle + CAMERA_ROTATION_STEP)
        elif key == GLUT_KEY_RIGHT:
            camera_angle = normalize_angle(camera_angle - CAMERA_ROTATION_STEP)

    elif game_mode == "bonus":
        if key == GLUT_KEY_LEFT:
            runner_lane = max(0, runner_lane - 1)
        elif key == GLUT_KEY_RIGHT:
            runner_lane = min(2, runner_lane + 1)

    glutPostRedisplay()


def mouseListener(button, state, x, y):
    global camera_mode

    if state != GLUT_DOWN:
        return

    if game_mode in ("stage1", "stage2", "boss"):
        if button == GLUT_LEFT_BUTTON:
            fire_bullet()
        elif button == GLUT_RIGHT_BUTTON and game_mode == "stage1":
            if camera_mode == "third_person":
                camera_mode = "first_person"
            else:
                camera_mode = "third_person"

    glutPostRedisplay()


def setupCamera():
    global camera_pos

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    scene_fov = fovY
    if game_mode == "stage1" and camera_mode == "first_person":
        scene_fov = 90
    elif game_mode == "stage2":
        scene_fov = 60
    elif game_mode in ("boss", "win"):
        scene_fov = 75

    gluPerspective(scene_fov, 1.25, 0.1, 3000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if game_mode == "bonus":
        camera_pos = (0, -330, 190)
        gluLookAt(0, -330, 190, 0, 180, 20, 0, 0, 1)
        return

    if game_mode == "stage2":
        camera_pos = (0, -620, 350)
        gluLookAt(0, -620, 350, 0, 0, 190, 0, 0, 1)
        return

    if game_mode in ("boss", "win"):
        camera_pos = (0, -900, 700)
        gluLookAt(0, -900, 700, 0, 0, 20, 0, 0, 1)
        return

    if camera_mode == "first_person" and game_mode == "stage1":
        view_rad = math.radians(player_angle)
        eye_x = player_x + math.cos(view_rad) * 8.0
        eye_y = player_y + math.sin(view_rad) * 8.0
        eye_z = 42.0
        look_x = eye_x + math.cos(view_rad) * 120.0
        look_y = eye_y + math.sin(view_rad) * 120.0
        camera_pos = (eye_x, eye_y, eye_z)
        gluLookAt(eye_x, eye_y, eye_z,
                  look_x, look_y, 36.0,
                  0, 0, 1)
        return

    angle_rad = math.radians(camera_angle)
    cam_x = camera_distance * math.sin(angle_rad)
    cam_y = -camera_distance * math.cos(angle_rad)
    cam_z = camera_height
    camera_pos = (cam_x, cam_y, cam_z)
    gluLookAt(cam_x, cam_y, cam_z, 0, 0, 0, 0, 0, 1)


def idle():
    global last_update_time

    current_time = time.time()
    delta_time = current_time - last_update_time
    last_update_time = current_time
    delta_time = min(delta_time, 0.05)

    if game_mode in ("stage1", "stage2", "boss"):
        if check_bonus_transition(current_time):
            glutPostRedisplay()
            return

    if game_mode == "stage1":
        update_stage1_monsters(delta_time, current_time)
        if game_mode == "stage1":
            update_stage1_bullets(delta_time, current_time)
        if game_mode == "stage1" and game_score >= STAGE1_SCORE_TARGET:
            start_stage2()
        if game_mode in ("stage1", "stage2"):
            check_bonus_transition(current_time)

    elif game_mode == "stage2":
        update_stage2(delta_time, current_time)
        if game_mode == "stage2":
            check_bonus_transition(current_time)

    elif game_mode == "boss":
        update_boss(delta_time, current_time)
        if game_mode == "boss":
            check_bonus_transition(current_time)

    elif game_mode == "bonus":
        update_bonus(delta_time, current_time)

    glutPostRedisplay()


def draw_common_combat_hud(stage_name):
    draw_text(10, 770, stage_name)
    draw_text(10, 740, "LIVES: " + str(player_life))
    draw_text(10, 710, "SCORE: " + str(game_score))
    draw_text(10, 680, "WEAPON LEVEL: " + str(weapon_level))
    draw_text(10, 650, "SHIELD: " + str(shield_count))
    draw_text(10, 620, "MISSED BULLETS: "
              + str(missed_bullets_since_bonus)
              + " / " + str(BONUS_MISS_TARGET))
    draw_text(10, 590, "BONUS: LIFE 4 OR 20 MISSES")


def draw_stage1_hud(current_time):
    draw_common_combat_hud("STAGE 1 - AMAZON JUNGLE")
    draw_text(10, 560, "WAVE: " + str(get_wave()))
    draw_text(10, 530, "NEXT STAGE AT SCORE: " + str(STAGE1_SCORE_TARGET))
    if boost_is_active(current_time):
        draw_text(10, 500, "POWER BOOST: ACTIVE", color=(1.0, 0.4, 1.0))


def draw_stage2_hud(current_time):
    draw_common_combat_hud("STAGE 2 - FLOOR " + str(active_floor + 1))
    enemies_left = len(stage2_floor_enemies[active_floor])
    draw_text(10, 560, "ENEMIES ON FLOOR: " + str(enemies_left))

    if stair_transition is not None:
        draw_text(335, 750, "CLIMBING...", color=(1.0, 0.85, 0.15))
    elif enemies_left == 0 and active_floor < 2:
        side = "RIGHT" if STAGE2_STAIR_X[active_floor] > 0 else "LEFT"
        draw_text(300, 750, side + " STAIRS UNLOCKED - PRESS W",
                  color=(0.2, 1.0, 0.4))
    elif active_floor == 2 and all(
        len(enemy_list) == 0 for enemy_list in stage2_floor_enemies
    ):
        draw_text(300, 750, "BOSS DOOR OPEN - PRESS W",
                  color=(0.2, 1.0, 0.4))

    if boost_is_active(current_time):
        draw_text(10, 530, "POWER BOOST: ACTIVE", color=(1.0, 0.4, 1.0))


def draw_boss_hud(current_time):
    draw_common_combat_hud("BOSS ARENA")
    draw_text(350, 750, "JUNGLE TITAN",
              color=(1.0, 0.2, 0.2))
    draw_text(350, 720, "MASTER LIFE: " + str(max(0, boss_health))
              + " / " + str(BOSS_MAX_HEALTH),
              color=(1.0, 0.2, 0.2))
    draw_text(350, 690, "ACTIVE MINIONS: " + str(len(boss_minions)))
    draw_text(350, 660, "GUN ANGLE: "
              + str(int(normalize_angle(boss_aim_angle))) + " DEGREES",
              color=(0.2, 0.9, 1.0))
    if boss_is_in_rage_phase():
        draw_text(350, 630, "RAGE PHASE - FASTER TITAN",
                  color=(1.0, 0.35, 0.05))
    else:
        draw_text(350, 630, "SINGLE FIRE PHASE",
                  color=(1.0, 0.75, 0.15))
    if boost_is_active(current_time):
        draw_text(350, 600, "POWER BOOST: ACTIVE", color=(1.0, 0.4, 1.0))


def draw_bonus_hud(current_time):
    remaining = max(0, int(math.ceil(
        BONUS_DURATION - (current_time - bonus_started_at)
    )))
    draw_text(10, 770, "BONUS STAGE - TEMPLE RUN")
    draw_text(10, 740, "TIME LEFT: " + str(remaining) + " SECONDS")
    draw_text(10, 710, "LIVES: " + str(player_life))
    draw_text(10, 680, "WEAPON LEVEL: " + str(weapon_level))
    draw_text(10, 650, "SHIELD: " + str(shield_count))
    draw_text(10, 620, "RETURNING TO: " + origin_label())
    draw_text(10, 590, "MISSED BULLETS RESET: 0 / 20")
    if boost_ready:
        draw_text(10, 560, "POWER BOOST COLLECTED",
                  color=(1.0, 0.4, 1.0))


def draw_stage1_scene(current_time, fallen=False):
    draw_jungle_ruins()
    draw_jungle_ground()
    draw_jungle_boundaries()
    draw_jungle_trees()
    draw_jungle_rocks()

    if camera_mode == "third_person" or fallen:
        draw_player_model(player_x, player_y, 0, player_angle, fallen)

    if not fallen:
        for monster in monsters:
            draw_monster(monster, get_monster_size(monster, current_time))
        for bullet in bullets:
            draw_bullet(bullet)


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    setupCamera()
    current_time = time.time()

    if game_mode == "stage1":
        draw_stage1_scene(current_time)
        draw_stage1_hud(current_time)

    elif game_mode == "stage2":
        draw_stage2_world()

        player_draw_x = stage2_player_position(current_time)
        player_draw_z = stage2_player_height(current_time)
        angle = 0.0 if stage2_facing > 0 else 180.0
        draw_player_model(player_draw_x, 0, player_draw_z, angle)

        for floor_index in range(3):
            for enemy in stage2_floor_enemies[floor_index]:
                draw_monster(
                    enemy,
                    get_monster_size(enemy, current_time),
                    STAGE2_FLOOR_Z[floor_index],
                )
        for bullet in bullets:
            draw_bullet(bullet)
        draw_stage2_hud(current_time)

    elif game_mode == "boss":
        draw_boss_arena()
        draw_player_model(
            boss_player_x, boss_player_y, 0, boss_aim_angle
        )

        if boss_master is not None:
            draw_fire_titan(boss_master, current_time)
        for minion in boss_minions:
            draw_monster(minion, get_monster_size(minion, current_time))
        for bullet in bullets:
            draw_bullet(bullet)
        for projectile in boss_projectiles:
            draw_boss_projectile(projectile)
        draw_boss_hud(current_time)

    elif game_mode == "bonus":
        draw_bonus_track()
        draw_bonus_sides()
        draw_bonus_player(current_time)
        for item in bonus_objects:
            draw_bonus_object(item)
        draw_bonus_hud(current_time)

    elif game_mode == "game_over":
        draw_stage1_scene(current_time, fallen=True)
        draw_text(330, 430, "MISSION FAILED", color=(0.0, 0.0, 0.0))
        draw_text(330, 400, "Final Score: " + str(game_score),
                  color=(0.0, 0.0, 0.0))
        draw_text(330, 370, "Press R to Restart", color=(0.0, 0.0, 0.0))

    elif game_mode == "win":
        draw_boss_arena()
        draw_player_model(
            boss_player_x, boss_player_y, 0, boss_aim_angle
        )
        draw_text(300, 440, "MISSION COMPLETE", color=(1.0, 0.9, 0.15))
        draw_text(300, 410, "Jungle Titan Defeated!",
                  color=(1.0, 1.0, 1.0))
        draw_text(300, 380, "Final Score: " + str(game_score),
                  color=(1.0, 1.0, 1.0))
        draw_text(300, 350, "Press R to Restart", color=(1.0, 1.0, 1.0))

    glutSwapBuffers()


def main():
    reset_game()
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Monster Hunter - Multi-Stage Jungle Survival")
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    glutMainLoop()


if __name__ == "__main__":
    main()
