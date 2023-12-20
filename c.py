map3 = {

}


# Function to generate the key for the cubes
def generate_cube_key(x, y, z):
    return f'cube {x} {y} {z}'


# Add more elements to the map
x, y, z = 0, 4, 0  # Initial coordinates
for x in range(20):
    for z in range(20):
        map3[generate_cube_key(x * 2, y, z * 2)] = {'position': [x * 2, y, z * 2], 'texture': 'None'}

print(map3)