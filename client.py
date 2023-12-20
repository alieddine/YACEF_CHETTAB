import socket
import sys
import threading
from math import ceil

import pygame as pg
import json
import numpy as np
import copy


my_id = None
me = None
players = {}
players_changed = False
players_lock = threading.Lock()
cubes = {}
cubes_changed = False
cubes_lock = threading.Lock()
body = {}
body_changed = False
body_lock = threading.Lock()
movement_action = {'force': 0, 'angle': 0}
movement_action_lock = threading.Lock()
actions = []
actions_lock = threading.Lock()
# top bottom face back_face side
texture = {
    'grass': {
        'top': pg.image.load('src/grass_top.png'),
        'bottom': pg.image.load('src/grass_top.png'),
        'default': pg.image.load('src/grass_side.png')
    },
    'player': {
        'top': pg.image.load('src/player_back.png'),
        'bottom': pg.image.load('src/player_bottom.png'),
        'back_face': pg.image.load('src/player_front.png'),
        'face': pg.image.load('src/player_back.png'),
        'side': pg.image.load('src/player_side.png')
    },
    'body': {
        'top': pg.image.load('src/body_top.png'),
        'bottom': pg.image.load('src/body_bottom.png'),
        'back_face': pg.image.load('src/body_back.png'),
        'face': pg.image.load('src/body_front.png'),
        'side': pg.image.load('src/body_side.png')
    },
    'planks_oak': {
        'top': pg.image.load('src/planks_oak.png'),
        'bottom': pg.image.load('src/planks_oak.png'),
        'back_face': pg.image.load('src/planks_oak.png'),
        'face': pg.image.load('src/planks_oak.png'),
        'side': pg.image.load('src/planks_oak.png')
    },
    'diamond_ore': {
        'top': pg.image.load('src/diamond_ore.png'),
        'bottom': pg.image.load('src/diamond_ore.png'),
        'back_face': pg.image.load('src/diamond_ore.png'),
        'face': pg.image.load('src/diamond_ore.png'),
        'side': pg.image.load('src/diamond_ore.png')
    },
    'default': {
        'default': pg.image.load('src/brick.png')
    }
}

# player ==> position angle_x_z angle_y_z jump_force texture* points(client ytcreeaw)
# cube ==> position points(client ytcreeaw) texture
# action ==> type , kwargs**
# movement action ==> force[0,1], angle

# pandora box ==> cubes players
# players(pandora box) ==> player_id -> operation new_data*
# cubes(pandora box) ==> cube_id -> operation new_data*

width, height = 1500, 900
rotate_x_z = []
rotate_y_z = []
rotate_x_y = []
cos = []
sin = []

for a in range(360):
    a = np.deg2rad(a)
    c = np.cos(a)
    s = np.sin(a)
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
    rotate_x_y.append(np.array([
        [c, -s, 0],
        [s, c, 0],
        [0, 0, 1]
    ]))


def set_player(name, data):
    global players_changed, players, players_lock, my_id, me
    with players_lock:
        if name == my_id:
            me = data
        else:
            players_changed = True
            players[name] = data


def delete_player(name):
    global players_changed, players, players_lock
    with players_lock:
        players_changed = True
        return players.pop(name, None)


def get_players():
    global players_changed, players, players_lock
    with players_lock:
        players_changed = False
        return copy.deepcopy(list(players.values()))

def get_my_position():
    with players_lock:
        return list(me.get('position'))


def set_cube(id_, cube):
    global cubes_changed, cubes, cubes_lock
    with cubes_lock:
        cubes_changed = True
        cubes[id_] = cube

def set_body(id_, b):
    global body_changed, body, body_lock
    with body_lock:
        body_changed = True
        body[id_] = b

def get_body():
    global body_changed, body, body_lock
    with body_lock:
        body_changed = False
        return copy.deepcopy(list(body.values()))

def delete_cube(id_):
    global cubes_changed, cubes, cubes_lock
    with cubes_lock:
        cubes_changed = True
        return cubes.pop(id_, None)


def get_cubes():
    global cubes_changed, cubes, cubes_lock
    with cubes_lock:
        cubes_changed = False
        return copy.deepcopy(list(cubes.values()))


def set_movement_action(force, angle):
    with movement_action_lock:
        movement_action['force'] = force
        movement_action['angle'] = angle


def add_action(type_, **kwargs):
    with actions_lock:
        kwargs['type'] = type_
        actions.append(kwargs)


