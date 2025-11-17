from pygame_template import *

class Circle(Sprite):
    def __init__(self, radius=50, pos=V2(APP.HW,APP.HH), *groups):
        super().__init__(*groups)

        self.image = pygame.Surface((radius*2,)*2, pygame.SRCALPHA)
        self.rect = self.image.get_frect(center = pos)
        self.pos = pos
        self.radius = radius

        self.image.fill((0,0,0,0))

        pygame.draw.circle(self.image, Color.random(), V2(self.rect.center) - V2(self.rect.topleft), radius)

    # COLLISION CHECKS

    def check_collision_circle(self, other: "Circle") -> bool:
        return self.pos.distance_to(other.pos) <= self.radius + other.radius
    
    def check_collision_rect(self, other: "Rect") -> bool:
        x, y = self.pos.x, self.pos.y
        x = max(min(x, other.rect.right), other.rect.left)
        y = max(min(y, other.rect.bottom), other.rect.top)
        return self.pos.distance_to((x,y)) < self.radius
    
    def check_collision_polygon(self, poly: "Polygon") -> bool:
        return poly.check_collision_circle(self)

    # COLLISION RESOLUTIONS

    def resolve_collision_circle(self, other: "Circle"):
        delta = self.pos - other.pos
        distance = delta.length()
        min_distance = self.radius + other.radius
        if distance == 0:
            delta = V2(1, 0)
            distance = 1
        overlap = min_distance - distance
        if overlap > 0:
            push_dir = delta.normalize()
            correction = push_dir * overlap
            self.pos += correction
            self.rect.center = self.pos

    def resolve_collision_rect(self, other: "Rect"):
        x = max(other.rect.left, min(self.pos.x, other.rect.right))
        y = max(other.rect.top,  min(self.pos.y, other.rect.bottom))
        closest_point = V2(x, y)
        delta = self.pos - closest_point
        distance = delta.length()
        if distance == 0:
            delta = V2(1, 0)
            distance = 1
        overlap = self.radius - distance
        if overlap > 0:
            correction = delta.normalize() * overlap
            self.pos += correction
            self.rect.center = self.pos

    def resolve_collision_polygon(self, poly: "Polygon"):
        global_points = [p + poly.rect.topleft for p in poly.local_points]
        closest_point = None
        min_dist = float("inf")
        for i in range(len(global_points)):
            a = global_points[i]
            b = global_points[(i + 1) % len(global_points)]
            ab = b - a
            ap = self.pos - a
            t = max(0, min(1, ap.dot(ab) / ab.length_squared()))
            p = a + ab * t
            dist = self.pos.distance_to(p)
            if dist < min_dist:
                min_dist = dist
                closest_point = p
        if min_dist < self.radius:
            correction_dir = (self.pos - closest_point).normalize()
            correction = correction_dir * (self.radius - min_dist)
            self.pos += correction
            self.rect.center = self.pos

    def move(self, direction: V2, dt: float):
        self.pos += direction * dt * 5
        self.rect.center = self.pos

    
        








