import pygame as pg
import numpy as np
import sys
import pygame.gfxdraw
from time import time, sleep
from multiprocessing import Pool, Process
from multiprocessing.dummy import Pool as ThreadPool

rotate_x_z = []
rotate_y_z = []
cos = []
sin = []

for angle in range(360):
    angle = np.deg2rad(angle)
    c = np.cos(angle)
    s = np.sin(angle)
    cos.append(c)
    sin.append(s)
    rotate_x_z.append(np.array([
        [c, 0, -s],
        [0, 1, 0],
        [s, 0, c]
    ]))
    rotate_y_z.append(np.array([
        [1, 0, 0],
        [0, c, -s],
        [0, s, c]
    ]))


def generate_point_of_cube(center, size):
    half_size = size / 2
    points = np.array([
        [-1, -2, -1, 1],
        [1, -2, -1, 1],
        [1, 1, -1, 1],
        [-1, 1, -1, 1],
        [-1, -2, 1, 1],
        [1, -2, 1, 1],
        [1, 1, 1, 1],
        [-1, 1, 1, 1]
    ]).T
    transform_martice = np.array([
        [half_size, 0, 0, center[0]],
        [0, half_size, 0, center[1]],
        [0, 0, half_size, center[2]]
    ])
    return np.dot(transform_martice, points).T


def transform_points(points, f):
    points_x = points[..., 0]
    points_y = points[..., 1]
    points_z = (points[..., 2])
    points_z[points_z < 0.001] = 0.001
    return np.column_stack((points_x/points_z, points_y/points_z, np.ones(len(points))))


def save_surfaces(transformed_coordinates):
    return sorted([
        [[0, np.linalg.norm(transformed_coordinates[0]), transformed_coordinates[0][2]], [1, np.linalg.norm(transformed_coordinates[1]), transformed_coordinates[1][2]], [2, np.linalg.norm(transformed_coordinates[2]), transformed_coordinates[2][2]],
         [3, np.linalg.norm(transformed_coordinates[3]), transformed_coordinates[3][2]]],
        [[4, np.linalg.norm(transformed_coordinates[4]), transformed_coordinates[4][2]], [5, np.linalg.norm(transformed_coordinates[5]), transformed_coordinates[5][2]], [6, np.linalg.norm(transformed_coordinates[6]), transformed_coordinates[6][2]],
         [7, np.linalg.norm(transformed_coordinates[7]), transformed_coordinates[7][2]]],
        [[0, np.linalg.norm(transformed_coordinates[0]), transformed_coordinates[0][2]], [1, np.linalg.norm(transformed_coordinates[1]), transformed_coordinates[1][2]], [5, np.linalg.norm(transformed_coordinates[5]), transformed_coordinates[5][2]],
         [4, np.linalg.norm(transformed_coordinates[4]), transformed_coordinates[4][2]]],  # top
        [[2, np.linalg.norm(transformed_coordinates[2]), transformed_coordinates[2][2]], [3, np.linalg.norm(transformed_coordinates[3]), transformed_coordinates[3][2]], [7, np.linalg.norm(transformed_coordinates[7]), transformed_coordinates[7][2]],
         [6, np.linalg.norm(transformed_coordinates[6]), transformed_coordinates[6][2]]],  # buttom
        [[5, np.linalg.norm(transformed_coordinates[5]), transformed_coordinates[5][2]], [1, np.linalg.norm(transformed_coordinates[1]), transformed_coordinates[1][2]],[2, np.linalg.norm(transformed_coordinates[2]), transformed_coordinates[2][2]], [6, np.linalg.norm(transformed_coordinates[6]), transformed_coordinates[6][2]],],
        [[4, np.linalg.norm(transformed_coordinates[4]), transformed_coordinates[4][2]], [0, np.linalg.norm(transformed_coordinates[0]), transformed_coordinates[0][2]],[3, np.linalg.norm(transformed_coordinates[3]), transformed_coordinates[3][2]], [7, np.linalg.norm(transformed_coordinates[7]), transformed_coordinates[7][2]],]
    ], key=lambda x: np.mean(x, axis=0)[1], reverse=True)[-3:]


