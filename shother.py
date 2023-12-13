import pygame
import os
import random

# shother.py
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)
TILE_SIZE = 20  # tamaño del mosaico

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Shooter")

# set frame rate limit
clock = pygame.time.Clock()
FPS = 60
# define game vsriables
GRAVITY = 0.75

# define player action variables
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

# bullet
bullet_img = pygame.image.load(
    "images/gui/hi_overlays/hi_overlay_variant_cubes_x1_1_png_1354840427.png"
).convert_alpha()

# grenade
grenade_img = pygame.image.load(
    "images/gui/hi_overlays/hi_overlay_variant_rocketships_x1_1_png_1354840462.png"
).convert_alpha()

###-----------------------box (buscar split)-------->
# pick up boxes
health_box_img = pygame.image.load(
    "images/tileset/forest/Objects/Mushroom_2.png"
).convert_alpha()
ammo_box_img = pygame.image.load(
    "images/tileset/forest/Objects/Crate.png"
).convert_alpha()
grenade_box_img = pygame.image.load(
    "images/tileset/forest/Objects/Mushroom_1.png"
).convert_alpha()
item_boxes = {
    "Health": health_box_img,
    "Ammo": ammo_box_img,
    "Grenade": grenade_box_img,
}
###------------------------------->
# define colours
BG = (144, 201, 120)
RED = (255, 0, 0)
WHILE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
font = pygame.font.SysFont("Futura", 30)


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def draw_bg():
    screen.fill(BG)


class Soldier(pygame.sprite.Sprite):  # voy
    def __init__(
        self, char_type, x, y, scale, speed, ammo, grenades
    ):  # propios de cada objeto
        pygame.sprite.Sprite.__init__(self)
        # voy a heredar algunas de las funcionabilidades de la clase sprite
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo  # municiones
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.grenades = grenades

        self.health = 100  # salud
        self.max_health = self.health

        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        # invoca to action list in particular,cotrola las acciones del fotograma
        self.action = 0

        # ai specific variables
        self.move_counter = 0
        self.idling = False
        self.idling_counter = False
        self.vision = pygame.Rect(0, 0, 130, 20)

        self.update_time = pygame.time.get_ticks()

        # load all images for the players
        animation_types = ["Idle", "Run", "Jump", "Dead"]

        for animation in animation_types:
            # reset temporary list of images
            temp_list = []

            # count number of files in the folder
            num_of_frames = len(
                os.listdir(f"images/caracters/{self.char_type}/{animation}")
            )

            for i in range(num_of_frames):
                # images/caracters/player/Idle
                # images/caracters/enemy/Idle/Idle (6).png

                if i > 0 and i <= num_of_frames:
                    img = pygame.image.load(
                        f"images/caracters/{self.char_type}/{animation}/{animation} ({i}).png"
                    ).convert_alpha()
                    img = pygame.transform.scale(
                        img,
                        (int(img.get_width() * scale), int(img.get_height() * scale)),
                    )  # "self." es una variable de instancia,sera especifico para ese jugador
                    temp_list.append(img)

            self.animation_list.append(temp_list)  # list of lists

        self.image = self.animation_list[self.action][
            self.frame_index
        ]  # depende de la "action" q me encuentre llamare al "index" del fotograma de de esa lista de acciones en particular
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    #########cooldown########>>>
    def update(self):
        self.update_animation()
        self.check_alive()

        # update cooldown/ actualization time of reutilization
        if self.shoot_cooldown > 0:  # if end of cooldown(disparar)
            self.shoot_cooldown -= 1
            print("self.shoot_cooldown -= 1", self.shoot_cooldown)

    #################>>>

    def move(self, moving_left, moving_right):
        # reset movments variaables
        dx = 0
        dy = 0

        # assign movement varables if moving_left or moving_rigth
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1
        # jump
        if self.jump == True and self.in_air == False:
            self.vel_y = -10
            self.jump = False
            self.in_air = True

        # apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y  # reiniciamos la velocidad a 10
        dy += self.vel_y
        # check collision with floor
        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.in_air = False
            # self.speed = 0

        # update rectangle position
        self.rect.x += dx
        self.rect.y += dy

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(
                self.rect.centerx + (0.80 * self.rect.size[0] * self.direction),
                self.rect.centery,
                player.direction,
            )

            bullet_group.add(bullet)
            # reduce ammo
            self.ammo -= 1

    # PATRULLA
    def ai(self):
        # --------- buscar una verificacion de inactivo(si el enemy ve al jugador)
        if self.alive and player.alive:
            # estado inactivo y estado no inactivo
            if (
                self.idling == False and random.randint(1, 200) == 1
            ):  # controla la probabilidad de que la accion suceda
                self.update_action(0)  # 0: idle , cero esta inactivo
                self.idling = True  # funciona en realenti
                self.idling_counter = 50
            # --------- ///////////////////

            # check if the ai in near the player

            if self.vision.colliderect(player.rect):
                # stop running and face the player
                self.update_action(0)  # 0 :idle
                # shoot
                self.shoot()

            # --------- movimimento y contador inactivo(si el enemy no lo ve continua la patrulla)
            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_rigth = True
                    else:
                        ai_moving_rigth = False
                    ai_moving_left = not ai_moving_rigth
                    self.move(ai_moving_left, ai_moving_rigth)
                    self.update_action(1)  # run
                    self.move_counter += 1

                    # update ai vision as the enemy moves
                    self.vision.center = (
                        self.rect.centerx + 50 * self.direction,
                        self.rect.centery,
                    )
                    pygame.draw.rect(
                        screen, RED, self.vision
                    )  ##veo el rectangulo, ouedo borrar esta linea

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = (
                            False  # se detiene el realenti y puede volver a caminar
                        )

    def update_animation(self):
        # update animation state
        ANIMATION_COOLDOWN = 100  # control animation speed

        # update image depending on currenet frame rate
        self.image = self.animation_list[self.action][self.frame_index]

        # check is enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action] - 1)
            else:
                self.frame_index = 0
        ###"Idle", "Run", "Jump", "Dead"

    #  metod que verifica si hay una nueva accion y luego utilizo la misma en consecuencia
    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            # update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)
            ######-animation_types = ["Idle", "Run", "Jump", "Dead"]

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        pygame.draw.rect(screen, RED, self.rect, 1)


