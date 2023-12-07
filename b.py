import random
import sys

import pygame
import pickle
import numpy as np
from time import time

pygame.init()


screen_info = pygame.display.Info()
width, height = screen_info.current_w, screen_info.current_h

screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
# width, height = pygame.transform.scale_by(pygame.image.load("background2/Image" + str(1) + ".jpg"), 0.7).get_size()
# screen = pygame.display.set_mode((width, height))
surface = pygame.Surface((width, height))

# pygame.draw.circle(surface, (255, 0, 0), (width // 2, height // 2), 50)
images = []
# surface_arrays = []
# for index in range(450):
#     images.append(pygame.image.load("background3/frame_" + str(index) + ".jpg"))
#     surface_arrays.append(pygame.surfarray.array3d(images[index]))
#     print(index)
# print("finish reading")
#
# with open('surface.pickle', 'wb') as file:
#     pickle.dump(surface_arrays, file)
# print("finish saving")

with open('surface.pickle', 'rb') as file:
    surface_arrays = pickle.load(file)


surfaces = []
for index, element in enumerate(surface_arrays):
    surfaces.append(pygame.surfarray.make_surface(element))
    print(index)

print("finish reading")

past_time = time()
running = True
index = 350
b1 = pygame.image.load("b1.jpg")
b0 = pygame.image.load("b1.jpg")
pos = 0, 0
scale = 1
start_black_filter = False
alpha = 0
black_filter_going_on = True
while running:
    # screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # screen.blit(b0, pos)
    # print(scale)
    # if time() - past_time >= 0.02:
    #     if scale <= 1.5:
    #         pos = pos[0] - 1, pos[1] - 1
    #         scale = scale + 0.0009
    #         b0 = pygame.transform.scale_by(b1, scale)
    #     elif scale <= 1.8:
    #         pos = pos[0], pos[1] + 1
    #         scale = scale + 0.0009
    #         b0 = pygame.transform.scale_by(b1, scale)
    #         past_time = time()

    if time() - past_time >= 0.1:
        screen.blit(surfaces[index], (0, 0))
        index += 1
        past_time = time()
        index = index % 450
        if index == 400:
            start_black_filter = True
        if start_black_filter:
            black_filter = pygame.surface.Surface((screen.get_width(), screen.get_height()))
            black_filter.fill((0, 0, 0))
            black_filter.set_alpha(alpha)
            screen.blit(black_filter, (0, 0))
            if black_filter_going_on:
                alpha += 5
                if alpha == 255:
                    black_filter_going_on = False
            else:
                alpha -= 5
                if alpha == 0:
                    black_filter_going_on = True
                    start_black_filter = False
                    index = random.randint(70, 380)

    pygame.display.update()
pygame.quit()
