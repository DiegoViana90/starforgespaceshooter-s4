from entities.explosion import Explosion
from systems.spawn_manager import maybe_spawn_health_pickup, maybe_spawn_weapon_pickup


def handle_collisions(game):
    handle_player_bullet_hits(game)
    handle_enemy_bullet_hits(game)
    handle_bomb_hits(game)
    handle_enemy_contact(game)
    handle_boss_contact(game)
    handle_pickup_hits(game)
    handle_weapon_pickup_hits(game)


def handle_player_bullet_hits(game):
    for bullet in game.player_bullets[:]:
        if bullet not in game.player_bullets:
            continue

        hit_something = False
        is_laser = getattr(bullet, "kind", "") == "laser_beam"
        damage = getattr(bullet, "damage", 1)

        for enemy in game.enemies[:]:
            if bullet.rect().colliderect(enemy.rect()):
                enemy.hp -= damage
                hit_something = True

                if not is_laser and bullet in game.player_bullets:
                    game.player_bullets.remove(bullet)

                if enemy.hp <= 0:
                    game.explosions.append(
                        Explosion(enemy.x + enemy.w // 2, enemy.y + enemy.h // 2, 1.0)
                    )
                    game.sound.play("explosion")
                    maybe_spawn_health_pickup(game, enemy)
                    maybe_spawn_weapon_pickup(game, enemy)

                    if enemy in game.enemies:
                        game.enemies.remove(enemy)

                    game.score += 100
                    game.kills += 1

                if not is_laser:
                    break

        if hit_something and not is_laser:
            continue

        if game.boss is not None and bullet.rect().colliderect(game.boss.rect()):
            game.boss.hp -= damage

            if not is_laser and bullet in game.player_bullets:
                game.player_bullets.remove(bullet)

            game.explosions.append(Explosion(bullet.x, bullet.y, 0.5))

            if game.boss.hp <= 0:
                game.sound.play("explosion")
                game.explosions.append(
                    Explosion(game.boss.x + game.boss.w // 2, game.boss.y + game.boss.h // 2, 2.8)
                )
                game.score += 3000
                game.boss = None

                if game.phase == 1:
                    game.start_next_phase()
                else:
                    game.phase_clear = True


def handle_enemy_bullet_hits(game):
    for bullet in game.enemy_bullets[:]:
        if bullet.rect().colliderect(game.player.rect()):
            game.explosions.append(
                Explosion(game.player.x + game.player.w // 2, game.player.y + game.player.h // 2, 0.8)
            )
            game.enemy_bullets.remove(bullet)
            game.sound.play("hit")

            damage = 6 if game.difficulty == "easy" else 8 if game.difficulty == "medium" else 11
            game.player.hp -= damage
            if game.player.hp <= 0:
                game.game_over = True


def handle_bomb_hits(game):
    for bomb in game.bombs[:]:
        if bomb.rect().colliderect(game.player.rect()):
            game.explosions.append(Explosion(bomb.x, bomb.y, 1.3))
            game.explosions.append(
                Explosion(game.player.x + game.player.w // 2, game.player.y + game.player.h // 2, 1.0)
            )
            game.bombs.remove(bomb)
            game.sound.play("hit")

            damage = 14 if game.difficulty == "easy" else 18 if game.difficulty == "medium" else 24
            game.player.hp -= damage
            if game.player.hp <= 0:
                game.game_over = True


def handle_enemy_contact(game):
    for enemy in game.enemies[:]:
        if enemy.rect().colliderect(game.player.rect()):
            game.explosions.append(Explosion(enemy.x + enemy.w // 2, enemy.y + enemy.h // 2, 1.0))
            game.explosions.append(
                Explosion(game.player.x + game.player.w // 2, game.player.y + game.player.h // 2, 1.0)
            )
            if enemy in game.enemies:
                game.enemies.remove(enemy)
            game.sound.play("hit")

            damage = 10 if game.difficulty == "easy" else 12 if game.difficulty == "medium" else 16
            game.player.hp -= damage
            if game.player.hp <= 0:
                game.game_over = True


def handle_boss_contact(game):
    if game.boss is not None and game.boss.rect().colliderect(game.player.rect()):
        game.explosions.append(
            Explosion(game.player.x + game.player.w // 2, game.player.y + game.player.h // 2, 1.4)
        )
        game.sound.play("hit")

        damage = 24 if game.difficulty == "easy" else 30 if game.difficulty == "medium" else 38
        game.player.hp -= damage
        if game.player.hp <= 0:
            game.game_over = True


def handle_pickup_hits(game):
    for pickup in game.pickups[:]:
        if pickup.rect().colliderect(game.player.rect()):
            heal = 26 if game.difficulty == "easy" else 20 if game.difficulty == "medium" else 16
            game.player.hp = min(100, game.player.hp + heal)
            game.pickups.remove(pickup)
            game.sound.play("pickup")


def handle_weapon_pickup_hits(game):
    for pickup in game.weapon_pickups[:]:
        if pickup.rect().colliderect(game.player.rect()):
            if pickup.weapon_type == "laser":
                amount = 52 if game.difficulty == "easy" else 42 if game.difficulty == "medium" else 32
            elif pickup.weapon_type == "spread":
                amount = 28 if game.difficulty == "easy" else 20 if game.difficulty == "medium" else 14
            else:
                amount = 30 if game.difficulty == "easy" else 22 if game.difficulty == "medium" else 16

            game.player.give_special_ammo(pickup.weapon_type, amount)
            game.weapon_pickups.remove(pickup)
            game.sound.play("pickup")
