import socket
import threading
import json
import copy
import numpy as np
import time


players = {}
players_changed = False
players_lock = threading.Lock()
cubes = {
    'cube 0 4 0': {'position': [0, 4, 0], 'texture': 'grass'},
    'cube 0 4 2 ': {'position': [0, 4, 2], 'texture': 'grass'},
    'cube 0 4 4': {'position': [0, 4, 4], 'texture': 'grass'},
    'cube 2 4 0 ': {'position': [2, 4, 0], 'texture': 'grass'},
    'cube 4 4 0': {'position': [4, 4, 0], 'texture': 'grass'},
    'cube 2 4 6': {'position': [2, 4, 6], 'texture': 'grass'},
    'cube 2 4 8': {'position': [2, 4, 8], 'texture': 'grass'},
    'cube 2 4 10': {'position': [2, 4, 10], 'texture': 'grass'},
}
cubes_changed = False
cubes_lock = threading.Lock()
pandora_box = {}
pandora_lock = {}
players_actions = {}
players_actions_lock = {}


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
    global players_changed, players, players_lock
    with players_lock:
        players_changed = True
        players[name] = data


def update_player_position(name, x, y, z):
    with players_lock:
        player_position = players[name]['position']
        player_position[0] += x
        player_position[1] += y
        player_position[2] += z


def update_player_angle(name, angle_x_z, angle_y_z):
    with players_lock:
        player = players[name]
        player['angle_x_z'] = angle_x_z
        player['angle_y_z'] = angle_y_z


def update_player_jump_force(name, value):
    with players_lock:
        players[name]['jump_force'] += value


def set_player_jump_force(name, value):
    with players_lock:
        players[name]['jump_force'] = value


def get_player_jump_force(name):
    with players_lock:
        return players[name].get('jump_force', 0)


def get_player_position(name):
    with players_lock:
        return copy.deepcopy(players[name].get('position'))


def get_player_angles(name):
    with players_lock:
        player = players[name]
        return player.get('angle_x_z'), player.get('angle_y_z')


def delete_player(name):
    global players_changed, players, players_lock
    with players_lock:
        players_changed = True
        players_actions.pop(name, None)
        players_actions_lock.pop(name, None)
        pandora_box.pop(name, None)
        pandora_lock.pop(name, None)
        return players.pop(name, None)


def get_player(name):
    with players_lock:
        return copy.deepcopy(players.get(name))


def get_players_id():
    global players_changed, players, players_lock
    with players_lock:
        players_changed = False
        return list(players.keys())


def set_cube(id_, cube):
    global cubes_changed, cubes, cubes_lock
    with cubes_lock:
        cubes_changed = True
        cubes[id_] = cube


def delete_cube(id_):
    global cubes_changed, cubes, cubes_lock
    with cubes_lock:
        cubes_changed = True
        return cubes.pop(id_, None)


def get_cubes():
    global cubes_changed, cubes, cubes_lock
    with cubes_lock:
        cubes_changed = False
        return list(cubes.values())


def get_cube(cube_id):
    with cubes_lock:
        return copy.deepcopy(cubes.get(cube_id))


def set_actions(player_id, actions):
    with players_actions_lock.get(player_id):
        action = players_actions.get(player_id)
        action['movement_action'] = actions.get('movement_action', action['movement_action'])
        action['actions'].extend(actions.get('actions', []))


def get_actions(player_id):
    with players_actions_lock.get(player_id):
        action = players_actions.get(player_id)
        actions = action.get('actions', [])
        action['actions'] = []
        return action.get('movement_action'), actions


def add_new_item_to_all_pandora_boxes(type_, operation, data):
    players_id = get_players_id()
    for player_id in players_id:
        add_new_item_to_pandora_box(player_id, type_, operation, data)


