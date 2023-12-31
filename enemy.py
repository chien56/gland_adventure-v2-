import pygame

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, taille, image, direction):
        super().__init__()
        self.x = x
        self.y = y
        self.taille = taille
        self.rect = pygame.Rect(self.x, self.y, self.taille[0], self.taille[1])
        self.saut = 0
        self.direction = direction
        self.etat = 'vivant'
        self.index = 0
        self.ennemi_vivant = [pygame.Rect(156, 104, 77, 84), pygame.Rect(404, 108, 78, 77)]
        self.ennemi_mort = [pygame.Rect(158, 397, 81, 85), pygame.Rect(386, 390, 78, 95), pygame.Rect(625, 387, 77, 101),
                            pygame.Rect(846, 400, 67, 90), pygame.Rect(1063, 414, 64, 77), pygame.Rect(1272, 420, 67, 76),
                            pygame.Rect(1497, 419, 65, 66), pygame.Rect(159, 650, 67, 77), pygame.Rect(388, 654, 70, 70),
                            pygame.Rect(1500, 800, 0, 1)]
        self.vie = 35
        self.degats_recus = 0
        self.droite = True
        self.gauche = False
        self.attaque = 10
        self.enemy_image = image
        self.movement = [0, 0]
        self.collision = {}

    def render(self, surf, scroll):  # affiche
        surf.blit(self.enemy_image, (self.x - scroll[0], self.y- scroll[1]))

    def afficher(self, surface, dict):

        self.index += 1
        if self.index >= len(dict[self.etat]):
            self.index = 0
            if self.etat == 'mort':
                self.index = 9
        if self.etat == 'vivant':
            pygame.draw.rect(surface, (255, 0, 0), (self.rect.x + 13, self.rect.y - 20, 50, 10))
            pygame.draw.rect(surface, (0, 0, 255), (self.rect.x + 13, self.rect.y - 20, self.vie*1.45, 10))

        image = dict[self.etat][self.index]
        if self.direction == -1:
            image = pygame.transform.flip(image, True, False)

        surface.blit(image, self.rect)

    def image_liste(self, image, dict):

        for image_vivant in self.ennemi_vivant:
            ennemi_rectangle_supprime = self.ennemi_vivant.pop(0)
            image_ennemi = image.subsurface(ennemi_rectangle_supprime)
            image_ennemi = pygame.transform.scale(image_ennemi, (78, 84))
            self.ennemi_vivant.append(image_ennemi)

        dict['vivant'] = self.ennemi_vivant

        for image_mort in self.ennemi_mort:
            image_rect = self.ennemi_mort.pop(0)
            image_ennemi = image.subsurface(image_rect)
            image_ennemi = pygame.transform.scale(image_ennemi, (78, 84))
            self.ennemi_mort.append(image_ennemi)

        dict['mort'] = self.ennemi_mort

        return dict

    def move(self, speed):
        self.x += speed * self.direction
        self.y += 0.2
