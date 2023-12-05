import pygame, sys, time
from settings import *
from sprites import Player, Ball, Block, Upgrade, Projectile
from surfaceMaker import SurfaceMaker
from random import choice , randint

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((window_width,window_height))
        pygame.display.set_caption('Breakout')

        #background
        self.bg = self.create_bg()

        #sprites group setup
        self.all_sprites = pygame.sprite.Group()
        self.block_sprites = pygame.sprite.Group()
        self.upgrade_sprites = pygame.sprite.Group()
        self.projectile_sprites = pygame.sprite.Group()

        #setup
        self.surfacemaker = SurfaceMaker()
        self.player = Player(self.all_sprites, self.surfacemaker)
        self.stage_setup()
        self.ball = Ball(self.all_sprites, self.player, self.block_sprites)

        #hearts
        self.heart_surf = pygame.image.load('graphics/other/heart.png').convert_alpha()

        #projectile
        self.projectile_surf =pygame.image.load('graphics/other/projectile.png').convert_alpha()
        self.can_shoot = True
        self.shoot_time = 0

        #CRT
        self.crt = CRT()

        #sounds
        self.laser_hit_sound = pygame.mixer.Sound('sounds/laser_hit.wav')
        self.laser_hit_sound.set_volume(0.1)
        self.laser_sound = pygame.mixer.Sound('sounds/laser.wav')
        self.laser_sound.set_volume(0.1)
        self.power_up_sound = pygame.mixer.Sound('sounds/powerup.wav')
        self.power_up_sound.set_volume(0.1)
        self.music = pygame.mixer.Sound('sounds/music.wav')
        self.music.set_volume(0.08)
        self.music.play(loops = -1)

    def laser_timer(self):
        if pygame.time.get_ticks() - self.shoot_time > 750:
            self.can_shoot = True

    def create_upgrade(self, position):
        upgrade_type = choice(upgrades)
        Upgrade(position, upgrade_type, [self.all_sprites,self.upgrade_sprites])

    def create_bg(self):
        bg_original = pygame.image.load('graphics/other/bg.png').convert()
        scale_factor = window_height/bg_original.get_height()
        scaled_width = bg_original.get_width() * scale_factor
        scaled_height = bg_original.get_height() * scale_factor
        scaled_bg = pygame.transform.scale(bg_original, (scaled_width, scaled_height))
        return scaled_bg
    
    def stage_setup(self):
        #cycle through all rows and columns of block map
        for row_index, row in enumerate(block_map):
            for col_index, col in enumerate(row):
                if col != ' ':
                    #find x and y position for each block
                    y = top_offest + row_index * (block_height + gap_size) + gap_size // 2
                    x = col_index * (block_width + gap_size) + gap_size // 2
                    Block(col, (x,y), [self.all_sprites, self.block_sprites], self.surfacemaker, self.create_upgrade)

    def display_hearts(self):
        for i in range(self.player.hearts):
            x =  3 + i * (self.heart_surf.get_width() + 3)
            self.display_surface.blit(self.heart_surf, (x, 4))

    def upgrade_collision(self):
        overlap_sprites = pygame.sprite.spritecollide(self.player, self.upgrade_sprites, True)
        for sprite in overlap_sprites:
            self.player.upgrade(sprite.upgrade_type)
            self.power_up_sound.play()

    def create_projectile(self):
        self.laser_sound.play()
        for projectile in self.player.laser_rects:
            Projectile(projectile.midtop - pygame.math.Vector2(0,30), self.projectile_surf, [self.all_sprites, self.projectile_sprites])

    def projectile_block_collision(self):
        for projectile in self.projectile_sprites:
            overlap_sprites = pygame.sprite.spritecollide(projectile, self.block_sprites, False)
            if overlap_sprites:
                for sprite in overlap_sprites:
                    sprite.get_damage(1)
                    self.laser_hit_sound.play()
                projectile.kill()

    def run(self):
        last_time = time.time()
        while True:

            #delta time
            dt = time.time() - last_time
            last_time = time.time()

            #event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT or self.player.hearts <= 0:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.ball.active = True
                        if self.can_shoot:
                            self.create_projectile()
                            self.can_shoot = False
                            self.shoot_time = pygame.time.get_ticks()
            
            #draw background
            self.display_surface.blit(self.bg, (0, 0))

            #update game
            self.all_sprites.update(dt)
            self.upgrade_collision()
            self.laser_timer()
            self.projectile_block_collision()
            
            #draw
            self.all_sprites.draw(self.display_surface)
            self.display_hearts()

            #crt styling
            self.crt.draw()

            #update window
            pygame.display.update()

class CRT:
    def __init__(self):
        vignette = pygame.image.load('graphics/other/tv.png').convert_alpha()
        self.scaled_vignette = pygame.transform.scale(vignette, (window_width, window_height))
        self.display_surface = pygame.display.get_surface()
        self.create_crt_lines()

    def create_crt_lines(self):
        line_height = 4
        line_amount = window_height // line_height
        for line in range(line_amount):
            y = line *line_height
            pygame.draw.line(self.scaled_vignette, ('black'), (0,y), (window_width,y), 1)

    def draw(self):
        self.scaled_vignette.set_alpha(randint(75,90))
        self.display_surface.blit(self.scaled_vignette, (0,0))
        
if __name__ == '__main__':
    game = Game()
    game.run()