class ItemBox(pygame.sprite.Sprite):  # cuadro de elementos
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (
            x + TILE_SIZE // 2,
            y + (TILE_SIZE - self.image.get_height()),
        )

    def update(self):
        # check if the player has picked up the box
        if pygame.sprite.collide_rect(self, player):
            if self.item_type == "Health":
                print(player.health)
                player.health += 10
                print(player.health)
                if player.health > player.max_health:
                    player.health = player.max_health

            elif self.item_type == "Ammo":  # municiones
                player.ammo += 10
            elif self.item_type == "Grenade":
                player.grenades += 5

            # delete the item box
            self.kill()


class HealthBar:
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        # updatewith new health
        self.health = health
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        # calculate health radio
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154 * ratio, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect_center = (x, y)
        self.direction = direction

    def update(self):
        # move bullet
        self.rect.x += self.direction * self.speed
        # check if bullet has gone off screen/si fue disparada
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
            print("check if bullet has gone off screen/si fue disparada")

        # check collition with characters
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                print("# check collition with characters", player.health)
                self.kill()
                print("se elimino bullet")

        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 25
                    print(enemy.health)
                    self.kill()


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel__y = -11
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect_center = (x, y)
        self.direction = direction

    def update(self):
        self.vel__y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel__y

        # check collision with floor
        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.speed = 0
            print("grenade check collision with floor")

        # check collision with walls
        if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
            self.direction *= -1
            dx = self.direction * self.speed
            print("grenade check collision with walls")

        # update grenade position
        self.rect.x += dx
        self.rect.y += dy
        ### cuntdown timer
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            explosion = Explosion(self.rect.x, self.rect.y, 0.5)
            explosion_group.add(explosion)
            # do damage to anyone that is nearby

            if (
                abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2
                and abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2
            ):
                player.health -= 50
            for enemy in enemy_group:
                if (
                    abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2
                    and abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2
                ):
                    enemy.health -= 50
                    print(enemy.health)

    # -----------------------EXPLOSION GRENADE


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.image = []
        for num in range(1, 4):
            img = pygame.image.load(
                f"images/caracters/players/warrior_woman_03/1_IDLE_00{num}.png"
            ).convert_alpha()
            img = pygame.transform.scale(
                img, (int(img.get_width() * scale), int(img.get_height() * scale))
            )
            self.image.append(img)
        self.frame_index = 0
        self.images = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect_center = (x, y)
        self.counter = 0

    def updatee(self):
        EXPLOSION_SPEED = 4

        # update explosion animation
        self.counter += 1
        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1

            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.image[self.frame_index]