def draw_surface(surface, quad, img):
    points = dict()
    w = img.get_size()[0]
    h = img.get_size()[1]

    for i in range(h + 1):
        b = quad[1][0] + i / h * (quad[2][0] - quad[1][0]), quad[1][1] + i / h * (quad[2][1] - quad[1][1])
        c = quad[0][0] + i / h * (quad[3][0] - quad[0][0]), quad[0][1] + i / h * (quad[3][1] - quad[0][1])
        # b = lerp2d(quad[1], quad[2], i / h)
        # c = lerp2d(quad[0], quad[3], i / h)
        for u in range(w + 1):
            # a = lerp2d(c, b, u / w)
            points[(u, i)] = c[0] + u / w * (b[0] - c[0]), c[1] + u / w * (b[1] - c[1])
    for x in range(w):
        for y in range(h):
            pygame.draw.polygon(
                surface,
                img.get_at((x, y)),
                [points[(a, b)] for a, b in [(x, y), (x, y + 1), (x + 1, y + 1), (x + 1, y)]]
            )


def draw_cube(screen, points, angle_x_z, angle_y_z, player_position, f, K, side, top, buttom):
    global rotate_x_z, rotate_y_z
    transformed_points = np.dot(np.dot(points - player_position, rotate_x_z[int(angle_x_z)]), rotate_y_z[int(angle_y_z)])
    surfaces = save_surfaces(transformed_points)
    points_2d = np.dot(transform_points(transformed_points, f), K)
    f = 0
    for index, surface in enumerate(surfaces):
        if surface[0][2] > f and surface[1][2] > f and surface[2][2] > f and surface[3][2] > f:
            p = []
            for point, _, _ in surface:
                p.append(points_2d[point])
            if surface[0][0] == 0 and surface[1][0] == 1 and surface[2][0] == 5 and surface[3][0] == 4:
                draw_surface(screen, p, top)
            elif surface[0][0] == 2 and surface[1][0] == 3 and surface[2][0] == 7 and surface[3][0] == 6:
                draw_surface(screen, p, buttom)
            else:
                draw_surface(screen, p, side)


