import random
import pygame
import sys
import time

pygame.init()
WIDTH, HEIGHT = 700, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Smart Traffic Signal ")
clock = pygame.time.Clock()

# Colors
GRASS = (34, 139, 34)
ROAD = (50, 50, 50)
WHITE = (255, 255, 255)
RED = (255, 70, 70)
GREEN = (70, 255, 70)
ORANGE = (255, 165, 0)

font = pygame.font.SysFont("Arial", 46, bold=True)
timer_font = pygame.font.SysFont("Arial", 26)
small_font = pygame.font.SysFont("Arial", 18)

road_thickness = 220

