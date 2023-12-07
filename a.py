import pygame as pg
import numpy as np
import sys
import pygame.gfxdraw


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
    return np.column_stack((points_x/points_z, points_y/points_z, np.ones(len(points))))


def save_surfaces(transformed_coordinates):
    return sorted([
        [[0, np.linalg.norm(transformed_coordinates[0]), transformed_coordinates[0]], [1, np.linalg.norm(transformed_coordinates[1]), transformed_coordinates[1]], [2, np.linalg.norm(transformed_coordinates[2]), transformed_coordinates[2]],
         [3, np.linalg.norm(transformed_coordinates[3]), transformed_coordinates[3]]],
        [[4, np.linalg.norm(transformed_coordinates[4]), transformed_coordinates[4]], [5, np.linalg.norm(transformed_coordinates[5]), transformed_coordinates[5]], [6, np.linalg.norm(transformed_coordinates[6]), transformed_coordinates[6]],
         [7, np.linalg.norm(transformed_coordinates[7]), transformed_coordinates[7]]],
        [[0, np.linalg.norm(transformed_coordinates[0]), transformed_coordinates[0]], [1, np.linalg.norm(transformed_coordinates[1]), transformed_coordinates[1]], [5, np.linalg.norm(transformed_coordinates[5]), transformed_coordinates[5]],
         [4, np.linalg.norm(transformed_coordinates[4]), transformed_coordinates[4]]],  # top
        [[2, np.linalg.norm(transformed_coordinates[2]), transformed_coordinates[2]], [3, np.linalg.norm(transformed_coordinates[3]), transformed_coordinates[3]], [7, np.linalg.norm(transformed_coordinates[7]), transformed_coordinates[7]],
         [6, np.linalg.norm(transformed_coordinates[6]), transformed_coordinates[6]]],  # buttom
        [[5, np.linalg.norm(transformed_coordinates[5]), transformed_coordinates[5]], [1, np.linalg.norm(transformed_coordinates[1]), transformed_coordinates[1]],[2, np.linalg.norm(transformed_coordinates[2]), transformed_coordinates[2]], [6, np.linalg.norm(transformed_coordinates[6]), transformed_coordinates[6]],],
        [[4, np.linalg.norm(transformed_coordinates[4]), transformed_coordinates[4]], [0, np.linalg.norm(transformed_coordinates[0]), transformed_coordinates[0]],[3, np.linalg.norm(transformed_coordinates[3]), transformed_coordinates[3]], [7, np.linalg.norm(transformed_coordinates[7]), transformed_coordinates[7]],]
    ], key=lambda x: np.mean([i[1] for i in x]), reverse=True)[-3:]


def lerp(p1, p2, f):
    return p1 + f * (p2 - p1)


def lerp2d(p1, p2, f):
    return tuple(lerp(p1[i], p2[i], f) for i in range(2))


def draw_quad(surface, quad, img, intensity):
    points = dict()
    w = img.get_size()[0]
    h = img.get_size()[1]

    for i in range(h + 1):
        b = lerp2d(quad[1], quad[2], i / h)
        c = lerp2d(quad[0], quad[3], i / h)
        for u in range(w + 1):
            a = lerp2d(c, b, u / w)
            points[(u, i)] = a
    for x in range(w):
        for y in range(h):
            pygame.draw.polygon(
                surface,
                np.array(img.get_at((x, y)))*intensity,
                [points[(a, b)] for a, b in [(x, y), (x, y + 1), (x + 1, y + 1), (x + 1, y)]]
            )


def draw_cube(screen, points, angle_x_z, angle_y_z, player_position, f, K, side, top, buttom, intensity=None):
    global rotate_x_z, rotate_y_z
    transformed_points = np.dot(np.dot(points - player_position, rotate_x_z[int(angle_x_z)%360]), rotate_y_z[int(angle_y_z)%360])
    surfaces = save_surfaces(transformed_points)
    points_2d = np.dot(transform_points(transformed_points, f), K)
    f = 0
    for index, surface in enumerate(surfaces):
        if surface[0][2][2] > f and surface[1][2][2] > f and surface[2][2][2] > f and surface[3][2][2] > f:
            if intensity is None:
                # intensity = 1
                a_ = np.cross(np.array(surface[0][2]) - surface[1][2], np.array(surface[0][2]) - surface[2][2])
                a_ /= np.linalg.norm(a_)
                light_direction = sun.get('center') - np.mean([surface[0][1], surface[1][1],surface[2][1],surface[3][1]])
                light_direction /= np.linalg.norm(light_direction)
                intensity = np.sum(a_*light_direction)
                intensity = (intensity + 1)/2
            p = []
            for point, _, _ in surface:
                p.append(points_2d[point])
            if surface[0][0] == 0 and surface[1][0] == 1 and surface[2][0] == 5 and surface[3][0] == 4:
                draw_quad(screen, p, top, intensity)
            elif surface[0][0] == 2 and surface[1][0] == 3 and surface[2][0] == 7 and surface[3][0] == 6:
                draw_quad(screen, p, buttom, intensity)
            else:
                draw_quad(screen, p, side, intensity)



