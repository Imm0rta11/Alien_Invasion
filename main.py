import sys
import pygame
from time import sleep
from settings import Settings
from star_ship import StarShip
from bullet import Bullet
from alien import Alien
from game_stats import GameStats
from button import Button
from score_board import Scoreboard


class AlienInvation:
    def __init__(self):
        pygame.init()
        self.settings = Settings()
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        self.screen_rect = self.screen.get_rect()
        pygame.display.set_caption('Alien Invasion')
        pygame.time.Clock().tick(60)

        self.star_ship = StarShip(self)
        self.game_stat = GameStats(self)
        self.score_board = Scoreboard(self)
        self.play_button = Button(self, 'Play', self.screen_rect.center)
        self.help_button = Button(self, 'Help', (self.screen_rect.centerx, self.screen_rect.centery + 60))
        self.quit_button = Button(self, 'Quit', (self.screen_rect.centerx, self.screen_rect.centery + 120))
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

    def run_game(self):
        while True:
            self._check_events()
            if self.game_stat.game_active:
                self.star_ship.update()
                self._update_aliens()
                self._update_bullets()
            self._update_screen()

    def _check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                with open('save.py', 'w') as file:
                    file.write(f'HighScore = {self.game_stat.high_score}')
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_event(event)
            elif event.type == pygame.KEYUP and self.game_stat.game_active:
                self._check_keyup_event(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
                self._check_quit_button(mouse_pos)

    def _check_keydown_event(self, event):
        if event.key == pygame.K_RIGHT and self.game_stat.game_active:
            self.star_ship.moving_right = True
        if event.key == pygame.K_LEFT and self.game_stat.game_active:
            self.star_ship.moving_left = True
        if event.key == pygame.K_SPACE and self.game_stat.game_active:
            self._fire_bullet()
        if event.key == pygame.K_q:
            with open('save.py', 'w') as file:
                file.write(f'HighScore = {self.game_stat.high_score}')
            sys.exit()

    def _check_keyup_event(self, event):
        if event.key == pygame.K_RIGHT:
            self.star_ship.moving_right = False
        if event.key == pygame.K_LEFT:
            self.star_ship.moving_left = False

    def _check_play_button(self, mouse_pos):
        if self.play_button.rect.collidepoint(mouse_pos):
            button_clicked = self.play_button.rect.collidepoint(mouse_pos)
            if button_clicked and not self.game_stat.game_active:
                pygame.mouse.set_visible(False)
                self.settings.initialize_dynamic_settings()
                self.game_stat.reset_stats()
                self.score_board.prep_score()
                self.score_board.prep_high_score()
                self.score_board.prep_level()
                self.game_stat.game_active = True

                self.aliens.empty()
                self.bullets.empty()

                self._create_fleet()
                self.star_ship.center_ship()

    def _check_help_button(self, mouse_pos):
        pass

    def _check_quit_button(self, mouse_pos):
        if self.quit_button.rect.collidepoint(mouse_pos):
            button_clicked = self.quit_button.rect.collidepoint(mouse_pos)
            if button_clicked and not self.game_stat.game_active:
                sys.exit()

    def _fire_bullet(self):
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        self.bullets.update()
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        self._check_bullet_alien_colision()

    def _update_aliens(self):
        self._check_fleet_edges()
        self.aliens.update()
        self._check_aliens_bottom()
        if pygame.sprite.spritecollideany(self.star_ship, self.aliens):
            self._ship_hit()

    def _check_aliens_bottom(self):
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                self._ship_hit()
                break

    def _ship_hit(self):
        if self.game_stat.ships_left > 0:
            self.game_stat.ships_left -= 1
            self.score_board.prep_star_ships()

            self.aliens.empty()
            self.bullets.empty()

            self._create_fleet()
            self.star_ship.center_ship()

            sleep(0.5)
        else:
            self.game_stat.ships_left = 3
            self.score_board.prep_star_ships()
            pygame.mouse.set_visible(True)
            self.game_stat.game_active = False

    def _check_bullet_alien_colision(self):
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        if not self.aliens:
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()
            self.game_stat.level += 1
            self.score_board.prep_level()
        if collisions:
            for aliens in collisions.values():
                self.game_stat.score += self.settings.alien_point * len(aliens)
                self.score_board.check_high_score()

        self.score_board.prep_score()

    def _create_fleet(self):
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        avalable_space_x = self.settings.screen_width - (2 * alien_width)
        number_alien_x = avalable_space_x // (2 * alien_width)

        ship_height = self.star_ship.rect.height
        avalable_space_y = (self.settings.screen_height - (3 * alien_height) - ship_height)
        number_rows = avalable_space_y // (2 * alien_height)

        for rows_numbers in range(number_rows):
            for aliens in range(number_alien_x):
                self._create_alien(aliens, rows_numbers)

    def _create_alien(self, alien_number, row_number):
        alien = Alien(self)
        alien_width = alien.rect.width
        alien_height = alien.rect.height
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.y = alien.rect.height + 2 * alien_height * row_number
        alien.rect.x = alien.x
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _draw_game_title(self):
        self.font = pygame.font.SysFont(None, 64)
        self.game_title = self.font.render('Alien Invasion', True, (0, 0, 0))
        self.game_title_rect = self.game_title.get_rect()
        self.game_title_rect.center = (self.screen_rect.centerx, self.screen_rect.centery - 120)
        self.screen.blit(self.game_title, self.game_title_rect)

    def _update_screen(self):
        self.screen.fill(self.settings.bg_color)
        self.score_board.show_score()
        self.star_ship.blit_ship()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)
        if not self.game_stat.game_active:
            self._draw_game_title()
            self.play_button.draw_button()
            self.help_button.draw_button()
            self.quit_button.draw_button()
        pygame.display.flip()


if __name__ == '__main__':
    ai = AlienInvation()
    ai.run_game()
