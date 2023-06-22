import pygame, sys, os, random, time
from pygame.sprite import Group
from enemy import Enemy

clock = pygame.time.Clock()#met en place l'horloge

from pygame.locals import* #importe les modules pygame
pygame.init() #initie pygame
pygame.mixer.pre_init(44100, -16, 2, 512)#prepare le mixer de son pour que le son sur le canal sorte direct

pygame.mixer.set_num_channels(64) #definit le nombre de sons pouvant etre joués en meme temps

pygame.display.set_caption('gland_adventure')#nomme la fenetre

WINDOW_SIZE = (1200, 800)#donne la taille de la fenetre
fullscreen = False#definit si le mode plein ecran est actif
if fullscreen:                                       #si plein ecran
    ScreenSize = pygame.display.get_desktop_sizes()    #recupere la taille de l'ecran d'ordi
    screen = pygame.display.set_mode(ScreenSize[0], 0, 32) # la taille de l'ecran s'adapte a celle de la resolution de l'ordi

else :
    screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32) #initie la fenetre


display = pygame.Surface((600, 400)) #definit combien de pixels vont etre utilisés dans la fenetre


enemy_image = pygame.image.load('enemy.png').convert_alpha() #charge image ennemi
caisse_image = pygame.image.load('caisse .png').convert_alpha() #charge image caisse
key_image = pygame.image.load('key.png').convert_alpha()#charge image clé


grass_image = pygame.image.load('images terrain/grass.png').convert_alpha() #charge image herbe
dirt_image = pygame.image.load('images terrain/dirt.png').convert_alpha()#charge image terre
stone_image = pygame.image.load('images terrain/stone.png').convert_alpha()#charge image pierre
pics_image = pygame.image.load('pics.png').convert_alpha()#charge image pics
door_image = pygame.image.load('door.png').convert_alpha()#charge image porte

jumper_image = pygame.image.load('champi.png').convert_alpha() #charge image champi rebondissant
JUMPER_WIDTH = jumper_image.get_width() #recupere la largeur du champi
JUMPER_HEIGHT = jumper_image.get_height() #recupere la hauteur du champi

icone = pygame.image.load('icon_g.png').convert_alpha() #charge l'icone de la fenetre
pygame.display.set_icon(icone) #met en place l'icone
class jumper_obj(): #cree une classe pour tout objet rebondissant
    def __init__(self, loc): #initie grace aux coordonées
        self.loc = loc # recupere les coordonnées
    def render(self, surf, scroll):#affiche grace a la surface (surf) et au scroll(camera)
        surf.blit(jumper_image, (self.loc[0]-scroll[0], self.loc[1]-scroll[1])) #affiche le jumper
    def get_rect(self):#obtient le rect
        return pygame.Rect(self.loc[0], self.loc[1], JUMPER_WIDTH, JUMPER_HEIGHT )
    def collision_test(self, rect):#test de collision avec un rect mis en argument
        jumper_rect = self.get_rect() #obtient le rect du jumper
        return jumper_rect.colliderect(rect) #verifie la collision

class breakable_obj(): #cree une classe pour tout objet rebondissant
    def __init__(self, loc): #initie grace aux coordonées
        self.loc = loc # recupere les coordonnées
    def render(self, surf, scroll, image):#affiche grace a la surface (surf) et au scroll(camera)
        surf.blit(image, (self.loc[0]-scroll[0], self.loc[1]-scroll[1])) #affiche le jumper
    def get_rect(self):#obtient le rect
        return pygame.Rect(self.loc[0], self.loc[1], JUMPER_WIDTH, JUMPER_HEIGHT )
    def collision_test(self, rect):#test de collision avec un rect mis en argument
        caisse_rect = self.get_rect() #obtient le rect du jumper
        return caisse_rect.colliderect(rect) #verifie la collision

shoot_image = pygame.image.load('shoot.png').convert_alpha() #charge image tir

class Long_range(): #cree une classe pour armes a distance
    def __init__(self, loc,taille, direction, image, degats, portee): #initie les variables avec les arguments donnés
        self.degats = degats
        self.portée = portee
        self.loc = loc
        self.image = image
        self.taille = taille
        self.direction = direction
        self.rect = pygame.Rect(self.loc[0], self.loc[1], self.taille[0], self.taille[1])
    def afficher(self, surface, delta_temps): #affiche en plus grand si le temps d'appui de touche est superieur a 1.2s
        if delta_temps > 1.2:
            self.image = pygame.transform.scale(self.image, (40, 40))
        surface.blit(self.image, self.rect)
    def mouvement(self, vitesse): #fait avancer le projectile en fonction de sa vitesse et l'oriente avec la direction
        self.rect.x += (vitesse * self.direction)
        self.rect[0] += vitesse * self.direction

