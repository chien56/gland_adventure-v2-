import pygame, sys, os, random

clock = pygame.time.Clock()#met en place l'horloge
from pygame.locals import*  #importe les modules pygame

pygame.init() #initie pygame
pygame.mixer.pre_init(44100, -16, 2, 512)
objects = []
pygame.mixer.set_num_channels(64)

pygame.display.set_caption('gland_adventure')#nomme la fenetre
fullscreen = False
WINDOW_SIZE = (1200, 800)#donne la taille de la fenetre
if fullscreen == True :
    ScreenSize = pygame.display.get_desktop_sizes()
    screen = pygame.display.set_mode(ScreenSize[0], 0, 32)

else :
    screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)#initie la fenetre


display = pygame.Surface((600, 400))
def text_objects(text, font):
    textSurface = font.render(text, True, (0,0,0))
    return textSurface, textSurface.get_rect()


def button(x,y,hauteur,largeur,message,couleur, fonction):
    pygame.draw.rect(screen, couleur, pygame.Rect(x,y,largeur,hauteur)) #créer un rectangle
    largetext = pygame.font.SysFont('Arial',25) # définie la police du texte
    largetextsurf = largetext.render(message, True, (0,0,0)) # créer le texte
    screen.blit(largetextsurf, (x,y)) # affiche le texte
    return (x, y, x+largeur, y+hauteur, fonction) #renvoie les coordonées du bouton et la fonction qu'il devra éxécuter