def get_movement_action():
    with movement_action_lock:
        return json.dumps(movement_action).encode('utf-8')


def get_actions():
    global actions
    with actions_lock:
        data = json.dumps(actions).encode('utf-8')
        actions = []
        return data


def send_data(client_socket):
    global movement_action
    while True:
        data_to_send = {
            "movement_action": json.loads(get_movement_action().decode('utf-8')),  # on_long_click
            "actions": json.loads(get_actions().decode('utf-8'))  # on_click
        }
        client_socket.send(json.dumps(data_to_send).encode("utf-8"))
        data = client_socket.recv(1024)
        if not data:
            break
        received_data = json.loads(data.decode("utf-8"))
        players_ = received_data.get('players', {})
        cubes_ = received_data.get('cubes', {})
        for player_id, player_data in players_.items():
            operation = player_data.get('operation', None)
            if operation is None:
                continue
            if operation == 'add':
                d = player_data.get('data', None)
                d['points'] = generate_point_of_cube(d.get('position'), size=.7)
                if d is not None:
                    set_player(player_id, d)
                    if player_id != my_id:
                        set_body(player_id, {"position": [d.get('position')[0], d.get('position')[1] + 1.5, d.get('position')[2]], "points": generate_point_of_cuboid([d.get('position')[0], d.get('position')[1] + 1.5, d.get('position')[2]]), 'texture': 'body', 'angle_x_z': d.get('angle_x_z')})

            elif operation == 'delete':
                delete_player(player_id)
        for cube_id, cube_data in cubes_.items():
            operation = cube_data.get('operation', None)
            if operation is None:
                continue
            if operation == 'add':
                d = cube_data.get('data', None)
                d['points'] = generate_point_of_cube(d.get('position'), 2)
                if d is not None:
                    set_cube(cube_id, d)
            elif operation == 'delete':
                delete_cube(cube_id)


def generate_point_of_cube(center, size=2):
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

def generate_point_of_cuboid(center, size=2):
    half_size = size / 2
    points = np.array([
        [-.75, -1, -.25, 1],
        [.75, -1, -.25, 1],
        [.75, 2, -.25, 1],
        [-.75, 2, -.25, 1],
        [-.75, -1, .25, 1],
        [.75, -1, .25, 1],
        [.75, 2, .25, 1],
        [-.75, 2, .25, 1]
    ]).T
    transform_martice = np.array([
        [half_size, 0, 0, center[0]],
        [0, half_size, 0, center[1]],
        [0, 0, half_size, center[2]]
    ])
    return np.dot(transform_martice, points).T


def transform_points(points):
    points_x = points[..., 0]
    points_y = points[..., 1]
    points_z = (points[..., 2])
    points_z[points_z < .1] = .1
    return np.column_stack((points_x/points_z, points_y/points_z, np.ones(len(points))))


def save_surfaces(transformed_coordinates):
    return sorted([
        [[0, np.linalg.norm(transformed_coordinates[0]), transformed_coordinates[0]], [1, np.linalg.norm(transformed_coordinates[1]), transformed_coordinates[1]], [2, np.linalg.norm(transformed_coordinates[2]), transformed_coordinates[2]],
         [3, np.linalg.norm(transformed_coordinates[3]), transformed_coordinates[3]]],  # face
        [[4, np.linalg.norm(transformed_coordinates[4]), transformed_coordinates[4]], [5, np.linalg.norm(transformed_coordinates[5]), transformed_coordinates[5]], [6, np.linalg.norm(transformed_coordinates[6]), transformed_coordinates[6]],
         [7, np.linalg.norm(transformed_coordinates[7]), transformed_coordinates[7]]],  # back face
        [[0, np.linalg.norm(transformed_coordinates[0]), transformed_coordinates[0]], [1, np.linalg.norm(transformed_coordinates[1]), transformed_coordinates[1]], [5, np.linalg.norm(transformed_coordinates[5]), transformed_coordinates[5]],
         [4, np.linalg.norm(transformed_coordinates[4]), transformed_coordinates[4]]],  # top
        [[2, np.linalg.norm(transformed_coordinates[2]), transformed_coordinates[2]], [3, np.linalg.norm(transformed_coordinates[3]), transformed_coordinates[3]], [7, np.linalg.norm(transformed_coordinates[7]), transformed_coordinates[7]],
         [6, np.linalg.norm(transformed_coordinates[6]), transformed_coordinates[6]]],  # buttom
        [[5, np.linalg.norm(transformed_coordinates[5]), transformed_coordinates[5]], [1, np.linalg.norm(transformed_coordinates[1]), transformed_coordinates[1]],[2, np.linalg.norm(transformed_coordinates[2]), transformed_coordinates[2]], [6, np.linalg.norm(transformed_coordinates[6]), transformed_coordinates[6]],],
        [[4, np.linalg.norm(transformed_coordinates[4]), transformed_coordinates[4]], [0, np.linalg.norm(transformed_coordinates[0]), transformed_coordinates[0]],[3, np.linalg.norm(transformed_coordinates[3]), transformed_coordinates[3]], [7, np.linalg.norm(transformed_coordinates[7]), transformed_coordinates[7]],]
    ], key=lambda x: np.mean([i[1] for i in x]), reverse=True)[-3:]


