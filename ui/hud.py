import pygame
from settings import GREEN, RED, WHITE, CYAN, BIG_FONT
from ui.layout import Layout


def draw_hud(game):
    sw, sh = game.screen.get_size()
    layout = Layout(sw, sh)
    rects = layout.hud_rects()

    hp_rect = rects["hp"]
    score_x, score_y = rects["score_pos"]
    stage_x, stage_y = rects["stage_pos"]
    boss_rect = rects["boss_bar"]
    weapon_rect = rects["weapon_bar"]

    font = layout.font(24)
    big_font = layout.font(48, bold=True)

    pygame.draw.rect(game.screen, (60, 60, 60), hp_rect, border_radius=8)
    hp_fill = pygame.Rect(hp_rect.x, hp_rect.y, max(0, int(hp_rect.w * (game.player.hp / 100))), hp_rect.h)
    pygame.draw.rect(game.screen, GREEN if game.player.hp > 30 else RED, hp_fill, border_radius=8)
    pygame.draw.rect(game.screen, WHITE, hp_rect, 2, border_radius=8)

    game.draw_text(f"Score: {game.score}", font, WHITE, score_x, score_y)

    if game.boss is None and not game.boss_spawned:
        game.draw_text("Fase 1", font, CYAN, stage_x, stage_y)
    elif game.boss is not None:
        game.draw_text("CHEFÃO", font, RED, boss_rect.x, boss_rect.y - int(28 * layout.scale))

        pygame.draw.rect(game.screen, (60, 60, 60), boss_rect, border_radius=8)
        current_boss_bar = int((game.boss.hp / game.boss.max_hp) * boss_rect.w)
        pygame.draw.rect(game.screen, RED, (boss_rect.x, boss_rect.y, current_boss_bar, boss_rect.h), border_radius=8)
        pygame.draw.rect(game.screen, WHITE, boss_rect, 2, border_radius=8)

    pygame.draw.rect(game.screen, (55, 55, 55), weapon_rect, border_radius=6)
    weapon_text = ""

    if game.player.special_ammo > 0:
        ratio = game.player.special_ammo / game.player.max_special_ammo
        fill_w = int(weapon_rect.w * ratio)
        pygame.draw.rect(game.screen, (255, 220, 70), (weapon_rect.x, weapon_rect.y, fill_w, weapon_rect.h), border_radius=6)
        weapon_text = "TIRO TRIPLO"

    elif game.player.overheated:
        ratio = max(0.0, min(1.0, game.player.weapon_heat / game.player.max_heat))
        fill_w = int(weapon_rect.w * ratio)
        if fill_w > 0:
            pygame.draw.rect(game.screen, (220, 70, 70), (weapon_rect.x, weapon_rect.y, fill_w, weapon_rect.h), border_radius=6)
        weapon_text = "AGUARDE..."

    else:
        ratio = game.player.weapon_heat / game.player.max_heat
        fill_w = int(weapon_rect.w * ratio)
        bar_color = (180 + int(75 * ratio), max(50, 220 - int(140 * ratio)), 60)
        if fill_w > 0:
            pygame.draw.rect(game.screen, bar_color, (weapon_rect.x, weapon_rect.y, fill_w, weapon_rect.h), border_radius=6)
        weapon_text = "ARMA NORMAL"

    pygame.draw.rect(game.screen, WHITE, weapon_rect, 2, border_radius=6)

    text_surface = font.render(weapon_text, True, WHITE)
    text_rect = text_surface.get_rect(center=weapon_rect.center)
    game.screen.blit(text_surface, text_rect)

    if game.game_over:
        text = big_font.render("GAME OVER", True, RED)
        game.screen.blit(text, text.get_rect(center=(sw // 2, sh // 2 - int(40 * layout.scale))))
        sub = font.render("Pressione R para reiniciar", True, WHITE)
        game.screen.blit(sub, sub.get_rect(center=(sw // 2, sh // 2 + int(20 * layout.scale))))

    if game.phase_clear:
        text = big_font.render("FASE 1 COMPLETA!", True, GREEN)
        game.screen.blit(text, text.get_rect(center=(sw // 2, sh // 2 - int(50 * layout.scale))))
        sub = font.render("Pressione R para jogar de novo", True, WHITE)
        game.screen.blit(sub, sub.get_rect(center=(sw // 2, sh // 2 + int(20 * layout.scale))))