def game() :
    grass_image = pygame.image.load('images terrain/grass.png')
    dirt_image = pygame.image.load('images terrain/dirt.png')
    stone_image = pygame.image.load('images terrain/stone.png')

    jump_sound = pygame.mixer.Sound('sons/jump.wav')
    grass_sounds = [pygame.mixer.Sound('sons/grass_0.wav'), pygame.mixer.Sound('sons/grass_1.wav')]
    grass_sounds[0].set_volume(0.2)
    grass_sounds[1].set_volume(0.2)

    pygame.mixer.music.load('music.mp3')
    pygame.mixer.music.play(-1)#nombre de repetitions (negatif=indefiniment)

    TILE_SIZE = grass_image.get_width()

    def load_map(path):
        f= open(path + '.txt','r') # <-
        data = f.read()
        f.close()
        data = data.split('\n')
        game_map = []
        for row in data:
            game_map.append(list(row))
        return game_map



    global animation_frames #<-- cette variable est la meme que celle definie a l'exterieur de la fonction
    animation_frames ={}
    def load_animations(path, frame_durations):
        global animation_frames
        animation_name = path.split('/')[-1]
        animation_frame_data = []
        n=0
        for frame in frame_durations:
            animation_frame_id = animation_name + '_' + str(n)
            img_loc = path + '/' + animation_frame_id + '.png'#player animations/course/course_1.png --------- le nom des fichiers d'animation est important

            animation_image = pygame.image.load(img_loc).convert_alpha()
    #        if img_loc == "animations player/immobile/immobile_0.png" : # Si l'image chargé est immobile_0.png
    #            animation_image = pygame.transform.scale(animation_image,(55,55)) # changer la taille de l'image à tant de pixel sur tant de pixel
            #animation_image.set_colorkey((0, 0, 0)) #supprime le noir des sprites au besoin
            animation_frames[animation_frame_id] = animation_image.copy()
            for i in range(frame):
                animation_frame_data.append(animation_frame_id)
            n+=1
        return animation_frame_data

    def change_action(action_var, frame, new_value):
        if action_var != 0:
            action_var = new_value
            frame=0
        return action_var, frame

    animation_database = {'course': load_animations('animations player/course', [7, 7, 7, 7, 7, 7, 7]),
                          'immobile': load_animations('animations player/immobile', [7, 10]),
                          'saut': load_animations('animations player/saut', [7, 7, 7, 7])}
    player_action = 'immobile'
    player_frame = 0
    player_flip = False

    grass_sound_timer = 0

    player_rect = pygame.Rect(50, 50, 35, 55) #taille de la hitbox, a voir dans le futur pour mettre ça en variable

    game_map = load_map('map')#pas beson de mettre .txt

    background_objects = [[0.25,[240,20,140,800]],[0.25,[560,60,80,800]],[0.5,[60,80,80,800]],[0.5,[260,180,200,800]],[0.5,[600,160,240,800]]] # garder l'ordre croissant dans les multiplicateurs 0.25,...


    def collison_test(rect, tiles):
        hit_list = []
        for tile in tiles:
            if rect.colliderect(tile):
                hit_list.append(tile)
        return hit_list

    def move (rect, movement, tiles):
        collision_types = {'top' : False, 'bottom' : False, 'right' : False, 'left' : False}
        rect.x += movement[0]
        hit_list  = collison_test(rect, tiles)
        for tile in hit_list:
            if movement[0] > 0:
                rect.right = tile.left
                collision_types['right']=True

            elif movement[0] < 0:
                rect.left = tile.right
                collision_types['left']=True

        rect.y += movement[1]
        hit_list = collison_test(rect, tiles)
        for tile in hit_list:
            if movement[1] > 0:
                rect.bottom = tile.top
                collision_types['bottom']=True

            elif movement[1] < 0:
                rect.top = tile.bottom
                collision_types['top'] = True

        return rect, collision_types

    moving_right = False
    moving_left = False


    player_y_momentum = 0#impulsion
    air_timer =0

    true_scroll = [0, 0]


    ########################################################################################################################
    while True: #boucle du jeu
        display.fill((90, 68, 50))

        if grass_sound_timer > 0:
            grass_sound_timer -= 1

        true_scroll[0] += (player_rect.x - true_scroll[0] - 600//2 + 38)/20 #motié du display pour centrer la caméra - la largeur du player
        true_scroll[1] += (player_rect.y - true_scroll[1] - 400//2 + 100)/20
        scroll = true_scroll.copy()
        scroll[0] = int(scroll[0])
        scroll[1] = int(scroll[1])

        pygame.draw.rect(display, (7, 80, 75), pygame.Rect(0, 240, 600, 160))#rectangle de background (doubler toutes les valeurs si prises du tuto)
        for background_object in background_objects:
            obj_rect = pygame.Rect(background_object[1][0] - scroll[0]*background_object[0], background_object[1][1] - scroll[1]*background_object[0], background_object[1][2], background_object[1][3])
            if background_object[0] == 0.5:
                pygame.draw.rect(display, (14, 222, 150), obj_rect)
            else:
                pygame.draw.rect(display, (9, 91, 85), obj_rect)


        tile_rects = []
        y=0
        for row in game_map:
            x=0
            for tile in row:
                if tile =='1':
                    display.blit(dirt_image, (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
                if tile == '2':
                    display.blit(grass_image, (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
                if tile == '3':
                    display.blit(stone_image, (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
                if tile != '0':
                    tile_rects.append(pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
                x+=1
            y+=1



        player_movement = [0,0]# "vitesse" horizontale et verticale
        if moving_right:
            player_movement[0] += 2
        if moving_left:
            player_movement[0] -= 2
        player_movement[1] = player_y_momentum
        player_y_momentum += 0.6 #vitesse de chute
        if player_y_momentum > 4: #accélération de chute
            player_y_momentum = 4

        if player_movement[0]>0:
            player_action, player_frame = change_action(player_action, player_frame, 'course')#il se met a courir (droite)
            player_flip=False
        if player_movement[0]<0:
            player_action, player_frame = change_action(player_action, player_frame, 'course')#(gauche)
            player_flip=True

        if player_movement[0]==0:
            player_action, player_frame = change_action(player_action, player_frame, 'immobile')#



        player_rect, collisions = move(player_rect, player_movement, tile_rects)

        if collisions['bottom']:
            player_y_momentum = 0
            air_timer=0
            if player_movement[0] != 0:
                if grass_sound_timer==0:
                    grass_sound_timer=30
                    random.choice(grass_sounds).play()
            if player_movement[0] < 0:
                player_action, player_frame = change_action(player_action, player_frame, 'saut')  # (saut droit)
                player_flip = False
            if player_movement[0] > 0:
                player_action, player_frame = change_action(player_action, player_frame, 'saut')  # (saut gauche)
                player_flip = True

        else:
            air_timer+=1

        if collisions['top']:
            player_y_momentum = 1

        player_frame += 1
        if player_frame>= len(animation_database[player_action]): #boucle d'animation
            player_frame=0

        player_img_id = animation_database[player_action][player_frame]

        player_image = animation_frames[player_img_id] # donne l'image du joueur actuelle

        display.blit(pygame.transform.flip(player_image, player_flip, False), (player_rect.x - scroll[0], player_rect.y - scroll[1]))

        for event in pygame.event.get():#boucle d'evenement d'entrée

            if event.type == QUIT:#verifie si la croix est pressée
                pygame.quit()#quitte pygame
                sys.exit()#ferme le script
            if event.type == VIDEORESIZE :
                print("a")
            if event.type == KEYDOWN:
                if event.key == K_w:
                    pygame.mixer.music.fadeout(1000)
                if event.key == K_x:
                    pygame.mixer.music.play(-1)
                if event.key == K_RIGHT:
                    moving_right = True
                if event.key == K_LEFT:
                    moving_left = True
                if event.key == K_UP:
                    if air_timer < 13: #peut sauter dans ce laps de temps, utile pour sauter apres une plateforme
                        jump_sound.play()
                        player_y_momentum= -11 #hauteur de saut

            if event.type == KEYUP:
                if event.key == K_RIGHT:
                    moving_right = False
                if event.key == K_LEFT:
                    moving_left = False


        if fullscreen == False :
            surf = pygame.transform.scale(display, WINDOW_SIZE)
        else:
            surf = pygame.transform.scale(display, ScreenSize[0])
        screen.blit(surf, (0, 0))
        pygame.display.update()#rafraichit l'ecran
        clock.tick(60)#maintient 60 fps

def menu(resolution, screen):
    inmenu = True # le jouer est dans le menu
    background = pygame.image.load('Image_Menu/background.jpg') # charge l'image de fond
    background = background.convert_alpha()
    background = pygame.transform.scale(background, resolution) #dimensionne l'image de fond à la taille de l'écran

    while inmenu:
        screen.blit(background, (0,0)) # affiche le fond
        poitionButton = button(resolution[0]/2 -100 , resolution[1]/2 - 25, 50, 200, "Jouer", (255, 0, 0), "game()") #créer et affiche le bouton jouer
        positionButton2 = button(resolution[0]/2 - 100, resolution[1]/2 + 100 , 50, 200, "Quitter", (255,0,0),"pygame.quit()") #créer et affiche le bouton quitter


        for event in pygame.event.get():#boucle d'evenement d'entrée

            if event.type == QUIT:#verifie si la croix est pressée
                pygame.quit()#quitte pygame
                sys.exit()#ferme le script
            if event.type == MOUSEBUTTONUP: # si clique gauche
                pos = pygame.mouse.get_pos() # récupère la position du clique

                if pos[0] >= poitionButton[0] and pos[0] <= poitionButton[2] and pos[1] >= poitionButton[1] and pos[1] <= poitionButton[3]: # Vérifie si le click est sur le bouton 1
                    exec(poitionButton[4]) #execute la fonction du bouton 1
                if pos[0] >= poitionButton[0] and pos[0] <= positionButton2[2] and pos[1] >= positionButton2[1] and pos[1] <= positionButton2[3]: # Vérifie si le click est sur le bouton 2
                    exec(positionButton2[4]) #éxecute la fonction du bouton 2


        pygame.display.update()
        clock.tick(60)



if fullscreen:
    menu(ScreenSize[0], screen)
else:
    menu(WINDOW_SIZE,screen)