def draw_surface(surface, quad, img, resolution, intensity=1):
    points = dict()
    w = img.get_size()[0] // resolution
    h = img.get_size()[1] // resolution
    for i in range(h + 1):
        b = quad[1][0] + i / h * (quad[2][0] - quad[1][0]), quad[1][1] + i / h * (quad[2][1] - quad[1][1])
        c = quad[0][0] + i / h * (quad[3][0] - quad[0][0]), quad[0][1] + i / h * (quad[3][1] - quad[0][1])
        for u in range(w + 1):
            points[(u, i)] = c[0] + u / w * (b[0] - c[0]), c[1] + u / w * (b[1] - c[1])
    for x in range(w):
        for y in range(h):
            p_1 = points[(x + 1, y + 1)]
            p_0 = points[(x, y)]
            p_2 = points[(x, y + 1)]  # fok +1 +1
            p_3 = points[(x + 1, y)]  # t7t +0 +0
            # if 0 <= points[(x + 1, y + 1)][0] <= width and 0 <= points[(x + 1, y + 1)][1] <= height and 0 <= points[(x, y )][0] <= width and 0 <= points[(x, y)][1] <= height:
            #     pass
            # if 0<=p_1[0]<=width and 0<=p_1[1]<=height:
            #     pass
            pg.draw.polygon(
                surface,
                np.array(img.get_at((x * resolution, y * resolution)))*intensity,
                [p_0, p_2, p_1, p_3]
            )


def draw_obj(screen, obj, angle_x_z, angle_y_z, player_position, f, K, resolution):
    obj_position = obj.get('position')
    points = np.array(obj.get('points'))
    obj_angle_x_z = obj.get('angle_x_z', None)
    if obj_angle_x_z is not None:
        obj_angle_y_z = obj.get('angle_y_z', 0)
        points = np.dot(np.dot(np.dot(points - obj_position, rotate_x_z[int(-obj_angle_x_z)%360]), rotate_y_z[int(-obj_angle_y_z*cos[int(obj_angle_x_z)%360])%360]), rotate_x_y[int(-obj_angle_y_z*sin[int(obj_angle_x_z)%360])%360]) + obj_position
    points = np.dot(np.dot(points - player_position, rotate_x_z[int(angle_x_z)%360]), rotate_y_z[int(angle_y_z)%360])
    if np.mean(points, axis=0)[2] <= -1:
        return
    surfaces = save_surfaces(points)
    points_2d = np.dot(transform_points(points), K)
    f = 0
    for surface in surfaces:
        if surface[0][2][2] > f and surface[1][2][2] > f and surface[2][2][2] > f and surface[3][2][2] > f:
            p = [points_2d[point] for point, _, _ in surface]
            # for point, _, _ in surface:
            #     p.append(points_2d[point])
            tex = texture.get(obj.get('texture'), texture.get('default'))
            def_tex = tex.get('default')
            if surface[0][0] == 0 and surface[1][0] == 1 and surface[2][0] == 5 and surface[3][0] == 4:
                draw_surface(screen, p, tex.get('top', def_tex), resolution)
            elif surface[0][0] == 2 and surface[1][0] == 3 and surface[2][0] == 7 and surface[3][0] == 6:
                draw_surface(screen, p, tex.get('bottom', def_tex), resolution)
            elif surface[0][0] == 0 and surface[1][0] == 1 and surface[2][0] == 2 and surface[3][0] == 3:
                draw_surface(screen, p, tex.get('face', def_tex), resolution)
            elif surface[0][0] == 4 and surface[1][0] == 5 and surface[2][0] == 6 and surface[3][0] == 7:
                draw_surface(screen, p, tex.get('back_face', def_tex), resolution)
            else:
                draw_surface(screen, p, tex.get('side', def_tex), resolution)


