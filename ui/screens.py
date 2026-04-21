import pygame
from settings import CYAN, WHITE
from ui.layout import Layout


def draw_menu(game):
    sw, sh = game.screen.get_size()
    layout = Layout(sw, sh)

    title_font = layout.font(56, bold=True)
    game_font = layout.font(44)
    sub_font = layout.font(24)

    title1 = title_font.render("STARFORGE", True, CYAN)
    title2 = game_font.render("SPACE SHOOTER S4", True, WHITE)
    subtitle = sub_font.render("Retro arcade shooter", True, (180, 180, 200))

    game.screen.blit(title1, title1.get_rect(center=(sw // 2, int(sh * 0.22))))
    game.screen.blit(title2, title2.get_rect(center=(sw // 2, int(sh * 0.31))))
    game.screen.blit(subtitle, subtitle.get_rect(center=(sw // 2, int(sh * 0.39))))

    font = layout.font(24)
    buttons = game.menu_buttons()

    for rect in buttons.values():
        pygame.draw.rect(game.screen, (45, 45, 70), rect, border_radius=12)
        pygame.draw.rect(game.screen, WHITE, rect, 2, border_radius=12)

    for text, key in [("START GAME", "start"), ("OPTIONS", "options"), ("EXIT", "exit")]:
        label = font.render(text, True, WHITE)
        game.screen.blit(label, label.get_rect(center=buttons[key].center))


def draw_options(game):
    sw, sh = game.screen.get_size()
    layout = Layout(sw, sh)

    title_font = layout.font(48, bold=True)
    font = layout.font(24)

    title = title_font.render("OPTIONS", True, CYAN)
    game.screen.blit(title, title.get_rect(center=(sw // 2, int(sh * 0.20))))

    buttons = game.options_buttons()

    for rect in buttons.values():
        pygame.draw.rect(game.screen, (45, 45, 70), rect, border_radius=12)
        pygame.draw.rect(game.screen, WHITE, rect, 2, border_radius=12)

    sound_label = "SOUND: ON" if game.sound.enabled else "SOUND: OFF"
    touch_label = "TOUCH CONTROLS: ON" if game.mobile_controls_enabled else "TOUCH CONTROLS: OFF"
    difficulty_label = f"DIFFICULTY: {game.difficulty.upper()}"

    items = [
        (sound_label, "sound"),
        (touch_label, "touch"),
        (difficulty_label, "difficulty"),
        ("BACK", "back"),
    ]

    for text, key in items:
        label = font.render(text, True, WHITE)
        game.screen.blit(label, label.get_rect(center=buttons[key].center))