pv = 150 #initialise les pv
jauge_vie = [20, 20, 150, 10] #initialise la position de la barre de vie


jump_sound = pygame.mixer.Sound('sons/jump.wav') #charge le son de saut
grass_sounds = [pygame.mixer.Sound('sons/grass_0.wav'), pygame.mixer.Sound('sons/grass_1.wav')] #charge les sons de pas
grass_sounds[0].set_volume(0.2) #met les sons de pas de la liste grass_sounds à 20%
grass_sounds[1].set_volume(0.2)

pygame.mixer.music.load('music.mp3') #charge la musique de fond
pygame.mixer.music.play(-1)#nombre de repetitions (negatif=indefiniment)

TILE_SIZE = grass_image.get_width() #obtient la taille d'une tuile en fonction d'une image(herbe)

def load_map(path): #charge la map grace a son nom
    f= open(path + '.txt','r') # <- ajoute .txt au nom donné
    data = f.read() # lit dans le fichier
    f.close() #ferme la map
    data = data.split('\n') #decoupe chaque nombre
    game_map = [] # liste qui contiendra la map
    for row in data: #crée des listes à chaque ligne
        game_map.append(list(row))
    return game_map #renvoie la map finale sous forme de liste



global animation_frames #<-- cette variable est la meme que celle definie a l'exterieur de la fonction
animation_frames ={} #crée un dictionnaire vide pr recueillir les animations /frame
def load_animations(path, frame_durations): #charge les animations en fonction de leur nom et leur durée en frames par animation
    global animation_frames
    animation_name = path.split('/')[-1]
    animation_frame_data = []
    n=0
    for frame in frame_durations:
        animation_frame_id = animation_name + '_' + str(n)
        img_loc = path + '/' + animation_frame_id + '.png'#player animations/course/course_1.png --------- le nom des fichiers d'animation est important
        animation_image = pygame.image.load(img_loc).convert_alpha()
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

animation_database = {}
animation_database['course']= load_animations('animations player/course', [8, 8, 8, 8, 8, 8, 8])#<- le dernier terme est le nombre de frame qui s'écoule entre chaque sprite
animation_database['immobile']=load_animations('animations player/immobile', [20, 5])
animation_database['saut']= load_animations('animations player/saut', [8, 20, 100, 8])
player_action = 'immobile'
player_frame = 0
player_flip = False

grass_sound_timer = 0

player_rect = pygame.Rect(128, 50, 32, 55) #taille de la hitbox, a voir dans le futur pour mettre ça en variable

game_map = load_map('mapversion2') #pas beson de mettre .txt

background_objects = [[0.25,[240,20,140,800]],[0.25,[560,60,80,800]],[0.5,[60,80,80,800]],[0.5,[260,180,200,800]],[0.5,[600,160,240,800]]] # garder l'ordre croissant dans les multiplicateurs 0.25,...

jumper_objects = []

direction_enemy =1