def main_loop(settings):
    pg.init()
    # screen_info = pg.display.Info()
    # width, height = screen_info.current_w, screen_info.current_h
    font2 = pg.font.Font("fonts/Mojang-Regular.ttf", 20)
    screen = settings.screen
    resolution = settings.cube_resolution[1][settings.cube_resolution[0]]
    alpha = 100
    beta = 100
    f = round(settings.focal)
    if settings.full_screen:
        width = settings.screen_info[0]
        height = settings.screen_info[1]
    else:
        width = settings.width
        height = settings.height
    u0 = width // 2
    v0 = height // 2
    K = np.array([[f * alpha, 0, u0], [0, f * beta, v0]]).T
    pg.event.set_grab(True)
    all_players = get_players()
    all_body = get_body()
    all_cubes = get_cubes()
    # pg.mouse.set_visible(False)

    settings.menu_track.stop()
    settings.main_track.play(-1)
    inventory = pg.transform.scale_by(pg.image.load("intrface gui/inventory.png"),  3)
    inventory_window = pg.transform.scale_by(pg.image.load("intrface gui/inventory_window.png"), 2)
    cursor = pg.transform.scale(pg.image.load("src/cursor.png"), (10, 10))
    show_inventory_window = False
    clock = pg.time.Clock()
    selected_item = 0
    item_size = inventory.get_width() // 9, inventory.get_height()
    item_grass = pg.transform.scale(pg.image.load("src/grass_side.png"), (item_size[0] - 15, item_size[1] - 15))
    item_brick = pg.transform.scale(pg.image.load("src/brick.png"), (item_size[0] - 15, item_size[1] - 15))
    item_planks_oak = pg.transform.scale(pg.image.load("src/planks_oak.png"), (item_size[0] - 15, item_size[1] - 15))
    item_diamond_ore = pg.transform.scale(pg.image.load("src/diamond_ore.png"), (item_size[0] - 15, item_size[1] - 15))
    while True:
        clock.tick(60000)
        player_position = get_my_position()

        screen.fill((66, 135, 245))
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 3:
                    if selected_item == 0:
                        texture = "grass"
                    elif selected_item == 1:
                        texture = "brick"
                    elif selected_item == 2:
                        texture = "diamond_ore"
                    elif selected_item == 3:
                        texture = "planks_oak"
                    else:
                        texture = "None"
                    add_action('build', cube=texture)
                if event.button == 1:
                    add_action('destroy')
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    settings.main_track.stop()
                    pg.event.set_grab(False)
                    settings.show = True
                elif event.key == pg.K_e:
                    show_inventory_window = not show_inventory_window
                elif event.key == pg.K_1:
                    selected_item = 0
                elif event.key == pg.K_2:
                    selected_item = 1
                elif event.key == pg.K_3:
                    selected_item = 2
                elif event.key == pg.K_4:
                    selected_item = 3
                elif event.key == pg.K_5:
                    selected_item = 4
                elif event.key == pg.K_6:
                    selected_item = 5
                elif event.key == pg.K_7:
                    selected_item = 6
                elif event.key == pg.K_8:
                    selected_item = 7
                elif event.key == pg.K_9:
                    selected_item = 8


        if settings.show:
            settings.show_settings_interface()
            f = round(settings.focal)
            screen = settings.screen
            settings.main_track.play(-1)
            u0 = screen.get_width() // 2
            v0 = screen.get_height() // 2
            K = np.array([[f * alpha, 0, u0], [0, f * beta, v0]]).T
            pg.mouse.set_visible(False)
            resolution = settings.cube_resolution[1][settings.cube_resolution[0]]
            pg.event.set_grab(True)
        keys = pg.key.get_pressed()
        mouse = pg.mouse.get_pos()
        angle_x_z = int(360 * (u0 - mouse[0]) / width)
        angle_y_z = int(180 * (v0 - mouse[1]) / height)
        print(player_position)
        if pg.mouse.get_rel() != (0, 0):
            add_action('angle', angle_x_z=angle_x_z, angle_y_z=angle_y_z)
            if mouse[0] == screen.get_width() - 1:
                pg.mouse.set_pos((0, mouse[1]))
            elif mouse[0] == 0:
                pg.mouse.set_pos((screen.get_width(), mouse[1]))
        x = 0
        y = 0
        if keys[pg.K_a]:
            x -= 1
        if keys[pg.K_d]:
            x += 1
        if keys[pg.K_w]:
            y += 1
        if keys[pg.K_s]:
            y -= 1
        if keys[pg.K_SPACE]:
            add_action('jump')
        force = 0
        movement_angle = angle_x_z
        if x != 0 or y != 0:
            force = 1
            if x == 0:
                if y > 0:
                    movement_angle += 90
                else:
                    movement_angle -= 90
            elif y == 0:
                if x < 0:
                    movement_angle += 180
            else:
                if x > 0:
                    if y > 0:
                        movement_angle += 45
                    else:
                        movement_angle -= 45
                else:
                    if y > 0:
                        movement_angle += 135
                    else:
                        movement_angle -= 135
        movement_angle %= 360
        set_movement_action(force, movement_angle)
        if players_changed:
            all_players = get_players()
        if body_changed:
            all_body = get_body()

        if cubes_changed:
            all_cubes = get_cubes()
        objects = sorted(all_players + all_cubes + all_body, key=lambda elem: np.linalg.norm(np.dot(np.dot(np.array(elem.get('position')) - player_position, rotate_x_z[int(angle_x_z)]), rotate_y_z[int(angle_y_z)])), reverse=True)
        for obj in objects:
            draw_obj(screen, obj, angle_x_z, angle_y_z, player_position, f, K, resolution)
        if show_inventory_window:
            screen.blit(inventory_window, (screen.get_width() / 2 - inventory_window.get_width() / 2, screen.get_height() / 2 - inventory_window.get_height() / 2))

        screen.blit(inventory, (screen.get_width() / 2 - inventory.get_width() / 2, screen.get_height() - inventory.get_height() * 1.5))

        screen.blit(item_grass, (screen.get_width() / 2 - inventory.get_width() / 2 + item_size[0] * 0 + 7.5, screen.get_height() - inventory.get_height() * 1.5 + 7.5))

        screen.blit(item_brick, (screen.get_width() / 2 - inventory.get_width() / 2 + item_size[0] * 1 + 7.5, screen.get_height() - inventory.get_height() * 1.5 + 7.5))

        screen.blit(item_diamond_ore, (screen.get_width() / 2 - inventory.get_width() / 2 + item_size[0] * 2 + 7.5, screen.get_height() - inventory.get_height() * 1.5 + 7.5))

        screen.blit(item_planks_oak, (screen.get_width() / 2 - inventory.get_width() / 2 + item_size[0] * 3 + 7.5 + 7.5, screen.get_height() - inventory.get_height() * 1.5 + 7.5))

        pg.draw.rect(screen, (255, 255, 255), (screen.get_width() / 2 - inventory.get_width() / 2 + item_size[0] * selected_item, screen.get_height() - inventory.get_height() * 1.5, item_size[0], item_size[1]), 5)

        screen.blit(cursor, (screen.get_width() / 2 - cursor.get_width() / 2, screen.get_height() / 2 - cursor.get_height() / 2))
        if settings.show_fps:
            screen.blit(font2.render("FPS  :  " + str(round(clock.get_fps())), True, (255, 255, 255)), (5, 5))
        pg.display.update()


