from collisions import *

class Particle(Circle):
    def __init__(self, pos:V2, radius = 10, fixed = False, *groups):
        super().__init__(radius, pos, *groups)

        self.pos = pos
        self.fixed = fixed
        self.radius = radius
        self.velocity = V2()
        self.force = V2()

    def draw(self, screen):
        pygame.draw.circle(screen, Color.gray60, self.pos, self.radius)
        pygame.draw.circle(screen, Color.black, self.pos, self.radius, 2)
    
    def update(self, dt):
        if not self.fixed:
            self.velocity += self.force * dt
            self.velocity *= 0.998
            self.pos += self.velocity * dt
        self.force = V2()

    def apply_force(self, force=V2(0,0.1)):
        self.force += force

    def ground_pound(self, level: int | float):
        if self.pos.y + self.radius >= level:
            self.pos.y = level - self.radius
            self.velocity.y = 0

    def collition_check_and_resolve(self, collidables:Group):
        for rect in collidables:
            if self.check_collision_rect(rect):
                self.resolve_collision_rect(rect)
                self.velocity = V2()



class Spring(Sprite):
    def __init__(self, a: Particle, b: Particle, k = 1, damping = 0.01, *groups):
        super().__init__(*groups)

        self.a = a
        self.b = b
        self.k = k
        self.damping = damping
        self.rest_len = (a.pos - b.pos).length()

    def update(self, dt):
        delta = self.a.pos - self.b.pos
        dist = delta.length()
        if dist == 0: return
        direction = delta.normalize()
        displacement = dist - self.rest_len
        force = -self.k * displacement * direction
        relative_velocity = self.a.velocity - self.b.velocity
        damping_force = self.damping * relative_velocity.dot(direction) * direction
        force -= damping_force
        if not self.a.fixed: self.a.force += force
        if not self.b.fixed: self.b.force -= force

    def draw(self, screen):
        pygame.draw.line(screen, Color.white, self.a.pos, self.b.pos, 1)



class Shape:
    @staticmethod
    def get_jelly_circle(particles: Group, springs: Group, draw_layer: Group):
        s, c, rad = math.sin, math.cos, math.radians
        radius_outer = 100
        radius_inner = 30
        num_outer = 15
        num_inner = 7
        center = V2(APP.HW, APP.HH)

        outer_parts = []
        inner_parts = []

        # ===== Outer Circle Particles =====
        for i in range(num_outer):
            angle = (i / num_outer) * 360
            pos = V2(radius_outer * s(rad(angle)), radius_outer * c(rad(angle))) + center
            outer_parts.append(Particle(pos, 10, False, particles, draw_layer))

        # ===== Inner Circle Particles =====
        if num_inner > 1:
            for i in range(num_inner):
                angle = (i / num_inner) * 360
                pos = V2(radius_inner * s(rad(angle)), radius_inner * c(rad(angle))) + center
                inner_parts.append(Particle(pos, 10, False, particles, draw_layer))
        else:
            inner_parts.append(Particle(center, 10, False, particles, draw_layer))

        # ===== Springs =====

        # Perimeter springs: Outer ring
        for i in range(num_outer):
            a = outer_parts[i]
            b = outer_parts[(i + 1) % num_outer]
            Spring(a, b, 0.5, 0.1, springs, draw_layer)

        # Perimeter springs: Inner ring
        for i in range(num_inner):
            a = inner_parts[i]
            b = inner_parts[(i + 1) % num_inner]
            Spring(a, b, 0.5, 0.1, springs, draw_layer)

        # Optional: Web connections (fully connect inner to all outer points)
        for inner in inner_parts:
            for outer in outer_parts:
                Spring(inner, outer, 1, 0.1, springs, draw_layer)

        # Optional: Web connections (webly connect outer points)
        for i in range(len(outer_parts)):
            Spring(outer_parts[i], outer_parts[(i+4)%len(outer_parts)], 1.5, 0.1, springs, draw_layer)

        # Optional: Inner to inner full mesh (to avoid collapse)
        for i in range(num_inner):
                Spring(inner_parts[i], inner_parts[(i+2)%num_inner], 0.1, 0.1, springs, draw_layer)

    @staticmethod
    def get_jelly_quad(particles: Group, springs: Group, draw_layer: Group):
        # ===== Particles =====
        parts = []
        grid_width = 16
        grid_height = 9
        for y in range(grid_height):
            for x in range(grid_width): parts.append(Particle(V2(x * 50 + APP.HW - 300, y * 50 + 100), 10, False, particles, draw_layer))

        # ===== Springs =====
        spring_levels = [
            ([(1, 0), (0, 1)], 0.3),   # structural
            ([(1, 1), (-1, 1)], 0.22),  # shear
            ([(2, 0), (0, 2)], 0.15)    # bend
        ]
        for i, p in enumerate(parts):
            x = i % grid_width
            y = i // grid_width
            for connections, k in spring_levels:
                    for dx, dy in connections:
                        nx = x + dx
                        ny = y + dy
                        if 0 <= nx < grid_width and 0 <= ny < grid_height:
                            neighbor_index = ny * grid_width + nx
                            if i < neighbor_index: 
                                Spring(p, parts[neighbor_index], k, 0.01, springs, draw_layer)