class Rect(Sprite):
    def __init__(self, pos=V2(APP.HW,APP.HH), size=V2(100,100), *groups):
        super().__init__(*groups)

        self.size = size
        self.pos = pos
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.rect = self.image.get_frect(center = pos)
        self.image.fill(Color.random())
        self.prev_rect = self.rect.copy()

    # COLLISION CHECK

    def check_collision_rect(self, other: "Rect") -> bool:
        return self.rect.colliderect(other.rect)
    
    def check_collision_circle(self, circle: "Circle") -> bool:
        x = max(self.rect.left, min(circle.pos.x, self.rect.right))
        y = max(self.rect.top,  min(circle.pos.y, self.rect.bottom))
        return circle.pos.distance_to((x, y)) < circle.radius
    
    def check_collision_polygon(self, poly: "Polygon") -> bool:
        return poly.check_collision_rect(self)

    # COLLISION RESOLUTION

    def resolve_collision_rect(self, other: "Rect"):
        a, b, c = self.rect, self.prev_rect, other.rect

        if a.right > c.left and b.right <= c.left: a.right = c.left
        elif a.left < c.right and b.left >= c.right: a.left = c.right

        if a.bottom > c.top and b.bottom <= c.top: a.bottom = c.top
        elif a.top < c.bottom and b.top >= c.bottom: a.top = c.bottom
        self.pos = V2(a.center)

    def resolve_collision_circle(self, circle: "Circle"):
        x = max(self.rect.left, min(circle.pos.x, self.rect.right))
        y = max(self.rect.top,  min(circle.pos.y, self.rect.bottom))
        closest_point = V2(x, y)
        delta = closest_point - circle.pos
        distance = delta.length()
        if distance == 0:
            delta = V2(1, 0)
            distance = 1
        overlap = circle.radius - distance
        if overlap > 0:
            correction = delta.normalize() * overlap
            self.pos += correction
            self.rect.center = self.pos

    def resolve_collision_polygon(self, poly: "Polygon"):
        poly_pts = [V2(p + poly.rect.topleft) for p in poly.local_points]
        rect_pts = [
            V2(self.rect.topleft),
            V2(self.rect.topright),
            V2(self.rect.bottomright),
            V2(self.rect.bottomleft)
        ]

        def get_edges(pts): return [pts[(i + 1) % len(pts)] - pts[i] for i in range(len(pts))]
        def get_normals(edges): return [V2(-e.y, e.x).normalize() for e in edges]
        def project(pts, axis):
            dots = [p.dot(axis) for p in pts]
            return min(dots), max(dots)
        def get_overlap(minA, maxA, minB, maxB): return min(maxA, maxB) - max(minA, minB)

        edges = get_edges(poly_pts) + get_edges(rect_pts)
        axes = get_normals(edges)
        min_overlap = float("inf")
        smallest_axis = None

        for axis in axes:
            minA, maxA = project(poly_pts, axis)
            minB, maxB = project(rect_pts, axis)
            if maxA < minB or maxB < minA:
                return  # No collision
            overlap = get_overlap(minA, maxA, minB, maxB)
            if overlap < min_overlap:
                min_overlap = overlap
                smallest_axis = axis

        direction = (self.pos - poly.pos).normalize()
        if direction.dot(smallest_axis) < 0:
            smallest_axis = -smallest_axis
        correction = smallest_axis * min_overlap
        self.pos += correction
        self.rect.center = self.pos


    def move(self, direction: V2, dt: float, speed: float = 10):
        self.prev_rect = self.rect.copy()
        self.pos += direction * dt * speed
        self.rect.center = self.pos





from typing import Sequence