def client(setting):
    global cubes, players, my_id, me, body
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("127.0.0.1", 12345))
    # client_socket.connect(("192.168.63.5", 12345))

    v = client_socket.recv(1024).decode('utf-8')
    data = json.loads(v)
    players = data.get('players')
    for player_id, player_data in players.items():
        players[player_id]['points'] = generate_point_of_cube(players[player_id].get('position'), size=.7)
    my_id = data.get('player_id')
    me = players.pop(my_id)
    received_data = ""
    while True:
        chunk = client_socket.recv(1000).decode('utf-8')
        if chunk == 'end':
            break
        received_data += chunk
        client_socket.send('nothing'.encode('utf-8'))


    data = json.loads(received_data)
    cubes = data.get('cubes')
    for cube in cubes.values():
        cube['points'] = generate_point_of_cube(cube.get('position'))

        # set_body(player_id, {"position": [players[player_id].get('position')[0], players[player_id].get('position')[1] + 1,players[player_id].get('position')[2]], "points": generate_point_of_cuboid([players[player_id].get('position')[0], players[player_id].get('position')[1] + 1,players[player_id].get('position')[2]]), 'texture': 'grass'})

    threading.Thread(target=send_data, args=(client_socket,)).start()
    # threading.Thread(target=main_loop).start()
    main_loop(setting)