def add_new_item_to_pandora_box(player_id, type_, operation, data):
    with pandora_lock.get(player_id):
        if type_ == 'cube':
            # pandora_box[player_id]['cubes'].append({'operation': operation, 'data': data})
            pandora_box[player_id]['cubes'][data.get('cube_id')] = {'operation': operation}
        elif type_ == 'player':
            pandora_box[player_id]['players'][data.get('player_id')] = {'operation': operation}


def read_all_items_from_pandora_box(player_id):
    with pandora_lock.get(player_id):
        new_cubes = pandora_box[player_id]['cubes']
        new_players = pandora_box[player_id]['players']
        pandora_box[player_id]['cubes'] = {}
        pandora_box[player_id]['players'] = {}
        for player in new_players:
            if new_players[player].get('operation') == 'add':
                new_players[player]['data'] = get_player(player)
        for cube in new_cubes:
            if new_cubes[cube].get('operation') == 'add':
                new_cubes[cube]['data'] = get_cube(cube)
        return json.dumps({'cubes': new_cubes, 'players': new_players}).encode('utf-8')


def cube_intersection1(all_cubes, player_position, angle_x_z, angle_y_z, min_distance=12):
    player_position = np.array(player_position)
    # arrow = np.dot(np.dot(np.array([0, 0, 1]), rotate_x_z[int(angle_x_z) % 360]), rotate_y_z[int(-angle_y_z) % 360])
    arrow = np.dot(np.dot(np.dot(np.array([0, 0, 1]), rotate_x_z[int(-angle_x_z) % 360]),
                  rotate_y_z[int(-angle_y_z * cos[int(angle_x_z) % 360]) % 360]),
           rotate_x_y[int(-angle_y_z * sin[int(angle_x_z) % 360]) % 360])
    all_cubes = map(lambda x: np.array(x.get('position'))-player_position, all_cubes)
    all_cubes = list(map(lambda x: {'position': x, 'distance': np.linalg.norm(x), 'inter_x': (arrow * ((x[0]-1)/arrow[0] if arrow[0]!=0 else .1), arrow * ((x[0]+1)/arrow[0] if arrow[0]!=0 else 0.1)), 'inter_y': (arrow * ((x[1]-1)/arrow[1] if arrow[1]!=0 else 0.1), arrow * ((x[1]+1)/arrow[1] if arrow[1]!=0 else 0.1)), 'inter_z': (arrow * ((x[2]-1)/arrow[2] if arrow[2]!=0 else 0.1), arrow * ((x[2]+1)/arrow[2] if arrow[2]!=0 else 0.1))}, all_cubes))

    def f(x):
        if x.get('distance') > min_distance:
            return False
        position = x.get('position')
        inter_z1, inter_z2 = x.get('inter_z')
        inter_x1, inter_x2 = x.get('inter_x')
        inter_y1, inter_y2 = x.get('inter_y')
        if np.all(np.abs(inter_x1 - position) <= 1) or np.all(np.abs(inter_x2 - position) <= 1) or np.all(np.abs(inter_y1 - position) <= 1) or np.all(np.abs(inter_y2 - position) <= 1) or np.all(np.abs(inter_z1 - position) <= 1) or np.all(np.abs(inter_z2 - position) <= 1):
            return True
        return False

    selected_cube = sorted(list(filter(f, all_cubes)), key=lambda x: x.get('distance'))
    if len(selected_cube) == 0:
        return
    selected_cube = selected_cube[0]
    p = selected_cube.get('position')
    i_z1, i_z2 = selected_cube.get('inter_z')
    i_x1, i_x2 = selected_cube.get('inter_x')
    i_y1, i_y2 = selected_cube.get('inter_y')
    inter = sorted(list(filter(lambda x: np.all(np.abs(x[0]-p) <= 1), [(i_z1, [0, 0, -2]), (i_z2, [0, 0, 2]), (i_x1, [-2, 0, 0]), (i_x2, [2, 0, 0]), (i_y1, [0, -2, 0]), (i_y2, [0, 2, 0])])), key=lambda x: np.linalg.norm(x[0]))
    inter = inter[0]
    r = np.array(p) + inter[1] + player_position
    return [int(i) for i in r]