width, height = 1024, 700
grass_top = pg.image.load('src/grass_top.png')
grass_side = pg.image.load('src/grass_side.png')
y = np.zeros((16, 16, 3))
y[..., :] = np.array([255,255,153])
yellow = pg.surfarray.make_surface(y)
sun = {'center': np.array((100, -50, 100)), 'points': generate_point_of_cube((10, -50, 10), 2), 'top': yellow, 'side': yellow, 'buttom': yellow}
def main():
    cubes = [
        {'center': np.array((0, 2, 0)), 'points': generate_point_of_cube((0, 2, 0), 2), 'top': grass_top, 'side': grass_side, 'buttom': grass_top},
        {'center': np.array((2, 2, 0)), 'points': generate_point_of_cube((2, 2, 0), 2), 'top': grass_top, 'side': grass_side, 'buttom': grass_top},
        {'center': np.array((0, 2, 2)), 'points': generate_point_of_cube((0, 2, 2), 2), 'top': grass_top, 'side': grass_side, 'buttom': grass_top},
        {'center': np.array((2, 2, 2)), 'points': generate_point_of_cube((2, 2, 2), 2), 'top': grass_top, 'side': grass_side, 'buttom': grass_top},
        # {'center': np.array((2, 0, 2)), 'points': generate_point_of_cube((2, 0, 2), 2), 'top': grass_top, 'side': grass_side, 'buttom': grass_top},
    ]
    player_position = [0, 0, -10]
    f = 2
    alpha = 100
    beta = 100
    angle_x_z = 0
    angle_y_z = 0
    movement_speed = .1
    rotation_speed = .8
    jump_force = 0
    jump_reduce = 0.04
    gravity = 1
    pg.init()
    width, height = 1024, 700
    screen = pg.display.set_mode((width, height))
    u0 = width//2
    v0 = height//2
    K = np.array([[f * alpha, 0, u0], [0, f * beta, v0]]).T
    clock = pg.time.Clock()

    while True:
        screen.fill((0, 0, 0))
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_j:
                    center = np.array([player_position[0] + 2*sin[int(angle_x_z)], player_position[1]+1, player_position[2] + 2*cos[int(angle_x_z)]]).astype('int32')
                    cubes.append({'center': center, 'points': generate_point_of_cube(center, 2), 'top': grass_top, 'side': grass_side, 'buttom': grass_top})

        keys = pg.key.get_pressed()

        if keys[pg.K_q]:
            player_position[2] -= movement_speed * sin[int(angle_x_z)]
            player_position[0] -= movement_speed * cos[int(angle_x_z)]
        if keys[pg.K_d]:
            player_position[2] += movement_speed * sin[int(angle_x_z)]
            player_position[0] += movement_speed * cos[int(angle_x_z)]
        if keys[pg.K_z]:
            player_position[2] += movement_speed * cos[int(angle_x_z)]
            player_position[0] -= movement_speed * sin[int(angle_x_z)]
        if keys[pg.K_s]:
            player_position[2] -= movement_speed * cos[int(angle_x_z)]
            player_position[0] += movement_speed * sin[int(angle_x_z)]
        if keys[pg.K_SPACE]:
            # player_position[1] -= movement_speed
            if jump_force == 0:
                jump_force = 2
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
        player_position[1] = min(0, player_position[1]-jump_force+gravity)
        angle_x_z %= 360
        angle_y_z %= 360
        draw_cube(screen, sun.get('points'), angle_x_z, angle_y_z, player_position, f, K, sun.get('side'), sun.get('top'), sun.get('buttom'), intensity=1)
        cubes.sort(key=lambda x: np.linalg.norm(np.dot(np.dot(x.get('center') - player_position, rotate_x_z[int(angle_x_z)%360]), rotate_y_z[int(angle_y_z)%360])), reverse=True)
        for cube in cubes:
            test = np.abs(cube["center"] - player_position - [0, 2, 0])
            print(cube["center"], player_position)
            if test == [1, 1, 1]:
                print(player_position)
                player_position[1] += 1
            draw_cube(screen, cube.get('points'), angle_x_z, angle_y_z, player_position, f, K, cube.get('side'), cube.get('top'), cube.get('buttom'))

        clock.tick(60)
        pg.display.set_caption(str(round(clock.get_fps())))
        pg.display.update()


if __name__ == '__main__':
    main()