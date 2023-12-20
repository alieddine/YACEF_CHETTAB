import ctypes
import pickle
import sys
from random import randint
from time import time
from cl import *
import pygame as pg


class Settings:
    def __init__(self, screen_info):
        self.full_screen = False
        self.music_volume = 50 
        self.sfx_volume = 50
        self.focal = 4
        self.sfx = True
        self.cube_resolution = (0, (1, 2, 4, 16))
        self.show_fps = False
        self.width, self.height = 1500, 900
        self.screen_info = screen_info.current_w, screen_info.current_h
        self.show = False
        self.screen = None
        self.menu_track = None
        self.main_track = pg.mixer.Sound('music/calm.mp3')
        self.click_sound = pg.mixer.Sound('music/click.mp3')
        self.moving_music_slider = False
        self.slider_music_mouse = None
        self.moving_sfx_slider = False
        self.slider_sfx_mouse = None
        self.moving_focal_slider = False
        self.slider_focal_mouse = None

    def show_settings_interface(self):
        background = pg.image.load("src/setting_background.png")
        font = pg.font.Font("fonts/Mojang-Regular.ttf", 20)
        button_small = pg.transform.scale(pg.image.load("intrface gui/button.png"), (400, 40))
        button_volume = pg.transform.scale(pg.image.load("intrface gui/edit_bg.png"), (400, 40))
        button_slider = pg.transform.scale(pg.image.load("intrface gui/slider.png"), (20, 40))
        pg.mouse.set_visible(True)
        pg.mixer.music.pause()
        while True:
            mouse_hand = False
            mouse = pg.mouse.get_pos()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    sys.exit()
                elif event.type == pg.MOUSEBUTTONDOWN:
                    mouse_pressed = pg.mouse.get_pressed()
                    if mouse_pressed[0]:
                        click = True
                        if self.screen.get_width() / 2 - button_small.get_width() - 10 <= mouse[0] <= self.screen.get_width() / 2 - button_small.get_width() - 10 + button_small.get_width() and self.screen.get_height() / 4 <= mouse[1] <= self.screen.get_height() / 4 + button_small.get_height():
                            self.full_screen = not self.full_screen
                            if self.full_screen:
                                self.screen = pg.display.set_mode(self.screen_info, pg.NOFRAME)
                                ctypes.windll.user32.SetWindowPos(pg.display.get_wm_info()["window"], 0, 0, 0, 0, 0, 0x0001)
                            else:
                                ctypes.windll.user32.SetWindowPos(pg.display.get_wm_info()["window"], 0, (self.screen_info[0] // 2 - self.width // 2), (self.screen_info[1] // 2 - self.height // 2), 0, 0, 0x0001)
                                self.screen = pg.display.set_mode((self.width, self.height))
                        elif self.screen.get_width() / 2 - button_small.get_width() - 10 + (self.music_volume * (button_volume.get_width() - button_slider.get_width()) / 100) <= mouse[0] <= self.screen.get_width() / 2 - button_small.get_width() - 10 + (self.music_volume * (button_volume.get_width() - button_slider.get_width()) / 100) + button_slider.get_width() and self.screen.get_height() / 4 + button_small.get_height() * 1.5 <= mouse[1] <= self.screen.get_height() / 4 + button_small.get_height() * 1.5 + button_slider.get_height():
                            mouse_buttons = pg.mouse.get_pressed()
                            if mouse_buttons[0]:
                                self.moving_music_slider = True
                                self.slider_music_mouse = mouse
                        elif self.screen.get_width() / 2 - button_small.get_width() - 10 + (self.sfx_volume * (button_volume.get_width() - button_slider.get_width()) / 100) <= mouse[0] <= self.screen.get_width() / 2 - button_small.get_width() - 10 + (self.sfx_volume * (button_volume.get_width() - button_slider.get_width()) / 100) + button_slider.get_width() and self.screen.get_height() / 4 + button_small.get_height() * 3 <= mouse[1] <= self.screen.get_height() / 4 + button_small.get_height() * 3 + button_slider.get_height():
                            mouse_buttons = pg.mouse.get_pressed()
                            if mouse_buttons[0]:
                                self.moving_sfx_slider = True
                                self.slider_sfx_mouse = mouse
                        elif self.screen.get_width() / 2 + 10 <= mouse[0] <= self.screen.get_width() / 2 + 10 + button_small.get_width() and self.screen.get_height() / 4 <= mouse[1] <= self.screen.get_height() / 4 + button_small.get_height():
                            self.show_fps = not self.show_fps
                        elif self.screen.get_width() / 2 + 10 <= mouse[0] <= self.screen.get_width() / 2 + 10 + button_small.get_width() and self.screen.get_height() / 4 + button_small.get_height() * 1.5 <= mouse[1] <= self.screen.get_height() / 4 + button_small.get_height() * 1.5 + button_small.get_height():
                            self.cube_resolution = (self.cube_resolution[0] + 1) % 4, self.cube_resolution[1]
                        elif self.moving_music_slider or self.screen.get_width() / 2 + 10 + (self.focal * (button_volume.get_width() - button_slider.get_width()) / 20) <= mouse[0] <= self.screen.get_width() / 2 + 10 + (self.focal * (button_volume.get_width() - button_slider.get_width()) / 20) + button_slider.get_width() and self.screen.get_height() / 4 + button_small.get_height() * 3 <= mouse[1] <= self.screen.get_height() / 4 + button_small.get_height() * 3 + button_slider.get_height():
                            mouse_buttons = pg.mouse.get_pressed()
                            if mouse_buttons[0]:
                                self.moving_focal_slider = True
                                self.slider_focal_mouse = mouse
                        elif self.screen.get_width() / 2 - button_small.get_width() / 2 <= mouse[0] <= self.screen.get_width() / 2 + button_small.get_width() / 2 and self.screen.get_height() - button_small.get_height() * 2 <= mouse[1] <= self.screen.get_height() - button_small.get_height():
                            sys.exit()
                        else:
                            click = False
                        if click:
                            self.click_sound.set_volume(self.sfx_volume / 100)
                            self.click_sound.play()


                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.show = False
            if not self.show:
                pg.mixer.music.unpause()
                break
            self.screen.blit(background, (0, 0))
            self.screen.blit(font.render("Options", True, (255, 255, 255)), (self.screen.get_width() / 2 - font.size("Options")[0] / 2, 50))

            self.screen.blit(button_small, (self.screen.get_width() / 2 - button_small.get_width() - 10, self.screen.get_height() / 4))
            if self.screen.get_width() / 2 - button_small.get_width() - 10 <= mouse[0] <= self.screen.get_width() / 2 - button_small.get_width() - 10 + button_small.get_width() and self.screen.get_height() / 4 <= mouse[1] <= self.screen.get_height() / 4 + button_small.get_height():
                pg.draw.rect(self.screen, (255, 255, 255), (self.screen.get_width() / 2 - button_small.get_width() - 10, self.screen.get_height() / 4 , button_small.get_width(), button_small.get_height()), 2)
                mouse_hand = True

            self.screen.blit(button_volume, (self.screen.get_width() / 2 - button_small.get_width() - 10, self.screen.get_height() / 4 + button_small.get_height() * 1.5))
            self.screen.blit(button_slider, (self.screen.get_width() / 2 - button_small.get_width() - 10 + (self.music_volume * (button_volume.get_width() - button_slider.get_width()) / 100), self.screen.get_height() / 4 + button_small.get_height() * 1.5))
            if self.moving_music_slider or self.screen.get_width() / 2 - button_small.get_width() - 10 + (self.music_volume * (button_volume.get_width() - button_slider.get_width()) / 100) <= mouse[0] <= self.screen.get_width() / 2 - button_small.get_width() - 10 + (self.music_volume * (button_volume.get_width() - button_slider.get_width()) / 100) + button_slider.get_width() and self.screen.get_height() / 4 + button_small.get_height() * 1.5 <= mouse[1] <= self.screen.get_height() / 4 + button_small.get_height() * 1.5 + button_slider.get_height():
                pg.draw.rect(self.screen, (255, 255, 255), (self.screen.get_width() / 2 - button_small.get_width() - 10 + (self.music_volume * (button_volume.get_width() - button_slider.get_width()) / 100), self.screen.get_height() / 4 + button_small.get_height() * 1.5, button_slider.get_width(), button_slider.get_height()), 2)
                mouse_hand = True
            self.screen.blit(font.render("Music volume : " + str(round(self.music_volume)) + "%", True, (255, 255, 255)), (self.screen.get_width() / 2 - button_small.get_width() / 2 - 10 - font.size("Music volume : " + str(round(self.music_volume)) + "%")[0] / 2, self.screen.get_height() / 4 + button_small.get_height() / 2 + button_small.get_height() * 1.5 - font.size("A")[1] / 2))

            self.screen.blit(button_volume, (self.screen.get_width() / 2 - button_small.get_width() - 10, self.screen.get_height() / 4 + button_small.get_height() * 3))
            self.screen.blit(button_slider, (self.screen.get_width() / 2 - button_small.get_width() - 10 + (self.sfx_volume * (button_volume.get_width() - button_slider.get_width()) / 100), self.screen.get_height() / 4 + button_small.get_height() * 3))
            if self.moving_sfx_slider or self.screen.get_width() / 2 - button_small.get_width() - 10 + (self.sfx_volume * (button_volume.get_width() - button_slider.get_width()) / 100) <= mouse[0] <= self.screen.get_width() / 2 - button_small.get_width() - 10 + (self.sfx_volume * (button_volume.get_width() - button_slider.get_width()) / 100) + button_slider.get_width() and self.screen.get_height() / 4 + button_small.get_height() * 3 <= mouse[1] <= self.screen.get_height() / 4 + button_small.get_height() * 3 + button_slider.get_height():
                pg.draw.rect(self.screen, (255, 255, 255), (self.screen.get_width() / 2 - button_small.get_width() - 10 + (self.sfx_volume * (button_volume.get_width() - button_slider.get_width()) / 100), self.screen.get_height() / 4 + button_small.get_height() * 3, button_slider.get_width(), button_slider.get_height()), 2)
                mouse_hand = True
            self.screen.blit(font.render("SFX volume : " + str(round(self.sfx_volume)) + "%", True, (255, 255, 255)), (self.screen.get_width() / 2 - button_small.get_width() / 2 - 10 - font.size("SFX volume : " + str(round(self.sfx_volume)) + "%")[0] / 2, self.screen.get_height() / 4 + button_small.get_height() / 2 + button_small.get_height() * 3 - font.size("A")[1] / 2))

            mouse_buttons = pg.mouse.get_pressed()
            if self.moving_music_slider:
                if mouse_buttons[0]:
                    if self.screen.get_width() / 2 - button_small.get_width() - 10 <= mouse[0] <= self.screen.get_width() / 2 - button_small.get_width() - 10 + button_volume.get_width():
                        self.music_volume += (mouse[0] - self.slider_music_mouse[0]) * 100 / (button_volume.get_width() - button_slider.get_width())

                        self.music_volume = max(0, self.music_volume)
                        self.music_volume = min(100, self.music_volume)
                        self.slider_music_mouse = mouse

            elif self.moving_sfx_slider:
                if mouse_buttons[0]:
                    if self.screen.get_width() / 2 - button_small.get_width() - 10 <= mouse[0] <= self.screen.get_width() / 2 - button_small.get_width() - 10 + button_volume.get_width():
                        self.sfx_volume += (mouse[0] - self.slider_sfx_mouse[0]) * 100 / (button_volume.get_width() - button_slider.get_width())

                        self.sfx_volume = max(0, self.sfx_volume)
                        self.sfx_volume = min(100, self.sfx_volume)
                        self.slider_sfx_mouse = mouse
            elif self.moving_focal_slider:
                if mouse_buttons[0]:
                    if self.screen.get_width() / 2 + 10 <= mouse[0] <= self.screen.get_width() / 2 + 10 + button_volume.get_width():
                        self.focal += (mouse[0] - self.slider_focal_mouse[0]) * 20 / (button_volume.get_width() - button_slider.get_width())

                        self.focal = max(0, self.focal)
                        self.focal = min(20, self.focal)
                        self.slider_focal_mouse = mouse

            if not mouse_buttons[0]:
                self.moving_music_slider = False
                self.moving_sfx_slider = False
                self.moving_focal_slider = False

            self.main_track.set_volume(self.music_volume / 100)
            self.menu_track.set_volume(self.music_volume / 100)

            self.screen.blit(button_volume, (self.screen.get_width() / 2 + 10, self.screen.get_height() / 4 + button_small.get_height() * 3))
            self.screen.blit(button_slider, (self.screen.get_width() / 2 + 10 + (round(self.focal) * (button_volume.get_width() - button_slider.get_width()) / 20), self.screen.get_height() / 4 + button_small.get_height() * 3))
            if self.moving_music_slider or self.screen.get_width() / 2 + 10 + (self.focal * (button_volume.get_width() - button_slider.get_width()) / 20) <= mouse[0] <= self.screen.get_width() / 2 + 10 + (self.focal * (button_volume.get_width() - button_slider.get_width()) / 20) + button_slider.get_width() and self.screen.get_height() / 4 + button_small.get_height() * 3 <= mouse[1] <= self.screen.get_height() / 4 + button_small.get_height() * 3 + button_slider.get_height():
                pg.draw.rect(self.screen, (255, 255, 255), (self.screen.get_width() / 2 + 10 + (round(self.focal) * (button_volume.get_width() - button_slider.get_width()) / 20), self.screen.get_height() / 4 + button_small.get_height() * 3, button_slider.get_width(), button_slider.get_height()), 2)
                mouse_hand = True
            self.screen.blit(font.render("Focal : " + str(round(self.focal)), True, (255, 255, 255)), (self.screen.get_width() / 2 + button_small.get_width() / 2 + 10 - font.size("focal " + str(round(self.focal)))[0] / 2, self.screen.get_height() / 4 + button_small.get_height() / 2 + button_small.get_height() * 3 - font.size("A")[1] / 2))

            if self.full_screen:
                self.screen.blit(font.render("FullScreen : ON", True, (255, 255, 255)), (self.screen.get_width() / 2 - button_small.get_width() / 2 - 10 - font.size("FullScreen : ON")[0] / 2, self.screen.get_height() / 4 + button_small.get_height() / 2 - font.size("FullScreen : ON")[1] / 2))
            else:
                self.screen.blit(font.render("FullScreen : OFF", True, (255, 255, 255)), (self.screen.get_width() / 2 - button_small.get_width() / 2 - 10 - font.size("FullScreen : OFF")[0] / 2, self.screen.get_height() / 4 + button_small.get_height() / 2 - font.size("FullScreen : OFF")[1] / 2))

            self.screen.blit(button_small, (self.screen.get_width() / 2 + 10, self.screen.get_height() / 4))
            if self.screen.get_width() / 2 + 10 <= mouse[0] <= self.screen.get_width() / 2 + 10 + button_small.get_width() and self.screen.get_height() / 4 <= mouse[1] <= self.screen.get_height() / 4 + button_small.get_height():
                pg.draw.rect(self.screen, (255, 255, 255), (self.screen.get_width() / 2 + 10, self.screen.get_height() / 4, button_small.get_width(), button_small.get_height()), 2)
                mouse_hand = True

            if self.show_fps:
                self.screen.blit(font.render("Show  Fps  :  ON", True, (255, 255, 255)), (self.screen.get_width() / 2 + button_small.get_width() / 2 + 10 - font.size("Show  Fps  :  ON")[0] / 2, self.screen.get_height() / 4 + button_small.get_height() / 2 - font.size("FullScreen : ON")[1] / 2))
            else:
                self.screen.blit(font.render("Show  Fps  :  OFF", True, (255, 255, 255)), (self.screen.get_width() / 2 + button_small.get_width() / 2 + 10 - font.size("Show  Fps  :  OFF")[0] / 2, self.screen.get_height() / 4 + button_small.get_height() / 2 - font.size("FullScreen : OFF")[1] / 2))

            self.screen.blit(button_small, (self.screen.get_width() / 2 + 10, self.screen.get_height() / 4 + button_small.get_height() * 1.5))
            if self.screen.get_width() / 2 + 10 <= mouse[0] <= self.screen.get_width() / 2 + 10 + button_small.get_width() and self.screen.get_height() / 4 + button_small.get_height() * 1.5 <= mouse[1] <= self.screen.get_height() / 4 + button_small.get_height() * 1.5 + button_small.get_height():
                pg.draw.rect(self.screen, (255, 255, 255), (self.screen.get_width() / 2 + 10, self.screen.get_height() / 4 + button_small.get_height() * 1.5, button_small.get_width(), button_small.get_height()), 2)
                mouse_hand = True

            if self.cube_resolution[0] == 0:
                self.screen.blit(font.render("cube  resolution  :  16X16", True, (255, 255, 255)), (self.screen.get_width() / 2 + button_small.get_width() / 2 + 10 - font.size("cube  resolution  :  16X16")[0] / 2, self.screen.get_height() / 4 + button_small.get_height() * 1.5 + button_small.get_height() / 2 - font.size("FullScreen : ON")[1] / 2))
            elif self.cube_resolution[0] == 1:
                self.screen.blit(font.render("cube  resolution  :  8X8", True, (255, 255, 255)), (self.screen.get_width() / 2 + button_small.get_width() / 2 + 10 - font.size("cube  resolution  :  16X16")[0] / 2, self.screen.get_height() / 4 + button_small.get_height() * 1.5 + button_small.get_height() / 2 - font.size("FullScreen : OFF")[1] / 2))
            elif self.cube_resolution[0] == 2:
                self.screen.blit(font.render("cube  resolution  :  4X4", True, (255, 255, 255)), (self.screen.get_width() / 2 + button_small.get_width() / 2 + 10 - font.size("cube  resolution  :  16X16")[0] / 2, self.screen.get_height() / 4 + button_small.get_height() * 1.5 + button_small.get_height() / 2 - font.size("FullScreen : OFF")[1] / 2))
            elif self.cube_resolution[0] == 3:
                self.screen.blit(font.render("cube  resolution  :  1X1", True, (255, 255, 255)), (self.screen.get_width() / 2 + button_small.get_width() / 2 + 10 - font.size("cube  resolution  :  16X16")[0] / 2, self.screen.get_height() / 4 + button_small.get_height() * 1.5 + button_small.get_height() / 2 - font.size("FullScreen : OFF")[1] / 2))


            self.screen.blit(button_small, (self.screen.get_width() / 2 - button_small.get_width() / 2, self.screen.get_height() - button_small.get_height() * 2))
            if self.screen.get_width() / 2 - button_small.get_width() / 2 <= mouse[0] <= self.screen.get_width() / 2 + button_small.get_width() / 2 and self.screen.get_height() - button_small.get_height() * 2 <= mouse[1] <= self.screen.get_height() - button_small.get_height():
                pg.draw.rect(self.screen, (255, 255, 255), (self.screen.get_width() / 2 - button_small.get_width() / 2, self.screen.get_height() - button_small.get_height() * 2, button_small.get_width(), button_small.get_height()), 2)
                mouse_hand = True
            self.screen.blit(font.render("Quit Game", True, (255, 255, 255)), (self.screen.get_width() / 2 - font.size("Quit Game")[0] / 2, self.screen.get_height() - button_small.get_height() * 1.5 - font.size("FullScreen : ON")[1] / 2))

            if mouse_hand:
                pg.mouse.set_cursor(pg.SYSTEM_CURSOR_HAND)
            else:
                pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)

            pg.display.update()


pg.init()
font_mojang = pg.font.Font("fonts/fs-mojang-studios-2.ttf", 120)
font_mojang2 = pg.font.Font("fonts/fs-mojang-studios-2.ttf", 40)
font1 = pg.font.Font("fonts/Comfortaa-Bold.ttf", 50)
font2 = pg.font.Font("fonts/Mojang-Regular.ttf", 20)
logo = pg.transform.scale_by(pg.image.load("src/logo1.png"), 0.12)
button = pg.transform.scale_by(pg.image.load("intrface gui/button.png"), 2)
button_small = pg.transform.scale(pg.image.load("intrface gui/button.png"), (180, 40))
icon = pg.image.load("src/icon.png")
pg.display.set_icon(icon)
myappid = 'mycompany.myproduct.subproduct.version'  # icon
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
pg.display.set_caption("minecrfat by The Boys")
font1.set_bold(True)
with open('surface.pickle', 'rb') as file:
    surface_arrays = pickle.load(file)
screen_info = pg.display.Info()
width, height = 1500, 900
settings = Settings(screen_info)
surfaces = []
# surfaces = pg.image.load("src/frame_0.jpg")


def main():


    screen = pg.display.set_mode((width, height))
    settings.screen = screen


    bar_size = font_mojang.size("Mojang")[0] + 50 - 10
    bar_size /= 450

    index = 0

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    sys.exit()
        screen.fill((239, 51, 62))
        screen.blit(font_mojang.render("The Boys", True, (255, 255, 255)),(screen.get_width() / 2 - font_mojang.size("Mojang")[0] / 2,screen.get_height() / 2 - font_mojang.size("Mojang")[1]))
        screen.blit(font1.render("STUDIOS", True, (255, 255, 255)),(screen.get_width() / 2 - font1.size("STUDIOS")[0] / 2,screen.get_height() / 2 + font1.size("STUDIOS")[1] / 2))
        pg.draw.rect(screen, (255, 255, 255), (screen.get_width() / 2 - (font_mojang.size("Mojang")[0] + 50) / 2, screen.get_height() / 2 + font1.size("STUDIOS")[1] + 50, font_mojang.size("Mojang")[0] + 50, 30), 3)
        # surfaces.append(pg.surfarray.make_surface(surface_arrays[index]))
        surfaces.append(pg.surfarray.make_surface(surface_arrays[index]))
        pg.draw.rect(screen, (255, 255, 255), (screen.get_width() / 2 - (font_mojang.size("Mojang")[0] + 50) / 2 + 5, screen.get_height() / 2 + font1.size("STUDIOS")[1] + 50 + 5,index * bar_size, 30 - 10))
        index += 1
        if index == 450:
            break
        pg.display.update()
    settings.screen = screen
    start_window(settings)


def start_window(settings):
    screen = settings.screen
    start_black_filter = False
    past_time = time()
    alpha = 0
    black_filter_going_on = True
    index = 0

    start_new_singel_game = False
    pg.mixer.init()
    settings.menu_track = pg.mixer.Sound('music/menu.mp3')
    settings.menu_track.play(-1)
    settings.menu_track.set_volume(settings.music_volume)

    while True:
        mouse_hand = False

        mouse = pg.mouse.get_pos()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                if screen.get_width() / 2 - button.get_width() / 2 <= mouse[0] <= screen.get_width() / 2 + button.get_width() / 2 and screen.get_height() / 2 - button.get_height() * 2 <= mouse[1] <= screen.get_height() / 2 - button.get_height() * 1:
                    start_new_singel_game = True
                elif screen.get_width() / 2 - button.get_width() / 2 <= mouse[0] <= screen.get_width() / 2 + button.get_width() / 2 and screen.get_height() / 2 - button.get_height() * .5 <= mouse[1] <= screen.get_height() / 2 + button.get_height() * .5:
                    client(settings)
                elif screen.get_width() / 2 - button.get_width() / 2 <= mouse[0] <= screen.get_width() / 2 - button.get_width() / 2 + button_small.get_width() and screen.get_height() / 2 + button_small.get_height() * 2 <= mouse[1] <= screen.get_height() / 2 + button_small.get_height() * 3:
                    settings.show = True
                elif screen.get_width() / 2 + button.get_width() / 2 - button_small.get_width() <= mouse[0] <= screen.get_width() / 2 + button.get_width() / 2 and screen.get_height() / 2 + button_small.get_height() * 2 <= mouse[1] <= screen.get_height() / 2 + button_small.get_height() * 3:
                    sys.exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    sys.exit()

        if time() - past_time >= 0.1 and not settings.show:
            screen.blit(surfaces[index], (0, 0))
            # screen.blit(surfaces, (0, 0))
            index += 1
            past_time = time()
            index = index % 450
            if index == 400:
                start_black_filter = True
            if start_black_filter:
                black_filter = pg.surface.Surface((screen.get_width(), screen.get_height()))
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
                        index = randint(70, 380)
                        index = 0
        if settings.show:
            settings.show_settings_interface()
            screen = settings.screen
        screen.blit(logo, (screen.get_width() / 2 - logo.get_width() / 2, logo.get_height()))
        screen.blit(button, (screen.get_width() / 2 - button.get_width() / 2, screen.get_height() / 2 - button.get_height() * 2))
        screen.blit(font2.render("Singleplayer", True, (255, 255, 255)), (screen.get_width() / 2 - font2.size("Singleplayer")[0] / 2, screen.get_height() / 2 - button.get_height() * 1.5 - font2.size("0")[1] / 2))
        if screen.get_width() / 2 - button.get_width() / 2 <= mouse[0] <= screen.get_width() / 2 + button.get_width() / 2 and screen.get_height() / 2 - button.get_height() * 2 <= mouse[1] <= screen.get_height() / 2 - button.get_height() * 1 :
            mouse_hand = True
            pg.draw.rect(screen, (255, 255, 255), (screen.get_width() / 2 - button.get_width() / 2, screen.get_height() / 2 - button.get_height() * 2, button.get_width(), button.get_height()), 2)

        screen.blit(button, (screen.get_width() / 2 - button.get_width() / 2, screen.get_height() / 2 - button.get_height() * .5))
        screen.blit(font2.render("Multiplayer", True, (255, 255, 255)), (screen.get_width() / 2 - font2.size("Multiplayer")[0] / 2, screen.get_height() / 2 - font2.size("0")[1] / 2))
        if screen.get_width() / 2 - button.get_width() / 2 <= mouse[0] <= screen.get_width() / 2 + button.get_width() / 2 and screen.get_height() / 2 - button.get_height() * .5 <= mouse[1] <= screen.get_height() / 2 + button.get_height() * .5:
            mouse_hand = True
            pg.draw.rect(screen, (255, 255, 255), (screen.get_width() / 2 - button.get_width() / 2, screen.get_height() / 2 - button.get_height() * .5, button.get_width(), button.get_height()), 2)

        screen.blit(button_small, (screen.get_width() / 2 - button.get_width() / 2, screen.get_height() / 2 + button.get_height() * 2))
        screen.blit(font2.render("Options", True, (255, 255, 255)), (screen.get_width() / 2 - button.get_width() / 2 + button_small.get_width() / 2 - font2.size("Options")[0] / 2, screen.get_height() / 2 + button_small.get_height() * 2 + font2.size("0")[1] / 2))
        if screen.get_width() / 2 - button.get_width() / 2 <= mouse[0] <= screen.get_width() / 2 - button.get_width() / 2 + button_small.get_width() and screen.get_height() / 2 + button_small.get_height() * 2 <= mouse[1] <= screen.get_height() / 2 + button_small.get_height() * 3:
            mouse_hand = True
            pg.draw.rect(screen, (255, 255, 255), (screen.get_width() / 2 - button.get_width() / 2, screen.get_height() / 2 + button_small.get_height() * 2, button_small.get_width(), button_small.get_height()), 2)

        screen.blit(button_small, (screen.get_width() / 2 + button.get_width() / 2 - button_small.get_width(), screen.get_height() / 2 + button.get_height() * 2))
        screen.blit(font2.render("Quit Game", True, (255, 255, 255)), (screen.get_width() / 2 + button.get_width() / 2 - button_small.get_width() / 2 - font2.size("Quit Game")[0] / 2, screen.get_height() / 2 + button_small.get_height() * 2 + font2.size("0")[1] / 2))
        if screen.get_width() / 2 + button.get_width() / 2 - button_small.get_width() <= mouse[0] <= screen.get_width() / 2 + button.get_width() / 2 and screen.get_height() / 2 + button_small.get_height() * 2 <= mouse[1] <= screen.get_height() / 2 + button_small.get_height() * 3:
            mouse_hand = True
            pg.draw.rect(screen, (255, 255, 255), (screen.get_width() / 2 + button.get_width() / 2 - button_small.get_width(), screen.get_height() / 2 + button_small.get_height() * 2, button_small.get_width(), button_small.get_height()), 2)
        font2.set_bold(True)
        screen.blit(pg.transform.rotate(font2.render("By The Boys", True, (204, 204, 0)), 45), (screen.get_width() / 2 + logo.get_width() / 2 - 48, logo.get_height() + 2))
        font2.set_bold(False)
        screen.blit(pg.transform.rotate(font2.render("By The Boys", True, (255, 255, 0)), 45), (screen.get_width() / 2 + logo.get_width() / 2 - 50, logo.get_height()))

        if mouse_hand:
            pg.mouse.set_cursor(pg.SYSTEM_CURSOR_HAND)
        else:
            pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)
        pg.display.update()



if __name__ == "__main__":
    main()