width, height = 1024, 700
resolution = 5, 5
grass_top = pg.transform.scale(pg.image.load('src/grass_top.png'), resolution)
grass_side = pg.transform.scale(pg.image.load('src/grass_side.png'), resolution)
log_top = pg.transform.scale(pg.image.load('src/log_oak_t.png'), resolution)
log_side = pg.transform.scale(pg.image.load('src/log_oak_s.png'), resolution)
def main():
    # cubes = [
    #     {'center': np.array((0, 2, 0)), 'points': generate_point_of_cube((0, 2, 0), 2), 'top': grass_top, 'side': grass_side, 'buttom': grass_top},
    #     {'center': np.array((2, 2, 0)), 'points': generate_point_of_cube((2, 2, 0), 2), 'top': grass_top, 'side': grass_side, 'buttom': grass_top},
    #     {'center': np.array((0, 2, 2)), 'points': generate_point_of_cube((0, 2, 2), 2), 'top': grass_top, 'side': grass_side, 'buttom': grass_top},
    #     {'center': np.array((2, 2, 2)), 'points': generate_point_of_cube((2, 2, 2), 2), 'top': grass_top, 'side': grass_side, 'buttom': grass_top},
    #     {'center': np.array((2, 0, 2)), 'points': generate_point_of_cube((2, 0, 2), 2), 'top': grass_top, 'side': grass_side, 'buttom': grass_top},
    # ]
    cubes = [
        {'center': np.array((0, 2, 0)), 'points': generate_point_of_cube((0, 2, 0), 2), 'top': grass_top, 'side': grass_side, 'buttom': grass_top},
        {'center': np.array((2, 2, 0)), 'points': generate_point_of_cube((2, 2, 0), 2), 'top': grass_top, 'side': grass_side, 'buttom': grass_top},
        {'center': np.array((0, 2, 2)), 'points': generate_point_of_cube((0, 2, 2), 2), 'top': grass_top, 'side': grass_side, 'buttom': grass_top},
        {'center': np.array((2, 2, 2)), 'points': generate_point_of_cube((2, 2, 2), 2), 'top': grass_top, 'side': grass_side, 'buttom': grass_top},
        {'center': np.array((2, 0, 2)), 'points': generate_point_of_cube((2, 0, 2), 2), 'top': grass_top, 'side': grass_side, 'buttom': grass_top},
        {'center': np.array((4, -2, 2)), 'points': generate_point_of_cube((4, -2, 2), 2), 'top': grass_top, 'side': grass_side, 'buttom': grass_top},

        {'center': np.array((10, -4, 0)), 'points': generate_point_of_cube((10, -4, 0), 2), 'top': log_top, 'side': log_side, 'buttom': log_top},
        {'center': np.array((12, -4, 0)), 'points': generate_point_of_cube((12, -4, 0), 2), 'top': log_top, 'side': log_side, 'buttom': log_top},
        {'center': np.array((10, -4, 2)), 'points': generate_point_of_cube((10, -4, 2), 2), 'top': log_top, 'side': log_side, 'buttom': log_top},
        {'center': np.array((12, -4, 2)), 'points': generate_point_of_cube((12, -4, 2), 2), 'top': log_top, 'side': log_side, 'buttom': log_top},
        {'center': np.array((14, -4, 0)), 'points': generate_point_of_cube((14, -4, 0), 2), 'top': log_top, 'side': log_side, 'buttom': log_top},
        {'center': np.array((14, -4, 2)), 'points': generate_point_of_cube((14, -4, 2), 2), 'top': log_top, 'side': log_side, 'buttom': log_top},
        {'center': np.array((10, -4, 4)), 'points': generate_point_of_cube((10, -4, 4), 2), 'top': log_top, 'side': log_side, 'buttom': log_top},
        {'center': np.array((12, -4, 4)), 'points': generate_point_of_cube((12, -4, 4), 2), 'top': log_top, 'side': log_side, 'buttom': log_top},
        {'center': np.array((14, -4, 4)), 'points': generate_point_of_cube((14, -4, 4), 2), 'top': log_top, 'side': log_side, 'buttom': log_top},

        {'center': np.array((8, -2, 0)), 'points': generate_point_of_cube((8, -2, 0), 2), 'top': log_top, 'side': log_side, 'buttom': log_top},
        {'center': np.array((8, 0, 0)), 'points': generate_point_of_cube((8, 0, 0), 2), 'top': log_top, 'side': log_side, 'buttom': log_top},
        {'center': np.array((8, 2, 0)), 'points': generate_point_of_cube((8, 2, 0), 2), 'top': log_top, 'side': log_side, 'buttom': log_top},

        {'center': np.array((8, -2, 2)), 'points': generate_point_of_cube((8, -2, 2), 2), 'top': log_top, 'side': log_side, 'buttom': log_top},
        {'center': np.array((8, 0, 2)), 'points': generate_point_of_cube((8, 0, 2), 2), 'top': log_top, 'side': log_side, 'buttom': log_top},
        {'center': np.array((8, 2, 2)), 'points': generate_point_of_cube((8, 2, 2), 2), 'top': log_top, 'side': log_side, 'buttom': log_top},

        {'center': np.array((8, -2, 4)), 'points': generate_point_of_cube((8, -2, 4), 2), 'top': log_top, 'side': log_side, 'buttom': log_top},
        {'center': np.array((8, 0, 4)), 'points': generate_point_of_cube((8, 0, 4), 2), 'top': log_top, 'side': log_side, 'buttom': log_top},
        {'center': np.array((8, 2, 4)), 'points': generate_point_of_cube((8, 2, 4), 2), 'top': log_top, 'side': log_side, 'buttom': log_top},
        # ---------------------------
        {'center': np.array((16, -2, 0)), 'points': generate_point_of_cube((16, -2, 0), 2), 'top': log_top, 'side': log_side, 'buttom': log_top},
        {'center': np.array((16, 0, 0)), 'points': generate_point_of_cube((16, 0, 0), 2), 'top': log_top, 'side': log_side, 'buttom': log_top},
        {'center': np.array((16, 2, 0)), 'points': generate_point_of_cube((16, 2, 0), 2), 'top': log_top, 'side': log_side, 'buttom': log_top},

        {'center': np.array((16, -2, 2)), 'points': generate_point_of_cube((16, -2, 2), 2), 'top': log_top, 'side': log_side, 'buttom': log_top},
        {'center': np.array((16, 0, 2)), 'points': generate_point_of_cube((16, 0, 2), 2), 'top': log_top, 'side': log_side, 'buttom': log_top},
        {'center': np.array((16, 2, 2)), 'points': generate_point_of_cube((16, 2, 2), 2), 'top': log_top, 'side': log_side, 'buttom': log_top},

        {'center': np.array((16, -2, 4)), 'points': generate_point_of_cube((16, -2, 4), 2), 'top': log_top, 'side': log_side, 'buttom': log_top},
        {'center': np.array((16, 0, 4)), 'points': generate_point_of_cube((16, 0, 4), 2), 'top': log_top, 'side': log_side, 'buttom': log_top},
        {'center': np.array((16, 2, 4)), 'points': generate_point_of_cube((16, 2, 4), 2), 'top': log_top, 'side': log_side, 'buttom': log_top},

        #-----------------------------------------
    ]
    player_position = [0, 0, -10]
    f = 4
    alpha = 100
    beta = 100
    angle_x_z = 0
    angle_y_z = 0

    jump_force = 0
    jump_reduce = 0.05
    gravity = 1.2
    pg.init()
    screen_info = pygame.display.Info()
    width, height = screen_info.current_w, screen_info.current_h
    print(width, height)
    # width, height = 1024, 700
    screen = pg.display.set_mode((width, height))
    u0 = width//2
    v0 = height//2
    K = np.array([[f * alpha, 0, u0], [0, f * beta, v0]]).T
    clock = pg.time.Clock()

    past_mouse = pg.mouse.get_pos()
    pg.mouse.set_visible(False)
    cursor = pg.transform.scale(pg.image.load("src/cursor.png"), (10, 10))
    font = pg.font.Font("fonts/Comfortaa-Bold.ttf", 15)
    font2 = pg.font.Font("fonts/Comfortaa-Bold.ttf", 80)
    font3 = pg.font.Font("fonts/Comfortaa-Bold.ttf", 82)
    font.set_bold(True)
    font2.set_bold(True)
    font3.set_bold(True)
    start = False
    t = time()
    while True:

        if not start:
            pg.mouse.set_pos(screen.get_width() / 2, screen.get_height() / 2)
            y_center = angle_y_z
        else:
            # print(angle_y_z)
            # print(angle_x_z)
            print("--------------------")
        if time() - t >= 5:
            start = True
        movement_speed = .08 * 60 / (clock.get_fps() + 0.00001)
        rotation_speed = .8 * 60 / (clock.get_fps() + 0.00001)
        screen.fill((0, 0, 0))
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN:
                if start and event.key == pg.K_RETURN:
                    pg.mouse.set_pos(screen.get_width() / 2, screen.get_height() / 2)
                elif event.key == pg.K_ESCAPE:
                    sys.exit()
        mouse = pg.mouse.get_pos()
        # mouse_x = max(min(mouse[0], screen.get_width() - 1), 1)
        # mouse_y = max(min(mouse[1], screen.get_height() - 1), 1)
        # mouse_x = 1 if mouse_x == 0 else mouse_x
        # mouse_y = 1 if mouse_y == 0 else mouse_y
        # pygame.mouse.set_pos((mouse_x, mouse_y))
        if start and past_mouse[0] - mouse[0] != 0:
            if mouse[0] == 0:
                pg.mouse.set_pos(screen.get_width() - 5, mouse[1])
                mouse = screen.get_width() - 5, mouse[1]
            else:
                move_x = past_mouse[0] - mouse[0]
                angle_x_z += rotation_speed * move_x * .4
        if start and past_mouse[1] - mouse[1] != 0:
            if mouse[0] == screen.get_width() - 1:
                pg.mouse.set_pos(1, mouse[1])
                mouse = 1, mouse[1]
            else:
                move_y = past_mouse[1] - mouse[1]
                angle_y_z += rotation_speed * move_y * .4
                if 60 <= angle_y_z <= 100:
                    angle_y_z = 60
                elif 200 <= angle_y_z <= 300:
                    angle_y_z = 300

            # angle_y_z = max(min(angle_y_z % 360, y_center + 100), y_center - 100)
            # print(angle_y_z)
        past_mouse = mouse
        keys = pg.key.get_pressed()
        # angle_x_z = max(0, angle_x_z)
        # angle_x_z = min(359, angle_x_z)
        # angle_x_z = 358 if angle_x_z == 0 else angle_x_z
        # angle_x_z = 1 if angle_x_z == 359 else angle_x_z
        angle_x_z %= 360
        angle_y_z %= 360
        if start:
            if keys[pg.K_a]:
                player_position[2] -= movement_speed * sin[int(angle_x_z)]
                player_position[0] -= movement_speed * cos[int(angle_x_z)]
            if keys[pg.K_d]:
                player_position[2] += movement_speed * sin[int(angle_x_z)]
                player_position[0] += movement_speed * cos[int(angle_x_z)]
            if keys[pg.K_w]:
                player_position[2] += movement_speed * cos[int(angle_x_z)]
                player_position[0] -= movement_speed * sin[int(angle_x_z)]
            if keys[pg.K_s]:
                player_position[2] -= movement_speed * cos[int(angle_x_z)]
                player_position[0] += movement_speed * sin[int(angle_x_z)]
            if keys[pg.K_SPACE]:
                # player_position[1] -= movement_speed
                if jump_force == 0:
                    jump_force = 1.8
            if pg.key.get_mods() & pg.KMOD_SHIFT:
                player_position[1] += movement_speed
            if keys[pg.K_LEFT]:
                angle_x_z += rotation_speed
            if keys[pg.K_RIGHT]:
                angle_x_z -= rotation_speed
            if keys[pg.K_UP]:
                angle_y_z += rotation_speed
            if keys[pg.K_DOWN]:
                angle_y_z -= rotation_speed
        jump_force = max(0, jump_force-jump_reduce)
        if jump_force != 0:
            player_position[1] = min(0, player_position[1]-jump_force+gravity)
        angle_x_z %= 360
        angle_y_z %= 360
        up = False
        for index, cube in enumerate(cubes):
            test = np.abs(cube["center"] - player_position - [0, 1, 0])
            if np.all(test <= [1, 1, 1]):
                jump_force = 0
                player_position[1] = cube["center"][1] - 4
            test = np.abs(cube["center"] - player_position - [0, 3, 0])
            if np.all(test <= [1, 1, 1]):
                up = True
        if not up and player_position[1] != 0 and jump_force == 0:
            player_position[1] = player_position[1] + 0.6
        if player_position[1] >= 0:
            player_position[1] = 0

        cubes.sort(key=lambda x: np.linalg.norm(np.dot(np.dot(x.get('center') - player_position, rotate_x_z[int(angle_x_z)]), rotate_y_z[int(angle_y_z)])), reverse=True)

        for cube in cubes:
            draw_cube(screen, cube.get('points'), angle_x_z, angle_y_z, player_position, f, K, cube.get('side'), cube.get('top'), cube.get('buttom'))

        clock.tick(60000)
        # pg.display.set_caption(str(round(clock.get_fps())))
        screen.blit(cursor, (screen.get_width() / 2 - cursor.get_width() / 2, screen.get_height() / 2 - cursor.get_height() /2))
        screen.blit(font.render(str(round(clock.get_fps())), True, (255, 255, 255)), (2, 2))
        if not start:
            screen.blit(font3.render("loading", True, (255, 0, 0)), (screen.get_width() / 2 - font2.size("loading")[0] / 2 - 4, screen.get_height() / 2 - font2.size("loading")[1] / 2 - 4))
            screen.blit(font2.render("loading", True, (255, 255, 255)), (screen.get_width() / 2 - font2.size("loading")[0] / 2, screen.get_height() / 2 - font2.size("loading")[1] / 2))

        pg.display.update()


if __name__ == '__main__':
    main()



