import pygame


class SoundManager:
    def __init__(self):
        self.enabled = False
        self.sounds = {}

        try:
            pygame.mixer.init()
            self.sounds["shoot"] = pygame.mixer.Sound("assets/sounds/shoot.wav")
            self.sounds["explosion"] = pygame.mixer.Sound("assets/sounds/explosion.wav")
            self.sounds["pickup"] = pygame.mixer.Sound("assets/sounds/pickup.wav")
            self.sounds["hit"] = pygame.mixer.Sound("assets/sounds/hit.wav")

            self.sounds["shoot"].set_volume(0.25)
            self.sounds["explosion"].set_volume(0.35)
            self.sounds["pickup"].set_volume(0.35)
            self.sounds["hit"].set_volume(0.35)

            self.enabled = True
        except Exception as e:
            print(f"[Som desativado] {e}")

    def play(self, name):
        if not self.enabled:
            return

        sound = self.sounds.get(name)
        if sound:
            sound.play()