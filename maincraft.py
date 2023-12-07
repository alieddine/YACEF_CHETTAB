import pygame as pg
import numpy as np
import sys
import pygame.gfxdraw
from time import time

from network import Network


class Main_interface:
    def __init__(self):
        pg.init()
        self.width, self.height = 1024, 700
        self.resolution = 4, 4
        self.grass_top = pg.transform.scale(pg.image.load('src/grass_top.png'), self.resolution)
        self.grass_side = pg.transform.scale(pg.image.load('src/grass_side.png'), self.resolution)
        self.log_top = pg.transform.scale(pg.image.load('src/log_oak_t.png'), self.resolution)
        self.log_side = pg.transform.scale(pg.image.load('src/log_oak_s.png'), self.resolution)
        self.player_back = pg.transform.scale(pg.image.load('src/player_back.png'), self.resolution)
        self.player_side = pg.transform.scale(pg.image.load('src/player_side.png'), self.resolution)
        self.player_front = pg.transform.scale(pg.image.load('src/player_front.png'), self.resolution)
        self.player_bottom = pg.transform.scale(pg.image.load('src/player_front.png'), self.resolution)
        self.rotate_x_z = []
        self.rotate_y_z = []
        self.cos = []
        self.sin = []
        self.cubes = [
            {'center': np.array((0, 2, 0)), 'points': generate_point_of_cube((0, 2, 0), 2), 'top': self.grass_top, 'side': self.grass_side, 'buttom': self.grass_top},
            {'center': np.array((2, 2, 0)), 'points': generate_point_of_cube((2, 2, 0), 2), 'top': self.grass_top, 'side': self.grass_side, 'buttom': self.grass_top},
            {'center': np.array((0, 2, 2)), 'points': generate_point_of_cube((0, 2, 2), 2), 'top': self.grass_top, 'side': self.grass_side, 'buttom': self.grass_top},
            {'center': np.array((2, 2, 2)), 'points': generate_point_of_cube((2, 2, 2), 2), 'top': self.grass_top, 'side': self.grass_side, 'buttom': self.grass_top},
            {'center': np.array((2, 0, 2)), 'points': generate_point_of_cube((2, 0, 2), 2), 'top': self.grass_top, 'side': self.grass_side, 'buttom': self.grass_top},
            {'center': np.array((4, -2, 2)), 'points': generate_point_of_cube((4, -2, 2), 2), 'top': self.grass_top, 'side': self.grass_side, 'buttom': self.grass_top},

            {'center': np.array((10, -4, 0)), 'points': generate_point_of_cube((10, -4, 0), 2), 'top': self.log_top, 'side': self.log_side, 'buttom': self.log_top},
            {'center': np.array((12, -4, 0)), 'points': generate_point_of_cube((12, -4, 0), 2), 'top': self.log_top, 'side': self.log_side, 'buttom': self.log_top},
            {'center': np.array((10, -4, 2)), 'points': generate_point_of_cube((10, -4, 2), 2), 'top': self.log_top, 'side': self.log_side, 'buttom': self.log_top},
            {'center': np.array((12, -4, 2)), 'points': generate_point_of_cube((12, -4, 2), 2), 'top': self.log_top, 'side': self.log_side, 'buttom': self.log_top},
            {'center': np.array((14, -4, 0)), 'points': generate_point_of_cube((14, -4, 0), 2), 'top': self.log_top, 'side': self.log_side, 'buttom': self.log_top},
            {'center': np.array((14, -4, 2)), 'points': generate_point_of_cube((14, -4, 2), 2), 'top': self.log_top, 'side': self.log_side, 'buttom': self.log_top},
            {'center': np.array((10, -4, 4)), 'points': generate_point_of_cube((10, -4, 4), 2), 'top': self.log_top, 'side': self.log_side, 'buttom': self.log_top},
            {'center': np.array((12, -4, 4)), 'points': generate_point_of_cube((12, -4, 4), 2), 'top': self.log_top, 'side': self.log_side, 'buttom': self.log_top},
            {'center': np.array((14, -4, 4)), 'points': generate_point_of_cube((14, -4, 4), 2), 'top': self.log_top, 'side': self.log_side, 'buttom': self.log_top},

            {'center': np.array((8, -2, 0)), 'points': generate_point_of_cube((8, -2, 0), 2), 'top': self.log_top, 'side': self.log_side, 'buttom': self.log_top},
            {'center': np.array((8, 0, 0)), 'points': generate_point_of_cube((8, 0, 0), 2), 'top': self.log_top, 'side': self.log_side, 'buttom': self.log_top},
            {'center': np.array((8, 2, 0)), 'points': generate_point_of_cube((8, 2, 0), 2), 'top': self.log_top, 'side': self.log_side, 'buttom': self.log_top},

            {'center': np.array((8, -2, 2)), 'points': generate_point_of_cube((8, -2, 2), 2), 'top': self.log_top, 'side': self.log_side, 'buttom': self.log_top},
            {'center': np.array((8, 0, 2)), 'points': generate_point_of_cube((8, 0, 2), 2), 'top': self.log_top, 'side': self.log_side, 'buttom': self.log_top},
            {'center': np.array((8, 2, 2)), 'points': generate_point_of_cube((8, 2, 2), 2), 'top': self.log_top, 'side': self.log_side, 'buttom': self.log_top},

            {'center': np.array((8, -2, 4)), 'points': generate_point_of_cube((8, -2, 4), 2), 'top': self.log_top, 'side': self.log_side, 'buttom': self.log_top},
            {'center': np.array((8, 0, 4)), 'points': generate_point_of_cube((8, 0, 4), 2), 'top': self.log_top, 'side': self.log_side, 'buttom': self.log_top},
            {'center': np.array((8, 2, 4)), 'points': generate_point_of_cube((8, 2, 4), 2), 'top': self.log_top, 'side': self.log_side, 'buttom': self.log_top},
            # ---------------------------
            {'center': np.array((16, -2, 0)), 'points': generate_point_of_cube((16, -2, 0), 2), 'top': self.log_top, 'side': self.log_side, 'buttom': self.log_top},
            {'center': np.array((16, 0, 0)), 'points': generate_point_of_cube((16, 0, 0), 2), 'top': self.log_top, 'side': self.log_side, 'buttom': self.log_top},
            {'center': np.array((16, 2, 0)), 'points': generate_point_of_cube((16, 2, 0), 2), 'top': self.log_top, 'side': self.log_side, 'buttom': self.log_top},

            {'center': np.array((16, -2, 2)), 'points': generate_point_of_cube((16, -2, 2), 2), 'top': self.log_top, 'side': self.log_side, 'buttom': self.log_top},
            {'center': np.array((16, 0, 2)), 'points': generate_point_of_cube((16, 0, 2), 2), 'top': self.log_top, 'side': self.log_side, 'buttom': self.log_top},
            {'center': np.array((16, 2, 2)), 'points': generate_point_of_cube((16, 2, 2), 2), 'top': self.log_top, 'side': self.log_side, 'buttom': self.log_top},

            {'center': np.array((16, -2, 4)), 'points': generate_point_of_cube((16, -2, 4), 2), 'top': self.log_top, 'side': self.log_side, 'buttom': self.log_top},
            {'center': np.array((16, 0, 4)), 'points': generate_point_of_cube((16, 0, 4), 2), 'top': self.log_top, 'side': self.log_side, 'buttom': self.log_top},
            {'center': np.array((16, 2, 4)), 'points': generate_point_of_cube((16, 2, 4), 2), 'top': self.log_top, 'side': self.log_side, 'buttom': self.log_top},

            # -----------------------------------------
        ]
        self.player_position = []
        self.f = 4
        self.alpha = 100
        self.beta = 100
        self.angle_x_z = 0
        self.angle_y_z = 0
        self.jump_force = 0
        self.jump_reduce = 0.05
        self.gravity = 1.2
        self.screen_info = pygame.display.Info()
        self.width, height = self.screen_info.current_w, self.screen_info.current_h

        self.network = Network()

        self.screen = pg.display.set_mode((self.width, height), pg.FULLSCREEN)
        self.u0 = self.width // 2
        self.v0 = height // 2
        self.K = np.array([[self.f * self.alpha, 0, self.u0], [0, self.f * self.beta, self.v0]]).T
        self.clock = pg.time.Clock()
        self.font = pg.font.Font("fonts/Comfortaa-Bold.ttf", 15)
        self.font2 = pg.font.Font("fonts/Comfortaa-Bold.ttf", 80)
        self.font3 = pg.font.Font("fonts/Comfortaa-Bold.ttf", 82)
        self.font.set_bold(True)
        self.font2.set_bold(True)
        self.font3.set_bold(True)
        pg.event.set_grab(True)
        self.other_players_pos = []
        self.other_players = []
        for angle in range(360):
            angle = np.deg2rad(angle)
            c = np.cos(angle)
            s = np.sin(angle)
            self.cos.append(c)
            self.sin.append(s)
            self.rotate_x_z.append(np.array([
                [c, 0, -s],
                [0, 1, 0],
                [s, 0, c]
            ]))
            self.rotate_y_z.append(np.array([
                [1, 0, 0],
                [0, c, -s],
                [0, s, c]
            ]))