def cube_intersection(all_cubes, player_position, angle_x_z, angle_y_z, min_distance=12):
    player_position = np.array(player_position)
    # arrow = np.dot(np.dot(np.array([0, 0, 1]), rotate_x_z[int(angle_x_z) % 360]), rotate_y_z[int(-angle_y_z) % 360])
    arrow = np.dot(np.dot(np.dot(np.array([0, 0, 1]), rotate_x_z[int(-angle_x_z) % 360]),
                  rotate_y_z[int(-angle_y_z * cos[int(angle_x_z) % 360]) % 360]),
           rotate_x_y[int(-angle_y_z * sin[int(angle_x_z) % 360]) % 360])
    all_cubes = map(lambda x: (np.array(x.get('position'))-player_position, x.get('position')), all_cubes)
    all_cubes = list(map(lambda x: {'position': x[0], 'old position': x[1], 'distance': np.linalg.norm(x[0]), 'inter_x': (arrow * ((x[0][0]-1)/arrow[0] if arrow[0]!=0 else 0.1), arrow * ((x[0][0]+1)/arrow[0] if arrow[0]!=0 else 0.1)), 'inter_y': (arrow * ((x[0][1]-1)/arrow[1] if arrow[1]!=0 else 0.1), arrow * ((x[0][1]+1)/arrow[1] if arrow[1]!=0 else 0.1)), 'inter_z': (arrow * ((x[0][2]-1)/arrow[2] if arrow[2]!=0 else 0.1), arrow * ((x[0][2]+1)/arrow[2] if arrow[2]!=0 else 0.1))}, all_cubes))

    def f(x):
        if x.get('distance') > min_distance:
            return False
        position = x.get('position')
        inter_z1, inter_z2 = x.get('inter_z')
        inter_x1, inter_x2 = x.get('inter_x')
        inter_y1, inter_y2 = x.get('inter_y')
        if np.all(np.abs(inter_x1 - position) <= 1) or np.all(np.abs(inter_x2 - position) <= 1) or np.all(np.abs(inter_y1 - position) <= 1) or np.all(np.abs(inter_y2 - position) <= 1) or np.all(np.abs(inter_z1 - position) <= 1) or np.all(np.abs(inter_z2 - position) <= 1):
            return True
        return False

    selected_cube = sorted(list(filter(f, all_cubes)), key=lambda x: x.get('distance'))
    if len(selected_cube) == 0:
        return
    selected_cube = selected_cube[0]
    p = selected_cube.get('position')
    i_z1, i_z2 = selected_cube.get('inter_z')
    i_x1, i_x2 = selected_cube.get('inter_x')
    i_y1, i_y2 = selected_cube.get('inter_y')
    inter = sorted(list(filter(lambda x: np.all(np.abs(x[0]-p) <= 1), [(i_z1, [0, 0, -2]), (i_z2, [0, 0, 2]), (i_x1, [-2, 0, 0]), (i_x2, [2, 0, 0]), (i_y1, [0, -2, 0]), (i_y2, [0, 2, 0])])), key=lambda x: np.linalg.norm(x[0]))
    inter = inter[0]
    r = np.array(selected_cube.get('old position')) + inter[1]
    return [int(i) for i in r]