# creante sprite group
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

##-------------boxes--------------
item_box_group = pygame.sprite.Group()
# temp - create item boxes
item_box = ItemBox("Health", 200, 250)
item_box_group.add(item_box)
item_box = ItemBox("Ammo", 400, 250)
item_box_group.add(item_box)
item_box = ItemBox("Grenade", 600, 250)
item_box_group.add(item_box)


##-------------boxes--------------
player = Soldier("player", 50, 300, 0.09, 5, 4, 10)  # creo una instancia
health_bar = HealthBar(10, 10, player.health, player.health)

enemy = Soldier("enemy", 300, 200, 0.04, 2, 20, 0)
enemy2 = Soldier("enemy", 500, 200, 0.04, 5, 20, 0)
enemy_group.add(enemy)
enemy_group.add(enemy2)

run = True
while run:
    clock.tick(FPS)
    draw_bg()
    # show  player health
    health_bar.draw(player.health)

    """ # show ammo
    draw_text(f"AMMO: ", font, WHILE, 10, 35)
    for x in range(player.ammo):
        screen.blit(bullet_img, (90 + (x + 10), 40))

    # show grenade
    draw_text(f"GRENADE: ", font, WHILE, 10, 60)
    for x in range(player.grenades):
        screen.blit(grenade_img, (135 + (x + 15), 60)) """
    # show ammo
    draw_text(f"fAMMO: {player.ammo} ", font, WHILE, 10, 35)
    for x in range(player.ammo):
        screen.blit(bullet_img, (90 + (x + 10), 40))

    # show grenade
    draw_text(f"GRENADE: {player.grenades} ", font, WHILE, 10, 60)
    for x in range(player.grenades):
        screen.blit(grenade_img, (135 + (x + 15), 60))
    # player.ai()
    player.update()
    player.draw()

    for enemy in enemy_group:
        enemy.ai()
        enemy.update()
        enemy.draw()

    # update and draw groups
    bullet_group.update()
    bullet_group.draw(screen)

    grenade_group.update()
    grenade_group.draw(screen)

    explosion_group.update()
    explosion_group.draw(screen)

    item_box_group.update()
    item_box_group.draw(screen)

    # update player actions
    if player.alive:  # perfec transition for player actions
        if shoot:
            # shoot bullet
            player.shoot()

            # thow granades
        elif grenade and grenade_thrown == False and player.grenades > 0:
            grenade = Grenade(
                player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),
                player.rect.top,
                player.direction,
            )
            grenade_group.add(grenade)

            # reduce grenades
            player.grenades -= 1
            grenade_thrown = True
            print("player.grenades:", player.grenades)

        if player.in_air:
            player.update_action(2)  # 2: jump
        elif moving_left or moving_right:
            player.update_action(1)  # 1: run/ejecutar action
        else:
            player.update_action(0)  # 0: idle
        player.move(moving_left, moving_right)

    for event in pygame.event.get():
        # quit game
        if event.type == pygame.QUIT:
            run = False
        # keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                moving_left = True
            if event.key == pygame.K_RIGHT:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
                print("shoot:", shoot)
            if event.key == pygame.K_g:
                granade = True
                print("granade:", granade)
                grenade_thrown = True  # granada lanzada
            if event.key == pygame.K_s and player.alive:
                player.jump = True
            if event.key == pygame.K_ESCAPE:
                run = False

        # keyboard buttons releassed
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                moving_left = False
            if event.key == pygame.K_RIGHT:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_g:
                granade = False
                grenade_thrown = False  # granada lanzada
                print(grenade_thrown)

    pygame.display.update()
pygame.quit()
