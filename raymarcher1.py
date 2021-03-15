import argparse
import contextlib
import io
import time

from math import cos
from math import fabs
from math import sin
from math import tau

with contextlib.redirect_stdout(io.StringIO()):
    import pygame

from pygame import Color
from pygame import Vector3

SPHERE_RADIUS = .7

PIXELS = []
N = 8
for x in range(N+1):
    p = x / N
    c = int(p * 255)
    PIXELS.append(Color(c,)*3)

t = 0

def surface_distance(pos):
    center = Vector3(0, 0, 0)
    return (pos - center).length() - SPHERE_RADIUS

class Shader:

    def __init__(self):
        self.x = 50
        self.y = 20
        self.z = 50

    def shade(self, pos):
        L = Vector3(
            self.x * sin(t),
            self.y,
            self.z * cos(t)
        )
        L = L.normalize()

        dt = 1e-6
        current_val = surface_distance(pos)

        x = Vector3(pos.x + dt, pos.y, pos.z)
        dx = surface_distance(x) - current_val
        y = Vector3(pos.x, pos.y + dt, pos.z)
        dy = surface_distance(y) - current_val
        z = Vector3(pos.x, pos.y, pos.z + dt)
        dz = surface_distance(z) - current_val
        # normal
        N = Vector3(
            (dx - pos.x) / dt,
            (dy - pos.y) / dt,
            (dz - pos.z) / dt,
        )
        if N.length() < 1e-9:
            return PIXELS[0]
        N = N.normalize()
        diffuse = L.x * N.x + L.y * N.y + L.z * N.z
        diffuse = (diffuse + 1) / 2 * len(PIXELS)
        return PIXELS[int(diffuse) % len(PIXELS)]


def draw(rect, surface, position, shader):
    for y in range(rect.height):
        for x in range(rect.width):
            pos = position
            target = Vector3(
                x / rect.width - .5,
                (y / rect.height - .5) * (rect.height / rect.width) * 1.5,
                -1.5
            )
            ray = target - pos
            ray.normalize()
            pixel = PIXELS[0]
            max_ = 9_999
            for _ in range(15_000):
                if (fabs(pos.x) > max_
                        or fabs(pos.y) > max_
                        or fabs(pos.z) > max_):
                    break
                dist = surface_distance(pos)
                if dist < 1e-1:
                    pixel = shader.shade(pos)
                    break
                pos = pos + ray * dist
            surface.set_at((x,y), pixel)

def run():
    global SPHERE_RADIUS
    global t
    pygame.font.init()
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 30)
    screen = pygame.display.set_mode((800,800))
    buffer = pygame.Surface((80,40))
    rect = buffer.get_rect()
    position = Vector3(0, 0, -2)
    step = .005
    shader = Shader()
    running = True
    while running:
        elapsed = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                elif event.key == pygame.K_LEFT:
                    SPHERE_RADIUS += step
                    print(SPHERE_RADIUS)
                elif event.key == pygame.K_RIGHT:
                    SPHERE_RADIUS -= step
                    print(SPHERE_RADIUS)
        #
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_UP]:
            position.z += step
            print(position)
        elif pressed[pygame.K_DOWN]:
            position.z -= step
            print(position)
        elif pressed[pygame.K_a]:
            shader.x += 1
            print(shader.x)
        elif pressed[pygame.K_z]:
            shader.x -= 1
            print(shader.x)
        #
        buffer.fill((0,0,0))
        draw(rect, buffer, position, shader)
        pygame.transform.scale(buffer, screen.get_rect().size, screen)
        img = font.render(f'{t:.04f}', True, (200,200,200))
        screen.blit(img, (0,0))
        pygame.display.flip()
        #
        t = (t + elapsed / 1000 * 1) % tau

def main(argv=None):
    """
    https://ch-st.de/its-ray-marching-march/
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    args = parser.parse_args(argv)
    run()

if __name__ == '__main__':
    main()
