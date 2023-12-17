import pygame
from settings import *
from random import choice, randint

class Player(pygame.sprite.Sprite):
    def __init__(self, groups, surfacemaker):
        super().__init__(groups)

        self.display_surface = pygame.display.get_surface()
        self.surfacemaker = surfacemaker
        self.image = surfacemaker.get_surf('player',(window_width // 10, window_height//20))

        #position
        self.rect = self.image.get_rect(midbottom = (window_width // 2, window_height - 20))
        #create old rect
        self.old_rect = self.rect.copy()
        self.direction = pygame.math.Vector2()
        self.position = pygame.math.Vector2(self.rect.topleft)
        self.speed = 300

        #hearts
        self.hearts = 3

        #lasers
        self.laser_amount = 0
        self.laser_surf = pygame.image.load('Breakout/graphics/other/laser.png').convert_alpha()
        self.laser_rects = []

    def input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
        else:
            self.direction.x = 0
    
    def screen_constraint(self):
        if self.rect.right > window_width :
            self.rect.right = window_width
            self.position.x = self.rect.x
        elif self.rect.left < 0:
            self.rect.left = 0
            self.position.x = self.rect.x

    def upgrade(self, upgrade_type):
        if upgrade_type == 'speed':
            self.speed += 50

        if upgrade_type == 'heart':
            self.hearts += 1

        if upgrade_type == 'size':
            new_width = self.rect.width * 1.1
            self.image = self.surfacemaker.get_surf('player', (new_width, self.rect.height))
            self.rect = self.image.get_rect(center = self.rect.center)
            self.position.x = self.rect.x
        
        if upgrade_type == 'laser':
            self.laser_amount += 1

    def display_lasers(self):
        self.laser_rects = []
        if self.laser_amount > 0:
            divider_length = self.rect.width / (self.laser_amount + 1)
            for i in range(self.laser_amount):
                x = self.rect.left + divider_length * (i + 1)
                laser_rect = self.laser_surf.get_rect(midbottom = (x, self.rect.top))
                self.laser_rects.append(laser_rect)

            for laser_rect in self.laser_rects:
                self.display_surface.blit(self.laser_surf, laser_rect)

    def update(self,dt):
        self.old_rect = self.rect.copy
        self.input()
        self.screen_constraint()
        self.position.x += self.direction.x * self.speed * dt
        self.rect.x = round (self.position.x)
        self.display_lasers()

class Ball(pygame.sprite.Sprite):
    def __init__(self, groups, player, blocks):
        super().__init__(groups)

        #collision
        self.player = player
        self.blocks = blocks

        #graphics
        self.image = pygame.image.load('Breakout/graphics/other/ball.png').convert_alpha()

        #position
        self.rect = self.image.get_rect(midbottom = player.rect.midtop)
        #create old rect 
        self.old_rect = self.rect.copy()
        self.position = pygame.math.Vector2(self.rect.topleft)
        self.direction = pygame.math.Vector2((choice((1,-1)), -1))
        self.speed = 400

        #active
        self.active = False

        #sounds
        self.impact_sound = pygame.mixer.Sound('Breakout/sounds/impact.wav')
        self.impact_sound.set_volume(0.1)

        self.fail_sound = pygame.mixer.Sound('Breakout/sounds/fail.wav')
        self.fail_sound.set_volume(0.1)

    def window_collision(self, direction):
        if direction == 'horizontal':
            if self.rect.left < 0:
                self.rect.left = 0
                self.position.x = self.rect.x
                self.direction.x *= -1
            
            if self.rect.right > window_width:
                self.rect.right = window_width
                self.position.x = self.rect.x
                self.direction.x *= -1

        if direction == 'vertical':
            if self.rect.top < 0:
                self.rect.top = 0
                self.position.y = self.rect.y
                self.direction.y *= -1

            if self.rect.bottom > window_height:
                self.active = False
                self.direction.y = -1
                self.player.hearts -= 1
                self.fail_sound.play()

    def collision(self, direction):
        #find overlapping objects
        overlap_sprites = pygame.sprite.spritecollide(self, self.blocks, False)
        if self.rect.colliderect(self.player.rect):
            overlap_sprites.append(self.player)
        
        if overlap_sprites:
            if direction == 'horizontal':
                for sprite in overlap_sprites:
                    if self.rect.right >= sprite.rect.left and self.old_rect.right <= sprite.rect.left:
                        self.rect.right = sprite.rect.left - 1
                        self.position.x = self.rect.x
                        self.direction.x *= -1
                        self.impact_sound.play()

                    if self.rect.left <= sprite.rect.right and self.old_rect.left >= sprite.rect.right:
                        self.rect.left = sprite.rect.right + 1
                        self.position.x = self.rect.x
                        self.direction.x *= -1
                        self.impact_sound.play()

                    if getattr(sprite, 'health', None):
                        sprite.get_damage(1)

            if direction == 'vertical':
                for sprite in overlap_sprites:
                    if self.rect.bottom >= sprite.rect.top and self.old_rect.bottom <= sprite.rect.top:
                        self.rect.bottom = sprite.rect.top - 1
                        self.position.y = self.rect.y
                        self.direction.y *= -1
                        self.impact_sound.play()
                        
                    if self.rect.top <= sprite.rect.bottom and self.old_rect.top >= sprite.rect.bottom:
                        self.rect.top = sprite.rect.bottom + 1
                        self.position.y = self.rect.y
                        self.direction.y *= -1
                        self.impact_sound.play()
                    
                    if getattr(sprite, 'health', None):
                        sprite.get_damage(1)

    def update(self,dt):
        if self.active:

            if self.direction.magnitude() != 0:
                self.direction = self.direction.normalize()
            
            #create old rect
            self.old_rect = self.rect.copy()

            #horizontal movement + collision
            self.position.x += self.direction.x * self.speed * dt
            self.rect.x = round(self.position.x)
            self.collision('horizontal')
            self.window_collision('horizontal')

            #vertical movement + collision
            self.position.y += self.direction.y * self.speed * dt
            self.rect.y = round(self.position.y)
            self.collision('vertical')
            self.window_collision('vertical')
        else:
            self.rect.midbottom = self.player.rect.midtop
            self.position = pygame.math.Vector2(self.rect.topleft)

class Block(pygame.sprite.Sprite):
    def __init__(self, block_type, position, groups, surfacemaker, create_upgrade):
        super().__init__(groups)
        self.surfacemaker = surfacemaker
        self.image = self.surfacemaker.get_surf(color_legend[block_type],(block_width, block_height))
        self.rect = self.image.get_rect(topleft = position)

        #damage
        self.health = int(block_type)

        #upgrade
        self.create_upgrade = create_upgrade

    def get_damage(self, amount):
        self.health -= amount

        if self.health > 0:
            #update image
            self.image = self.surfacemaker.get_surf(color_legend[str(self.health)],(block_width,block_height))
        else:
            if randint (0,10) < 3:
                self.create_upgrade(self.rect.center)
            self.kill()

class Upgrade(pygame.sprite.Sprite):
    def __init__(self, position, upgrade_type, groups):
        super().__init__(groups)
        self.upgrade_type = upgrade_type
        self.image = pygame.image.load(f'Breakout/graphics/upgrades/{upgrade_type}.png').convert_alpha()
        self.rect = self.image.get_rect(midtop = position)

        self.position = pygame.math.Vector2(self.rect.topleft)
        self.speed = 300

    def update(self, dt):
        self.position.y += self.speed * dt
        self.rect.y = round(self.position.y)

        if self.rect.top > window_height + 100:
            self.kill()

class Projectile(pygame.sprite.Sprite):
    def __init__(self, position, surface, groups):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_rect(midbottom = position)

        self.position = pygame.math.Vector2(self.rect.topleft)
        self.speed = 300

    def update(self, dt):
        self.position.y -= self.speed * dt
        self.rect.y = round(self.position.y)

        if self.rect.bottom <= -100:
            self.kill()
            