class Polygon(Sprite):
    def __init__(self, points: Sequence[V2], pos=V2(APP.HW,APP.HH), *groups):
        super().__init__(*groups)

        self.min_size_V2 = V2(min(*[p.x for p in points]), min(*[p.y for p in points]))
        self.max_size_V2 = V2(max(*[p.x for p in points]), max(*[p.y for p in points]))
        self.size = self.max_size_V2 - self.min_size_V2

        self.local_points = [p - self.min_size_V2 for p in points]
        self.pos = pos

        self.image = pygame.Surface(self.size, pygame.SRCALPHA)
        self.rect = self.image.get_frect(center = pos)
        self.prev_rect = self.rect.copy()

        self.image.fill((0,0,0,0))
        pygame.draw.polygon(self.image, Color.random(), self.local_points)

    # COLLISION CHECK

    def check_collision_polygon(self, other: "Polygon") -> bool:
        def get_edges(pts): return [pts[(i + 1) % len(pts)] - pts[i] for i in range(len(pts))]
        def get_normals(edges): return [V2(-e.y, e.x).normalize() for e in edges]
        def project(pts, axis):
            dots = [p.dot(axis) for p in pts]
            return min(dots), max(dots)
        def overlap(minA, maxA, minB, maxB): return maxA >= minB and maxB >= minA

        pointsA = [p + self.rect.topleft for p in self.local_points]
        pointsB = [p + other.rect.topleft for p in other.local_points]
        edges = get_edges(pointsA) + get_edges(pointsB)
        axes = get_normals(edges)

        for axis in axes:
            minA, maxA = project(pointsA, axis)
            minB, maxB = project(pointsB, axis)
            if not overlap(minA, maxA, minB, maxB):
                return False
        return True


    def check_collision_rect(self, rect: "Rect") -> bool:
        def get_edges(pts): return [pts[(i + 1) % len(pts)] - pts[i] for i in range(len(pts))]
        def get_normals(edges): return [V2(-e.y, e.x).normalize() for e in edges]
        def project(pts, axis):
            dots = [p.dot(axis) for p in pts]
            return min(dots), max(dots)
        def overlap(minA, maxA, minB, maxB): return maxA >= minB and maxB >= minA

        # Convert all points to Vector2
        poly_pts = [V2(p + self.rect.topleft) for p in self.local_points]
        rect_pts = [
            V2(rect.rect.topleft),
            V2(rect.rect.topright),
            V2(rect.rect.bottomright),
            V2(rect.rect.bottomleft)
        ]
        edges = get_edges(poly_pts) + get_edges(rect_pts)
        axes = get_normals(edges)

        for axis in axes:
            minA, maxA = project(poly_pts, axis)
            minB, maxB = project(rect_pts, axis)
            if not overlap(minA, maxA, minB, maxB):
                return False
        return True


    def check_collision_circle(self, circle: "Circle") -> bool:
        global_points = [p + self.rect.topleft for p in self.local_points]
        for i in range(len(global_points)):
            a = global_points[i]
            b = global_points[(i + 1) % len(global_points)]
            ab = b - a
            ap = circle.pos - a
            t = max(0, min(1, ap.dot(ab) / ab.length_squared()))
            closest = a + ab * t
            dist = circle.pos.distance_to(closest)
            if dist < circle.radius: return True
        if self.point_in_polygon(circle.pos, global_points): return True
        return False

    @staticmethod
    def point_in_polygon(point: V2, poly_points: list[V2]) -> bool:
        x, y = point
        inside = False
        n = len(poly_points)
        for i in range(n):
            xi, yi = poly_points[i]
            xj, yj = poly_points[(i + 1) % n]
            if ((yi > y) != (yj > y)):
                slope = (xj - xi) / (yj - yi + 1e-10)
                intersect_x = xi + (y - yi) * slope
                if x < intersect_x:
                    inside = not inside
        return inside

    # COLLISION RESOLUTION

    def resolve_collision_polygon(self, other: "Polygon"):
        get_edges = lambda pts: [pts[(i + 1) % len(pts)] - pts[i] for i in range(len(pts))]
        get_normals = lambda edges: [V2(-e.y, e.x).normalize() for e in edges]
        def project(pts, axis):
            dots = [p.dot(axis) for p in pts]
            return min(dots), max(dots)
        def get_overlap(minA, maxA, minB, maxB): return min(maxA, maxB) - max(minA, minB)
        pointsA = [p + self.rect.topleft for p in self.local_points]
        pointsB = [p + other.rect.topleft for p in other.local_points]
        edges = get_edges(pointsA) + get_edges(pointsB)
        axes = get_normals(edges)
        min_overlap = float("inf")
        smallest_axis = None
        for axis in axes:
            minA, maxA = project(pointsA, axis)
            minB, maxB = project(pointsB, axis)
            if maxA < minB or maxB < minA: return
            overlap = get_overlap(minA, maxA, minB, maxB)
            if overlap < min_overlap:
                min_overlap = overlap
                smallest_axis = axis
        direction = (self.pos - other.pos).normalize()
        if direction.dot(smallest_axis) < 0: smallest_axis = -smallest_axis
        correction = smallest_axis * min_overlap
        self.pos += correction
        self.rect.center = self.pos

    def resolve_collision_circle(self, circle: "Circle"):
        global_points = [p + self.rect.topleft for p in self.local_points]
        closest_point = None
        min_dist = float("inf")
        for i in range(len(global_points)):
            a = global_points[i]
            b = global_points[(i + 1) % len(global_points)]
            ab = b - a
            ap = circle.pos - a
            t = max(0, min(1, ap.dot(ab) / ab.length_squared()))
            p = a + ab * t
            dist = circle.pos.distance_to(p)
            if dist < min_dist:
                min_dist = dist
                closest_point = p
        if min_dist < circle.radius:
            correction_dir = (circle.pos - closest_point).normalize()
            correction = correction_dir * (circle.radius - min_dist)
            self.pos -= correction
            self.rect.center = self.pos

    def resolve_collision_rect(self, rect: "Rect"):
        poly_pts = [V2(p + self.rect.topleft) for p in self.local_points]
        rect_pts = [V2(rect.rect.topleft),V2(rect.rect.topright),V2(rect.rect.bottomright),V2(rect.rect.bottomleft)]
        def get_edges(pts): return [pts[(i + 1) % len(pts)] - pts[i] for i in range(len(pts))]
        def get_normals(edges): return [V2(-e.y, e.x).normalize() for e in edges]
        def project(pts, axis):
            dots = [p.dot(axis) for p in pts]
            return min(dots), max(dots)
        def get_overlap(minA, maxA, minB, maxB): return min(maxA, maxB) - max(minA, minB)
        edges = get_edges(poly_pts) + get_edges(rect_pts)
        axes = get_normals(edges)
        min_overlap = float("inf")
        smallest_axis = None
        for axis in axes:
            minA, maxA = project(poly_pts, axis)
            minB, maxB = project(rect_pts, axis)
            if maxA < minB or maxB < minA: return
            overlap = get_overlap(minA, maxA, minB, maxB)
            if overlap < min_overlap:
                min_overlap = overlap
                smallest_axis = axis
        direction = (self.pos - rect.pos).normalize()
        if direction.dot(smallest_axis) < 0: smallest_axis = -smallest_axis
        correction = smallest_axis * min_overlap
        self.pos += correction
        self.rect.center = self.pos


    def move(self, direction: V2, dt: float):
        self.prev_rect = self.rect.copy()
        self.pos += direction * dt * 5
        self.rect.center = self.pos