def collision_test(rect, tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list

def move (rect, movement, tiles):
    collision_types = {'top' : False, 'bottom' : False, 'right' : False, 'left' : False}
    rect.x += movement[0]
    hit_list  = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types['right']=True
        elif movement[0] < 0:
            rect.left = tile.right
            collision_types['left']=True
    rect.y += movement[1]
    hit_list = collision_test(rect, tiles)
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

in_air = False
course_d = False
course_g = False
immobile = True

t1, t2 = 0, 0
delta_temps = 0
joueur_a_tire = False
projectile_groupe = []
tir_autorise = 5
direction = 1

spawn_enemy_list = [] #crée la liste des coordonnées de spawn de chaque ennemi
y=0 #numero de ligne
for row in game_map:#pour chaque ligne
    x=0 #numero de case
    for tile in row:#pour chaque case de la ligne
        if tile == '5':
            spawn_enemy_list.append((x*TILE_SIZE, y*TILE_SIZE)) #permet d'obtenir les co de spawn des ennemi d'apres la map
        x+=1
    y+=1

ENEMY_HEIGHT = enemy_image.get_height()
ENEMY_WIDTH = enemy_image.get_width()
enemy_list=[] #crée une liste d'ennemis

for spawn in spawn_enemy_list:  # pour chaque coordonnées de spawn de la liste
    enemy = Enemy(spawn[0], spawn[1], (ENEMY_WIDTH, ENEMY_HEIGHT), enemy_image, 1)  # creer un ennemi a ces coordonnées
    enemy_list.append(enemy)  # l'ajouter a la liste d'ennemis
keys = 0


########################################################################################################################################################################
while True: #boucle du jeu
    display.fill((255, 128, 0)) #couleur de fond d'écran
    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])
    scroll[1] = int(scroll[1])
    tile_u = [0, 0, 0, 0]
    tile_rects = []

    for tile in tile_rects:
        tile_u = tile


    for enemy in enemy_list: #pour chaque ennemi dans la lioste d'ennemis
        enemy.x += 1 * enemy.direction #ajouter 1 a la pos x de l'ennemi
        enemy.rect[0] += 1* enemy.direction #actualiser l'ennemi rect en ajoutant 1 aussi
        enemy.y += 0 #ajouter 1 a la pos y de l'ennemi
        enemy.rect[1] += 0 #actualiser l'ennemi rect en ajoutant 1 aussi
        enemy.render(display, scroll ) #afficher l'ennemi
        if player_rect.colliderect((enemy.x , enemy.y, ENEMY_WIDTH, ENEMY_HEIGHT)): #si le joueur touche un ennemi
            pv -= 1 #il perd des pv
            pass #il n'en perd pas a l'infini
        if enemy.vie < 0:
            enemy_list.remove(enemy) #fait mourir l'ennemi


    #dictionnaire_vide_ennemi = {}
    #dictionnaire_images_ennemi = self.ennemi.image_liste(self.image_ennemi, dictionnaire_vide_ennemi)
    pygame.draw.rect(display, (255, 255, 0), (100, 150, 100, 100))#dessine soleil
    pygame.draw.rect(display, (255, 0, 0), (jauge_vie))  # dessine un rectangle rouge aux co de la barre de vie
    pygame.draw.rect(display, (0, 255, 0), (jauge_vie[0], jauge_vie[1], pv, jauge_vie[3]))  # dessine rectangle vert

    delta_temps = t2 -t1 #difference entre moment touche pressée et relachée
    if joueur_a_tire: #si la touche de tir est relachée
        if len(projectile_groupe) < tir_autorise and delta_temps > 0.05: #si le nombre de projectiles affichés a l'ecran est inferieur au nombre de tir autorisé et deltatemps superieur a 0.05s
            projectile = Long_range((player_rect[0] -scroll[0], player_rect[1] -scroll[1] +20), [5, 5], direction, shoot_image, 5, 30)#crée un projectile
            projectile_groupe.append(projectile)#ajoute ce projectile au groupe de projectiles
            joueur_a_tire = False #le joueur n'est plus considéré comme ayant tiré
    for projectile in projectile_groupe: #pour chaque projectile dans le groupe de projectiles
        projectile.afficher(display, delta_temps)#afficher le projectile
        projectile.mouvement(10) #donner la vitesse du projectile
        if projectile.rect.right >= 800 or projectile.rect.right <= 0: #si le rect du projectile depasse ceux des bords de l'ecran
            projectile_groupe.remove(projectile)#le projectile disparait du groupe et donc de l'ecran

    for enemy in enemy_list:
        for projectile in projectile_groupe:
            if projectile.rect.colliderect((enemy.x - scroll[0], enemy.y-scroll[1], ENEMY_WIDTH, ENEMY_HEIGHT)):
                enemy.vie -= projectile.degats #fait prendre des degats a l'ennemi s'il touche un projectile
                projectile_groupe.remove(projectile)
                pass

    if grass_sound_timer > 0:
        grass_sound_timer -= 1

    true_scroll[0] += (player_rect.x - true_scroll[0] - 600//2 + 38)/20 # donne le decalage de caméra en x(motié du display pour centrer la caméra - la largeur du player)
    true_scroll[1] += (player_rect.y - true_scroll[1] - 400//2 + 100)/20#decalage de camera en y


    pygame.draw.rect(display, (7, 80, 75), pygame.Rect(0, 240, 600, 160)) #rectangle de background (doubler toutes les valeurs si prises du tuto)
    for background_object in background_objects: #pour chaque objet de background
        obj_rect = pygame.Rect(background_object[1][0] - scroll[0]*background_object[0], background_object[1][1] - scroll[1]*background_object[0], background_object[1][2], background_object[1][3])#creer un rectangle aux co de l'objet
        if background_object[0] == 0.5: #si le coeff est grand
            pygame.draw.rect(display, (14, 222, 150), obj_rect)# mettre l'objet dans une couleur foncée(ou l'inverse jsp)
        else: #sinon
            pygame.draw.rect(display, (9, 91, 85), obj_rect)#mettre une couleur plus claire


    y=0 #numero de ligne
    for row in game_map:#pour chaque ligne
        x=0 #numero de case
        for tile in row:#pour chaque case de la ligne
            if tile =='1': #si la case est 1 afficher de la terre
                display.blit(dirt_image, (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
            if tile == '2': #case2 afficher de l'herbe
                display.blit(grass_image, (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
            if tile == '3':#case3 afficher de la pierre
                display.blit(stone_image, (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
            if tile == '4':#case4 afficher un champi
                jumper_objects.append(jumper_obj((x * TILE_SIZE -1, y * TILE_SIZE -1)))
            if tile == '5':#case5 donner les coordonnées pour les ennemis
                #display.blit(enemy_image, (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
                spawn_enemy = [x * TILE_SIZE, y * TILE_SIZE]  #donne les co de spawn de l'ennemi d'apres la map
                spawn_enemy_list.append(spawn_enemy) #ajoute les co de la case a la liste des spawns d'ennemi
                #enemy_list.append(Enemy(spawn_enemy[0], spawn_enemy[1], (35, 35), enemy_image, 1))
            if tile == '6': #case6 affiche une caisse
                display.blit(caisse_image, (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
                for projectile in projectile_groupe:
                    if projectile.rect.colliderect((x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1], TILE_SIZE, TILE_SIZE)):
                        row[x] = '0'#detruit la caisse

            '''if tile == '6' and collision_test((player_rect[0] -scroll[0] +, player_rect[1] -scroll[1]), (x*TILE_SIZE, y*TILE_SIZE)):
                tile = '0' '''
            if tile == '7':
                display.blit(pics_image, (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1], TILE_SIZE, TILE_SIZE))
                if player_rect.colliderect((x * TILE_SIZE , y * TILE_SIZE , TILE_SIZE, TILE_SIZE)):
                    pv -= 0.1
                    pass
            if tile == '8':
                display.blit(key_image,  (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1], TILE_SIZE, TILE_SIZE))
                if player_rect.colliderect((x * TILE_SIZE , y * TILE_SIZE , TILE_SIZE, TILE_SIZE)):
                    keys += 1
                    row[x] = '0'
                    pass
            if tile =='9':
                display.blit(door_image, (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1], TILE_SIZE, TILE_SIZE))
                if player_rect.colliderect((x * TILE_SIZE -1, y * TILE_SIZE-1, TILE_SIZE +1, TILE_SIZE)) and keys > 0:
                    row[x] = '0'
                    keys -= 1
                    pass
            if tile != '0' and tile !='5' and tile!='7' and tile != '8': #pour toute tuile qui n'est pas de l'air ou un ennemi, ajouter a la liste des solides
                tile_rects.append(pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
                for projectile in projectile_groupe: #si un projectile touche un bloc il disparait
                    if projectile.rect.colliderect((x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1], TILE_SIZE, TILE_SIZE)):
                        projectile_groupe.remove(projectile)
                for enemy in enemy_list: #si un ennemi touche un bloc il fait demi-tour
                        if enemy.rect.colliderect((x * TILE_SIZE , y * TILE_SIZE , TILE_SIZE, TILE_SIZE)):
                            enemy.direction = -enemy.direction


            x+=1#changer de case
        y+=1 #change de ligne



    player_movement = [0,0]# "vitesse" horizontale et verticale
    if moving_right : #si joueur va a droite
        #player_flip = False
        player_movement[0] += 3 #avancer de 2 en x
        direction = 1 #vers la droite
    if moving_left : #si le joueur va a gauche
        #player_flip = True
        player_movement[0] -= 3 #avancer de 2 en x
        direction = -1#vers la gauche

    player_movement[1] = player_y_momentum #altitude = player y momentum
    player_y_momentum += 0.6 #vitesse de chute
    if player_y_momentum > 4: #accélération de chute
        player_y_momentum -=0.6  #l'acceleration stagne a 4

    '''if player_movement[0]>0 and in_air==False and course_d == False and course_g ==False and immobile==False:
        course_d = True
        #il se met a courir (droite)
        #player_flip=False
    else:
        course_d=False
    if player_movement[0]<0 and in_air==False and course_g==False and course_d==False and immobile==False:
        course_g = True
        #(gauche)
        #player_flip=True
    else:
        course_g=False'''
    if player_movement[0]==0 and in_air == False : #si le jouer est immobile et n'est pas en l'air
        #immobile = True
        player_action, player_frame = change_action(player_action, player_frame, 'immobile')#immobile(animations?)
    #else:
    #    immobile=False

    #print(player_action, player_frame, player_flip, in_air)




    player_rect, collisions = move(player_rect, player_movement, tile_rects) #le joueur avance de mouvement[0] en x et [1] en y, si le joueur a une collision, son y va changer

    if collisions['bottom']: #si il a une collision au sol
        player_y_momentum = 0 #il ne va plus descendre
        in_air = False #il n'est plus en l'air
        air_timer=0#timer en l'air = 0s
        if player_movement[0] != 0: #si le joueur avance
            if grass_sound_timer==0:#si le timer de son de pas est a 0 ?
                grass_sound_timer=30#le timer de son de pas devient a 30
                random.choice(grass_sounds).play()#jouer au hasard un des 2 sons de pas
        if player_movement[0] < 0: #si le joueur va a droite
                                # (saut droit)
            player_flip = True#animations tournées vers la droite
        if player_movement[0] > 0:#si le joueur va a gauche
             # (saut gauche)
            player_flip = False#animations tournées vers la gauche

    else: #sinon
        air_timer+=1 #le timer en l'air augmente

    if collisions['top']:#si il y a une collision au plafond
        player_y_momentum = 1#le joueur descend


    player_frame += 1#les animations du joueurs avancent de 1 frame

    for jumper in jumper_objects: #pour chaque champi

        jumper.render(display, scroll)          #cree une surface

        if jumper.collision_test(player_rect) : #si champi touche le joueur
            player_y_momentum = -15 #le joueur saute


    if player_frame>= len(animation_database[player_action]): #boucle d'animation
        player_frame=0 #repart a 0

    player_img_id = animation_database[player_action][player_frame]#l'image a afficher depend de l'action et de la frame ou en est le joueur

    player_image = animation_frames[player_img_id] # donne l'image du joueur actuelle

    display.blit(pygame.transform.flip(player_image, player_flip, False), (player_rect.x - scroll[0], player_rect.y - scroll[1])) #afficher l'image en cours d'animation

    for event in pygame.event.get():#boucle d'evenement d'entrée

        if event.type == QUIT:#verifie si la croix est pressée
            pygame.quit()#quitte pygame
            sys.exit()#ferme le script


        if event.type == KEYDOWN:#si une touche est pressé
            if event.key == K_w:#si c'est w
                pygame.mixer.music.fadeout(1000)#eteindre la musique en 1 seconde(1000ms)
            if event.key == K_x:#si c x
                pygame.mixer.music.play(-1)#allumer la musique a l'infini
            if event.key == K_RIGHT:#si c fleche droite
                player_action, player_frame = change_action(player_action, player_frame, 'course')#action devient courir
                moving_right = True #va vers la droite
            if event.key == K_LEFT:#si c fleche gauche
                player_action, player_frame = change_action(player_action, player_frame, 'course')#action devient courir
                moving_left = True#va vers la gauche
            if event.key == K_UP:#si c fleche haut
                if air_timer < 13 : #peut sauter dans ce laps de temps, utile pour sauter apres une plateforme
                    jump_sound.play()#joue le son de saut
                    in_air=True#est en l'air
                    player_action, player_frame = change_action(player_action, player_frame, 'saut')#action devient saut
                    player_y_momentum= -11 #hauteur de saut
            if event.key == pygame.K_SPACE:#si la touche est espace
                t1 = time.time()#lance timer entre pressée et relachée
            if event.key == pygame.K_DOWN:
                player_y_momentum += 10 #dash vers le bas


        if event.type == KEYUP:#si une touche est relachée
            if event.key == K_RIGHT:#si c fleche droite
                moving_right = False#ne va plus a droite
            if event.key == K_LEFT: #si c fleche gauche
                moving_left = False#ne va plus a gauche
            if event.key == pygame.K_SPACE:#si c espace
                t2 = time.time()#finit le timer
                joueur_a_tire = True#joueur tire

    if fullscreen == False: #si le mode plein ecran n'est pas activé
        surf = pygame.transform.scale(display, WINDOW_SIZE)#mettre la fenetre aux dimensions de la fenetre
    else:#sinon
        surf = pygame.transform.scale(display, ScreenSize[0])#mettre la fenetre aux dimensions de l'ecran

    screen.blit(surf, (0, 0)) #afficher a l'ecran le format modifié
    pygame.display.update()#rafraichit l'ecran
    clock.tick(60)#maintient 60 fps