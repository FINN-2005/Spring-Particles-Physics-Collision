from classes import *


class run(APP):
    def setup(self):
        self.particles = Group()
        self.springs = Group()
        self.collidables = Group()

        self.draw_layer = Group()

        self.apply_gravity = True

        Shape.get_jelly_quad(self.particles, self.springs, self.draw_layer)
        # Shape.get_jelly_circle(self.particles, self.springs, self.draw_layer)
        
    
        # ===== Collidales =====
        things = [
            [V2(APP.HW, 10), V2(APP.W, 20)],
            [V2(APP.HW, APP.H - 10), V2(APP.W, 20)],
            [V2(10, APP.HH), V2(20, APP.H)],
            [V2(APP.W - 10, APP.HH), V2(20, APP.H)]
        ]
        for pos, size in things:
            Rect(pos, size, self.collidables, self.draw_layer)
        self.platform = Rect(V2(APP.HW, APP.H - 100), V2(300,200), self.collidables, self.draw_layer)


    def update(self):
        move_direction = get_2d_input_dir()
        self.platform.move(move_direction, self.dt, 5)

        if self.apply_gravity:
            self.particles.apply_force()        # defualt is gravity

        self.springs.update(self.dt)
        self.particles.update(self.dt)
        self.particles.collition_check_and_resolve(self.collidables)

    def draw(self):
        # self.draw_layer.draw()
        self.springs.draw()
        self.particles.draw()
        self.collidables.draw()

    def event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_SPACE:
                self.apply_gravity = not self.apply_gravity

run()