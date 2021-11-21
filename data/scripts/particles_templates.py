import pygame as pg

class ParticleManager:

    def __init__(self, player):
        self.player = player
        self.particles = []
        self.particle_object = None

    def add_particles(self, *args) -> int:
        if self.particle_object is not None:
            self.particles.append(self.particle_object(*args, self.player.camera))
        return len(self.particles)

    def clear(self) -> None:
        # clear all the particles
        self.particles = []

    def trigger_check(self) -> bool:
        """condition to the particle effect to happen like 'if player moved' """
        return True

    def logic(self) -> bool:
        """if self.trigger_check():
            self.add_particles()"""
        return True

    def update(self, DISPLAY):
        self.logic()
        to_remove = []
        for particle in self.particles:
            update = particle.render(DISPLAY)
            if update == "kill":
                to_remove.append(particle)

        for removing in to_remove:
            self.particles.remove(removing)

class Particle:

    def __init__(self, image, pos, last_time, camera):
        self.image = image
        self.pos = pos
        self.rect = self.image.get_rect(topleft=pos)
        self.begin_time = pg.time.get_ticks()
        self.last_time = last_time
        self.camera = camera

    def behavior(self):

        """
        Basically defines the movements of the particle, if it goes diagonally or just randomly...
        """

        pass

    def logic(self):

        """
        Core part of the particle : you defines when it moves, color changes, size changes, etc
        """

        self.behavior()

    def render(self, screen):
        self.logic()
        screen.blit(self.image, self.rect.topleft-self.camera.offset.xy)
        return "kill" if pg.time.get_ticks() - self.begin_time > self.last_time else None