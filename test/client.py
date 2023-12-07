import pygame
from network import Network

width = 500
height = 500
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Client")

clientNumber = 0


class Player():
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.rect = (x,y,width,height)
        self.vel = 3

    def draw(self, win):
        pygame.draw.rect(win, self.color, self.rect)

    def move(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.x -= self.vel

        if keys[pygame.K_RIGHT]:
            self.x += self.vel

        if keys[pygame.K_UP]:
            self.y -= self.vel

        if keys[pygame.K_DOWN]:
            self.y += self.vel

        self.update()

    def update(self):
        self.rect = (self.x, self.y, self.width, self.height)


def read_pos(string):
    print(string)

    if string == "NO_PLAYERS":
        return []
    string = string.split(":")
    print(string)

    decode = []
    for element in string:
        element = element.split(",")
        decode.append((int(element[0]), int(element[1])))
    print(decode)

    return decode


def make_pos(tup):
    return str(tup[0]) + "," + str(tup[1])


def redrawWindow(win,player, other_players):
    win.fill((255,255,255))
    player.draw(win)
    for element in other_players:
        element.draw(win)
    pygame.display.update()


def main():
    run = True
    n = Network()
    startPos = read_pos(n.getPos())

    p = Player(startPos[0][1],startPos[0][1],50,50,(0,255,0))
    other_players_pos = []
    other_players = []
    clock = pygame.time.Clock()
    nmr_of_players = 0
    while run:

        clock.tick(60)
        if nmr_of_players == 0:
            print(other_players_pos)
            print("lol")

            other_players_pos = read_pos(n.send(make_pos((p.x, p.y))))
            print(other_players_pos)

            if len(other_players_pos) == 0:
                print("no players")
            elif nmr_of_players != len(other_players_pos):
                other_players = []
                for element in other_players_pos:
                    other_players.append(Player(element[0], element[1], 50, 50, (255, 0, 0)))
            else:
                for index, element in enumerate(other_players):
                    element.x = other_players_pos[index][0]
                    element.y = other_players_pos[index][1]
                    element.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        p.move()
        redrawWindow(win, p, other_players)

main()