def destroyed_cube(all_cubes, player_position, angle_x_z, angle_y_z, min_distance=12):
    player_position = np.array(player_position)
    # arrow = np.dot(np.dot(np.array([0, 0, 1]), rotate_x_z[int(angle_x_z) % 360]), rotate_y_z[int(-angle_y_z) % 360])
    arrow = np.dot(np.dot(np.dot(np.array([0, 0, 1]), rotate_x_z[int(-angle_x_z) % 360]),
                          rotate_y_z[int(-angle_y_z * cos[int(angle_x_z) % 360]) % 360]),
                   rotate_x_y[int(-angle_y_z * sin[int(angle_x_z) % 360]) % 360])
    all_cubes = map(lambda x: np.array(x.get('position')) - player_position, all_cubes)
    all_cubes = list(map(lambda x: {'position': x, 'distance': np.linalg.norm(x), 'inter_x': (
    arrow * ((x[0] - 1) / arrow[0] if arrow[0] != 0 else .1),
    arrow * ((x[0] + 1) / arrow[0] if arrow[0] != 0 else .1)), 'inter_y': (
    arrow * ((x[1] - 1) / arrow[1] if arrow[1] != 0 else .1),
    arrow * ((x[1] + 1) / arrow[1] if arrow[1] != 0 else .1)), 'inter_z': (
    arrow * ((x[2] - 1) / arrow[2] if arrow[2] != 0 else .1),
    arrow * ((x[2] + 1) / arrow[2] if arrow[2] != 0 else .1))}, all_cubes))

    def f(x):
        if x.get('distance') > min_distance:
            return False
        position = x.get('position')
        inter_z1, inter_z2 = x.get('inter_z')
        inter_x1, inter_x2 = x.get('inter_x')
        inter_y1, inter_y2 = x.get('inter_y')
        if np.all(np.abs(inter_x1 - position) <= 1) or np.all(np.abs(inter_x2 - position) <= 1) or np.all(
                np.abs(inter_y1 - position) <= 1) or np.all(np.abs(inter_y2 - position) <= 1) or np.all(
                np.abs(inter_z1 - position) <= 1) or np.all(np.abs(inter_z2 - position) <= 1):
            return True
        return False

    selected_cube = sorted(list(filter(f, all_cubes)), key=lambda x: x.get('distance'))
    if len(selected_cube) == 0:
        return
    selected_cube = selected_cube[0]
    p = selected_cube.get('position')
    r = np.array(p) + player_position
    return [int(i) for i in r]

def handle_client(client_socket, player_id):
    try:
        set_player(player_id, {'position': [0, - 1, 0], 'angle_x_z': 0, 'angle_y_z': 0, 'jump_force': 0, 'texture': 'player'})
        players_actions[player_id] = {'movement_action': {'force': 0, 'angle': 0}, 'actions': []}
        players_actions_lock[player_id] = threading.Lock()
        pandora_box[player_id] = {'cubes': {}, 'players': {}}
        pandora_lock[player_id] = threading.Lock()
        with players_lock:
            data = json.dumps({
                'player_id': player_id,
                'players': players,
                'cubes': cubes
            }).encode("utf-8")
        client_socket.send(data)
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            d = json.loads(data.decode("utf-8"))
            set_actions(player_id, d)
            d = read_all_items_from_pandora_box(player_id)
            client_socket.send(d)
    except:
        delete_player(player_id)
        client_socket.close()