def generate_point_of_cube(center, size):
    half_size = size / 2
    points = np.array([
        [-1, -1, -1, 1],
        [1, -1, -1, 1],
        [1, 1, -1, 1],
        [-1, 1, -1, 1],
        [-1, -1, 1, 1],
        [1, -1, 1, 1],
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
    return np.column_stack((points_x / points_z, points_y / points_z, np.ones(len(points))))


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
        [[5, np.linalg.norm(transformed_coordinates[5]), transformed_coordinates[5][2]], [1, np.linalg.norm(transformed_coordinates[1]), transformed_coordinates[1][2]], [2, np.linalg.norm(transformed_coordinates[2]), transformed_coordinates[2][2]], [6, np.linalg.norm(transformed_coordinates[6]), transformed_coordinates[6][2]], ],
        [[4, np.linalg.norm(transformed_coordinates[4]), transformed_coordinates[4][2]], [0, np.linalg.norm(transformed_coordinates[0]), transformed_coordinates[0][2]], [3, np.linalg.norm(transformed_coordinates[3]), transformed_coordinates[3][2]], [7, np.linalg.norm(transformed_coordinates[7]), transformed_coordinates[7][2]], ]
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


def draw_cube(screen, points, main_interface, side, top, buttom, front=None, back=None):
    transformed_points = np.dot(np.dot(points - main_interface.player_position, main_interface.rotate_x_z[int(main_interface.angle_x_z)]), main_interface.rotate_y_z[int(main_interface.angle_y_z)])
    surfaces = save_surfaces(transformed_points)
    points_2d = np.dot(transform_points(transformed_points, main_interface.f), main_interface.K)
    f = 0
    for index, surface in enumerate(surfaces):
        if surface[0][2] > f and surface[1][2] > f and surface[2][2] > f and surface[3][2] > f:
            p = []
            for point, _, _ in surface:
                p.append(points_2d[point])
            if surface[0][0] == 0 and surface[1][0] == 1 and surface[2][0] == 5 and surface[3][0] == 4:
                draw_surface(screen, p, top)
            elif front is not None and surface[0][0] == 0 and surface[1][0] == 1 and surface[2][0] == 3 and surface[3][0] == 2:
                draw_surface(screen, p, front)
            elif back is not None and surface[0][0] == 4 and surface[1][0] == 5 and surface[2][0] == 6 and surface[3][0] == 7:
                draw_surface(screen, p, front)
            elif surface[0][0] == 2 and surface[1][0] == 3 and surface[2][0] == 7 and surface[3][0] == 6:
                draw_surface(screen, p, buttom)
            else:
                draw_surface(screen, p, side)



def read_pos(string):
    print(string)

    if string == "NO_PLAYERS":
        return []
    string = string.split(":")
    print(string)

    decode = []
    for element in string:
        element = element.split(",")
        decode.append([float(element[0]), float(element[1]), float(element[2])])
    print(decode)

    return decode


def make_pos(tup):
    return str(tup[0]) + "," + str(tup[1]) + "," + str(tup[2])


def main_interface():
    pg.init()

    main = Main_interface()

    past_mouse = pg.mouse.get_pos()
    pg.mouse.set_visible(False)
    cursor = pg.transform.scale(pg.image.load("src/cursor.png"), (10, 10))

    start = False
    main.player_position = read_pos(main.network.getPos())[0]
    t = time()
    nmr_of_players = 0
    while True:
        if nmr_of_players == 0:
            print(main.other_players_pos)
            print("lol")
            print(main.player_position)

            main.other_players_pos = read_pos(main.network.send(make_pos(main.player_position)))
            print(main.other_players_pos)

            if len(main.other_players_pos) == 0:
                print("no players")
            elif nmr_of_players != len(main.other_players_pos):
                main.other_players = []
                for element in main.other_players_pos:
                    main.other_players.append({'center': np.array((element[0], element[1], element[2])), 'points': generate_point_of_cube((element[0], element[1], element[2]), 1), 'top': main.player_back, 'side': main.player_side, 'buttom': main.player_bottom, 'front': main.player_front})
            else:
                for index, element in enumerate(main.other_players):
                    main.other_players['center'][0] = main.other_players_pos[0]
                    main.other_players['center'][1] = main.other_players_pos[1]
                    main.other_players['center'][2] = main.other_players_pos[2]


        if not start:
            pg.mouse.set_pos(main.screen.get_width() / 2, main.screen.get_height() / 2)
        if time() - t >= 5:
            start = True
        main.movement_speed = .08 * 60 / (main.clock.get_fps() + 0.00001)
        main.rotation_speed = .8 * 60 / (main.clock.get_fps() + 0.00001)
        main.screen.fill((0, 0, 0))
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN:
                if start and event.key == pg.K_RETURN:
                    pg.mouse.set_pos(main.screen.get_width() / 2, main.screen.get_height() / 2)
                elif event.key == pg.K_ESCAPE:
                    sys.exit()
        mouse = pg.mouse.get_pos()

        if start and past_mouse[0] - mouse[0] != 0:
            if mouse[0] == 0:
                pg.mouse.set_pos(main.screen.get_width() - 5, mouse[1])
                mouse = main.screen.get_width() - 5, mouse[1]
            else:
                move_x = past_mouse[0] - mouse[0]
                main.angle_x_z += main.rotation_speed * move_x * .4
        if start and past_mouse[1] - mouse[1] != 0:
            if mouse[0] == main.screen.get_width() - 1:
                pg.mouse.set_pos(1, mouse[1])
                mouse = 1, mouse[1]
            else:
                move_y = past_mouse[1] - mouse[1]
                main.angle_y_z += main.rotation_speed * move_y * .4
                if 60 <= main.angle_y_z <= 100:
                    main.angle_y_z = 60
                elif 200 <= main.angle_y_z <= 300:
                    main.angle_y_z = 300
        past_mouse = mouse
        keys = pg.key.get_pressed()
        main.angle_x_z %= 360
        main.angle_y_z %= 360
        if start:
            if keys[pg.K_a]:
                main.player_position[2] -= main.movement_speed * main.sin[int(main.angle_x_z)]
                main.player_position[0] -= main.movement_speed * main.cos[int(main.angle_x_z)]
            if keys[pg.K_d]:
                main.player_position[2] += main.movement_speed * main.sin[int(main.angle_x_z)]
                main.player_position[0] += main.movement_speed * main.cos[int(main.angle_x_z)]
            if keys[pg.K_w]:
                main.player_position[2] += main.movement_speed * main.cos[int(main.angle_x_z)]
                main.player_position[0] -= main.movement_speed * main.sin[int(main.angle_x_z)]
            if keys[pg.K_s]:
                main.player_position[2] -= main.movement_speed * main.cos[int(main.angle_x_z)]
                main.player_position[0] += main.movement_speed * main.sin[int(main.angle_x_z)]
            if keys[pg.K_SPACE]:
                # player_position[1] -= movement_speed
                if main.jump_force == 0:
                    main.jump_force = 1.8
            if pg.key.get_mods() & pg.KMOD_SHIFT:
                main.player_position[1] += main.movement_speed
            if keys[pg.K_LEFT]:
                main.angle_x_z += main.rotation_speed
            if keys[pg.K_RIGHT]:
                main.angle_x_z -= main.rotation_speed
            if keys[pg.K_UP]:
                main.angle_y_z += main.rotation_speed
            if keys[pg.K_DOWN]:
                main.angle_y_z -= main.rotation_speed
        main.jump_force = max(0, main.jump_force - main.jump_reduce)
        if main.jump_force != 0:
            main.player_position[1] = min(0, main.player_position[1] - main.jump_force + main.gravity)
        main.angle_x_z %= 360
        main.angle_y_z %= 360
        up = False
        for index, cube in enumerate(main.cubes):
            test = np.abs(cube["center"] - main.player_position - [0, 1, 0])
            if np.all(test <= [1, 1, 1]):
                main.jump_force = 0
                main.player_position[1] = cube["center"][1] - 4
            test = np.abs(cube["center"] - main.player_position - [0, 3, 0])
            if np.all(test <= [1, 1, 1]):
                up = True
        if not up and main.player_position[1] != 0 and main.jump_force == 0:
            main.player_position[1] = main.player_position[1] + 0.6
        if main.player_position[1] >= 0:
            main.player_position[1] = 0

        main.cubes.sort(key=lambda x: np.linalg.norm(np.dot(np.dot(x.get('center') - main.player_position, main.rotate_x_z[int(main.angle_x_z)]), main.rotate_y_z[int(main.angle_y_z)])), reverse=True)

        for cube in main.cubes:
            draw_cube(main.screen, cube.get('points'), main, cube.get('side'), cube.get('top'), cube.get('buttom'))
        for player in main.other_players:
            draw_cube(main.screen, player.get('points'), main, player.get('side'), player.get('top'), player.get('buttom'), player.get('front'), player.get('top'))
        main.clock.tick(60000)
        # pg.display.set_caption(str(round(clock.get_fps())))
        main.screen.blit(cursor, (main.screen.get_width() / 2 - cursor.get_width() / 2, main.screen.get_height() / 2 - cursor.get_height() / 2))
        main.screen.blit(main.font.render(str(round(main.clock.get_fps())), True, (255, 255, 255)), (2, 2))
        if not start:
            main.screen.blit(main.font3.render("loading", True, (255, 0, 0)), (main.screen.get_width() / 2 - main.font2.size("loading")[0] / 2 - 4, main.screen.get_height() / 2 - main.font2.size("loading")[1] / 2 - 4))
            main.screen.blit(main.font2.render("loading", True, (255, 255, 255)), (main.screen.get_width() / 2 - main.font2.size("loading")[0] / 2, main.screen.get_height() / 2 - main.font2.size("loading")[1] / 2))

        pg.display.update()


if __name__ == '__main__':
    main_interface()