def main_loop():
    movement_speed = .09
    jump_force_init = 1.6
    gravity = 1
    jump_reduce = -.04
    p = get_players_id()
    cubes_value = get_cubes()
    desired_fps = 60
    frame_interval = 1 / desired_fps
    while True:
        start_time = time.time()
        if players_changed:
            p = get_players_id()
        for player_id in p:
            if cubes_changed:
                cubes_value = get_cubes()
            movement_action, actions = get_actions(player_id)
            player_stat_changed = False
            is_jump = False
            jump_force = get_player_jump_force(player_id)
            player_position = get_player_position(player_id)
            angle_x_z, angle_y_z = get_player_angles(player_id)
            for action in actions:
                type_ = action.get('type')
                if type_ == 'angle':
                    player_stat_changed = True
                    update_player_angle(player_id, action.get('angle_x_z', 0), action.get('angle_y_z', 0))
                elif type_ == 'jump':
                    is_jump = True
                elif type_ == 'build':
                    new_position = cube_intersection(cubes_value, player_position, angle_x_z, angle_y_z)
                    if new_position is not None:
                        build = True
                        for player_ in p:
                            pos = get_player_position(player_)
                            if np.all(np.abs(np.array(pos) - new_position) <= 2):
                                build = False
                                break
                        if build:
                            cube_id = 'cube ' + str(new_position[0]) + ' ' + str(new_position[1]) + ' ' + str(new_position[2])
                            new_cube = {'position': new_position, 'texture': action.get('cube')}
                            set_cube(cube_id, new_cube)
                            add_new_item_to_all_pandora_boxes('cube', 'add', {'cube_id': cube_id})
                            cubes_value = get_cubes()

                elif type_ == 'destroy':
                    d_position = destroyed_cube(cubes_value, player_position, angle_x_z, angle_y_z)
                    if d_position is not None:
                        cube_id = 'cube ' + str(d_position[0]) + ' ' + str(d_position[1]) + ' ' + str(
                            d_position[2])
                        delete_cube(cube_id)
                        add_new_item_to_all_pandora_boxes('cube', 'delete', {'cube_id': cube_id})


            movement_angle = int(movement_action.get('angle', 0))
            x = movement_speed * movement_action.get('force', 0) * cos[movement_angle]
            z = movement_speed * movement_action.get('force', 0) * sin[movement_angle]
            y = gravity - jump_force
            # y = 0
            update_player_jump_force(player_id, jump_reduce)
            # collide --> x, z, top, down
            # x : x=0 alt--> x= masafa binathom - (nisf el kotr ta3 cube + nisf el kotr dyali)
            # z : z=0 alt--> y= masafa binathom - (nisf el kotr ta3 cube + nisf el kotr dyali)
            # top : jump_force = 0
            # down : y=0
            for cube in cubes_value:
                cube_position = cube.get('position')
                if 2 >= player_position[1] + y - cube_position[1] >= -4:
                    if abs(player_position[0] + x - cube_position[0]) < 2 and abs(player_position[2] - cube_position[2]) < 2 and 2 > player_position[1] - cube_position[1] > -4:
                        x = 0
                    if abs(player_position[2] + z - cube_position[2]) < 2 and abs(player_position[0] - cube_position[0]) < 2 and 2 > player_position[1] - cube_position[1] > -4:
                        z = 0
                    if abs(player_position[0] + x - cube_position[0]) < 2 and abs(player_position[2] + z - cube_position[2]) < 2 and 2 > player_position[1] - cube_position[1] > -4:
                        x = 0
                        z = 0
                    if abs(player_position[0] - cube_position[0]) < 2 and abs(player_position[2] - cube_position[2]) < 2:
                        if y > 0:
                            y = 0
                            if is_jump:
                                set_player_jump_force(player_id, jump_force_init)
                            else:
                                set_player_jump_force(player_id, 0)
                        else:
                            set_player_jump_force(player_id, 0)
            if x != 0 or y != 0 or z != 0:
                player_stat_changed = True
                update_player_position(player_id, x, y, z)
            if player_stat_changed:
                add_new_item_to_all_pandora_boxes('player', 'add', {'player_id': player_id})
            if player_position[1] >= 100:
                update_player_position(player_id, - player_position[0] + 6, - player_position[1] - 100, - player_position[2])
        elapsed_time = time.time() - start_time
        if elapsed_time < frame_interval:
            time.sleep(frame_interval - elapsed_time)


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 12345))
    server_socket.listen(5)

    main_loop_thread = threading.Thread(target=main_loop)
    main_loop_thread.start()
    i = 0
    print("Server listening on port 12345")

    while True:
        client_socket, addr = server_socket.accept()
        player_id = 'player '+str(i)
        client_handler = threading.Thread(target=handle_client, args=(client_socket, player_id))
        client_handler.start()
        i += 1


if __name__ == '__main__':
    main()
