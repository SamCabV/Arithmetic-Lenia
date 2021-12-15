import numpy as np
import scipy.signal
import matplotlib.pylab as plt
import matplotlib.animation
import IPython.display
from matplotlib.widgets import Slider
import pygame
import matplotlib
matplotlib.use("Agg")
import matplotlib.backends.backend_agg as agg
import pylab
import pygame_menu
import pygame_menu.utils as ut
import time
np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)
# ptvLIB copyright (c) 2009 Luke Endres (Fallopiano)
#!/usr/bin/python 
import pygame
from pygame.locals import *
import random
import math
# attempt to import psyco
try: import psyco; psyco.full()
except: pass


def return_surface(width,height,alpha):
     # create our surface
     surface = pygame.Surface((width,height), pygame.SRCALPHA)
     # set all black pixels to transparent
     surface.set_colorkey((0,0,0))
     # apperently adding RLE_ACCEL as a flag to set_alpha
     # greatly increases the speed of per-pixel alpha blitting
     surface.set_alpha(alpha,RLEACCEL)
     return surface

def draw_alpha_rect(screen,color,x,y,rect,alpha):
     temp_surface = return_surface(rect.width,rect.height,alpha)
     color.append(alpha)
     temp_surface.fill(color)
     screen.blit(temp_surface,(x,y))

     
class Gradient():
    def __init__(self, palette, maximum):
        self.COLORS = palette
        self.N = len(self.COLORS)
        self.SECTION = maximum // (self.N - 1)

    def gradient(self, x):
        """
        Returns a smooth color profile with only a single input value.
        The color scheme is determinated by the list 'self.COLORS'
        """
        i = x // self.SECTION
        fraction = (x % self.SECTION) / self.SECTION
        c1 = self.COLORS[i % self.N]
        c2 = self.COLORS[(i+1) % self.N]
        col = [0, 0, 0]
        for k in range(3):
            col[k] = (c2[k] - c1[k]) * fraction + c1[k]
        return col


class Lenia:
  def __init__ (self):
    self.kernel_core = {
        0: lambda r: (4 * r * (1-r))**4,  # polynomial (quad4)
        1: lambda r: np.exp( 4 - 1 / (r * (1-r)) ),  # exponential / gaussian bump (bump4)
        2: lambda r, q=1/4: (r>=q)*(r<=1-q),  # step (stpz1/4)
        3: lambda r, q=1/4: (r>=q)*(r<=1-q) + (r<q)*0.5 # staircase (life)
    }
    self.growth_func = {
        0: lambda n, m, s: np.maximum(0, 1 - (n-m)**2 / (9 * s**2) )**4 * 2 - 1,  # polynomial (quad4)
        1: lambda n, m, s: np.exp( - (n-m)**2 / (2 * s**2) ) * 2 - 1,  # exponential / gaussian (gaus)
        2: lambda n, m, s: (np.abs(n-m)<=s) * 2 - 1  # step (stpz)
    }
    
    self.creatures = {
        0: [[]],
        1: [[0,0,0,0,0,0,0.1,0.14,0.1,0,0,0.03,0.03,0,0,0.3,0,0,0,0], [0,0,0,0,0,0.08,0.24,0.3,0.3,0.18,0.14,0.15,0.16,0.15,0.09,0.2,0,0,0,0], [0,0,0,0,0,0.15,0.34,0.44,0.46,0.38,0.18,0.14,0.11,0.13,0.19,0.18,0.45,0,0,0], [0,0,0,0,0.06,0.13,0.39,0.5,0.5,0.37,0.06,0,0,0,0.02,0.16,0.68,0,0,0], [0,0,0,0.11,0.17,0.17,0.33,0.4,0.38,0.28,0.14,0,0,0,0,0,0.18,0.42,0,0], [0,0,0.09,0.18,0.13,0.06,0.08,0.26,0.32,0.32,0.27,0,0,0,0,0,0,0.82,0,0], [0.27,0,0.16,0.12,0,0,0,0.25,0.38,0.44,0.45,0.34,0,0,0,0,0,0.22,0.17,0], [0,0.07,0.2,0.02,0,0,0,0.31,0.48,0.57,0.6,0.57,0,0,0,0,0,0,0.49,0], [0,0.59,0.19,0,0,0,0,0.2,0.57,0.69,0.76,0.76,0.49,0,0,0,0,0,0.36,0], [0,0.58,0.19,0,0,0,0,0,0.67,0.83,0.9,0.92,0.87,0.12,0,0,0,0,0.22,0.07], [0,0,0.46,0,0,0,0,0,0.7,0.93,1,1,1,0.61,0,0,0,0,0.18,0.11], [0,0,0.82,0,0,0,0,0,0.47,1,1,0.98,1,0.96,0.27,0,0,0,0.19,0.1], [0,0,0.46,0,0,0,0,0,0.25,1,1,0.84,0.92,0.97,0.54,0.14,0.04,0.1,0.21,0.05], [0,0,0,0.4,0,0,0,0,0.09,0.8,1,0.82,0.8,0.85,0.63,0.31,0.18,0.19,0.2,0.01], [0,0,0,0.36,0.1,0,0,0,0.05,0.54,0.86,0.79,0.74,0.72,0.6,0.39,0.28,0.24,0.13,0], [0,0,0,0.01,0.3,0.07,0,0,0.08,0.36,0.64,0.7,0.64,0.6,0.51,0.39,0.29,0.19,0.04,0], [0,0,0,0,0.1,0.24,0.14,0.1,0.15,0.29,0.45,0.53,0.52,0.46,0.4,0.31,0.21,0.08,0,0], [0,0,0,0,0,0.08,0.21,0.21,0.22,0.29,0.36,0.39,0.37,0.33,0.26,0.18,0.09,0,0,0], [0,0,0,0,0,0,0.03,0.13,0.19,0.22,0.24,0.24,0.23,0.18,0.13,0.05,0,0,0,0], [0,0,0,0,0,0,0,0,0.02,0.06,0.08,0.09,0.07,0.05,0.01,0,0,0,0,0]],
        2: [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.01,0.02,0.03,0.04,0.04,0.04,0.03,0.02,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.04,0.1,0.16,0.2,0.23,0.25,0.24,0.21,0.18,0.14,0.1,0.07,0.03,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.01,0.09,0.2,0.33,0.44,0.52,0.56,0.58,0.55,0.51,0.44,0.37,0.3,0.23,0.16,0.08,0.01,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.13,0.29,0.45,0.6,0.75,0.85,0.9,0.91,0.88,0.82,0.74,0.64,0.55,0.46,0.36,0.25,0.12,0.03,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.14,0.38,0.6,0.78,0.93,1.0,1.0,1.0,1.0,1.0,1.0,0.99,0.89,0.78,0.67,0.56,0.44,0.3,0.15,0.04,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.08,0.39,0.74,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.98,0.85,0.74,0.62,0.47,0.3,0.14,0.03,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.32,0.76,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.88,0.75,0.61,0.45,0.27,0.11,0.01,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.35,0.83,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.88,0.73,0.57,0.38,0.19,0.05,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.5,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.99,1.0,1.0,1.0,1.0,0.99,1.0,1.0,1.0,1.0,1.0,1.0,0.85,0.67,0.47,0.27,0.11,0.01], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.55,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.93,0.83,0.79,0.84,0.88,0.89,0.9,0.93,0.98,1.0,1.0,1.0,1.0,0.98,0.79,0.57,0.34,0.15,0.03], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.47,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.9,0.72,0.54,0.44,0.48,0.6,0.7,0.76,0.82,0.91,0.99,1.0,1.0,1.0,1.0,0.91,0.67,0.41,0.19,0.05], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.27,0.99,1.0,1.0,1.0,1.0,0.9,0.71,0.65,0.55,0.38,0.2,0.14,0.21,0.36,0.52,0.64,0.73,0.84,0.95,1.0,1.0,1.0,1.0,1.0,0.78,0.49,0.24,0.07], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.14,0.63,0.96,1.0,1.0,1.0,0.84,0.17,0,0,0,0,0,0,0,0.13,0.35,0.51,0.64,0.77,0.91,0.99,1.0,1.0,1.0,1.0,0.88,0.58,0.29,0.09], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.07,0.38,0.72,0.95,1.0,1.0,1.0,0.22,0,0,0,0,0,0,0,0,0,0.11,0.33,0.5,0.67,0.86,0.99,1.0,1.0,1.0,1.0,0.95,0.64,0.33,0.1], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.32,0.49,0.71,0.93,1.0,1.0,1.0,0.56,0,0,0,0,0,0,0,0,0,0,0,0.1,0.31,0.52,0.79,0.98,1.0,1.0,1.0,1.0,0.98,0.67,0.35,0.11],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.01,0.6,0.83,0.98,1.0,1.0,0.68,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.15,0.38,0.71,0.97,1.0,1.0,1.0,1.0,0.97,0.67,0.35,0.11], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.51,0.96,1.0,1.0,0.18,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.09,0.34,0.68,0.95,1.0,1.0,1.0,1.0,0.91,0.61,0.32,0.1], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.13,0.56,0.99,1.0,1.0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.17,0.45,0.76,0.96,1.0,1.0,1.0,1.0,0.82,0.52,0.26,0.07], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.33,0.7,0.94,1.0,1.0,0.44,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.33,0.68,0.91,0.99,1.0,1.0,1.0,1.0,0.71,0.42,0.19,0.03], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.53,0.89,1.0,1.0,1.0,0.8,0.43,0.04,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.47,0.86,1.0,1.0,1.0,1.0,1.0,0.95,0.58,0.32,0.12,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.77,0.99,1.0,0.97,0.58,0.41,0.33,0.18,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.54,0.95,1.0,1.0,1.0,1.0,1.0,0.8,0.44,0.21,0.06,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.39,0.83,1.0,1.0,0.55,0.11,0.05,0.15,0.22,0.06,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.58,0.99,1.0,1.0,1.0,1.0,1.0,0.59,0.29,0.11,0.01,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.04,0.55,0.81,0.86,0.97,1.0,1.0,0.5,0,0,0.01,0.09,0.03,0,0,0,0,0,0,0,0,0,0,0,0,0,0.26,0.78,1.0,1.0,1.0,1.0,1.0,0.66,0.35,0.13,0.03,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.33,1.0,1.0,1.0,1.0,1.0,1.0,0.93,0.11,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.23,0.73,0.95,1.0,1.0,1.0,1.0,1.0,0.62,0.35,0.12,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.51,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.72,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.56,0.25,0.09,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.12,0.38,1.0,1.0,1.0,0.66,0.08,0.55,1.0,1.0,1.0,0.03,0,0,0,0,0,0,0,0,0,0,0,0,0,0.35,1.0,1.0,1.0,1.0,1.0,1.0,0.67,0.12,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0.6,1.0,1.0,1.0,1.0,1.0,1.0,0.49,0,0,0.87,1.0,0.88,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1.0,1.0,1.0,1.0,1.0,1.0,0.7,0.07,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0.04,0.21,0.48,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0,0,0.04,0.42,0.26,0,0,0,0,0,0,0,0,0,0.12,0.21,0.34,0.58,1.0,1.0,1.0,0.99,0.97,0.99,0.46,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0.5,1.0,1.0,1.0,1.0,0.96,0,0.31,1.0,1.0,1.0,0.53,0,0,0,0,0,0,0,0,0.2,0.21,0,0,0,0.27,1.0,1.0,1.0,1.0,1.0,1.0,0.87,0.52,0.01,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0.84,1.0,1.0,1.0,1.0,1.0,0,0,0,0.83,1.0,1.0,0.52,0,0,0,0,0,0,0,0.26,0.82,0.59,0.02,0,0,0.46,1.0,1.0,1.0,1.0,1.0,0.9,0.55,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0.39,0.99,1.0,1.0,1.0,1.0,0.78,0.04,0,0,0,0.93,0.92,0,0,0,0,0,0,0,0,0.69,1.0,1.0,0.36,0,0,1.0,1.0,0.65,0.66,0.97,0.87,0.54,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0.55,0.75,0.59,0.74,1.0,1.0,0,0,0.75,0.71,0.18,0,0,0,0,0,0,0,0,0,0,0.29,0,0,0.45,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.47,0.39,0.71,0.25,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0.69,0.81,0.8,0.92,1.0,0.13,0,0,0.13,0.94,0.58,0,0,0,0,0,0,0,0,0,1.0,1.0,0.34,0,0.04,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.24,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0.63,0.85,0.9,0.98,1.0,0.09,0,0,0.02,1.0,0.64,0,0,0,0,0,0,0,0,0.59,1.0,1.0,0.84,0,0,1.0,1.0,1.0,1.0,1.0,1.0,0.64,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0.64,0.65,0.67,1.0,1.0,0.21,0.01,0,0.04,0.02,0,0,0,0,0,0,0,0,0,0.69,1.0,1.0,1.0,0.29,0.37,1.0,1.0,0.6,0.63,1.0,0.84,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0.44,0.73,0.73,0.85,1.0,0.97,0.23,0.05,0,0,0,0,0,0,0,0,0.06,0,0,0,0.97,1.0,1.0,1.0,1.0,1.0,1.0,0.33,0.24,0.67,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0.12,0.55,0.9,0.9,1.0,1.0,1.0,0.43,0.04,0,0,0,0,0,0,0,0.31,0.54,0,0,0,0.88,1.0,1.0,1.0,1.0,1.0,1.0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0.29,0.71,1.0,1.0,1.0,1.0,0.79,0.28,0,0,0,0,0,0,0,0,0.4,0.77,0.54,0,0,0.87,1.0,1.0,1.0,1.0,1.0,0.31,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0.16,0.27,0.41,0.72,0.99,1.0,1.0,0.82,0.42,0.09,0,0,0,0,0,0,0,0,0.1,0.55,0.58,0.58,0.77,0.99,1.0,1.0,1.0,1.0,0.63,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0.31,0.48,0.45,0.46,0.63,0.88,1.0,0.83,0.59,0.28,0.06,0,0,0,0,0,0,0,0,0,0.32,0.7,0.95,1.0,1.0,1.0,1.0,0.7,0.58,0.12,0.04,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0.23,0.54,0.53,0.48,0.57,0.59,0.65,0.63,0.55,0.35,0.13,0.03,0.02,0.09,0.74,1.0,0.09,0,0,0,0.32,0.86,1.0,1.0,1.0,1.0,0.57,0.44,0.31,0.16,0.01,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0.31,0.45,0.31,0.18,0.28,0.39,0.47,0.54,0.5,0.35,0.2,0.16,0.28,0.75,1.0,0.42,0.01,0,0,0.6,1.0,1.0,1.0,1.0,0.51,0.29,0.09,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0.14,0.3,0.4,0.54,0.71,0.74,0.65,0.49,0.35,0.27,0.47,0.6,0.6,0.72,0.98,1.0,1.0,1.0,1.0,0.65,0.33,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0.06,0.33,0.53,0.69,0.94,0.99,1.0,0.84,0.41,0.16,0.15,0.96,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.73,0.13,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0.42,0.86,0.98,0.98,0.99,1.0,0.94,0.63,0.32,0.62,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.65,0.23,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0.07,0.62,0.95,1.0,1.0,0.99,0.98,0.99,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.98,0.14,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0.03,0.46,0.89,1.0,1.0,0.97,0.83,0.75,0.81,0.94,1.0,1.0,1.0,1.0,0.99,0.03,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0.14,0.57,0.88,0.93,0.81,0.58,0.45,0.48,0.64,0.86,0.97,0.99,0.99,0.42,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0.23,0.45,0.47,0.39,0.29,0.19,0.2,0.46,0.28,0.03,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0.08,0.22,0.24,0.15,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0.07,0.22,0.14,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]],
        3: [[0,0,0,0,0,0,0,0,0,0,0,0.06,0.1,0.04,0.02,0.01,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0.15,0.37,0.5,0.44,0.19,0.23,0.3,0.23,0.15,0.01,0,0,0,0], [0,0,0,0,0,0,0.32,0.78,0.26,0,0.11,0.11,0.1,0.08,0.18,0.16,0.17,0.24,0.09,0,0,0], [0,0,0,0,0.45,0.16,0,0,0,0,0,0.15,0.15,0.16,0.15,0.1,0.09,0.21,0.24,0.12,0,0], [0,0,0,0.1,0,0,0,0,0,0,0,0.17,0.39,0.43,0.34,0.25,0.15,0.16,0.15,0.25,0.03,0], [0,0.15,0.06,0,0,0,0,0,0,0,0.24,0.72,0.92,0.85,0.61,0.47,0.39,0.27,0.12,0.18,0.17,0], [0,0.08,0,0,0,0,0,0,0,0,1.0,1.0,1.0,1.0,0.73,0.6,0.56,0.31,0.12,0.15,0.24,0.01], [0,0.16,0,0,0,0,0,0,0,0.76,1.0,1.0,1.0,1.0,0.76,0.72,0.65,0.39,0.1,0.17,0.24,0.05], [0,0.05,0,0,0,0,0,0,0.21,0.83,1.0,1.0,1.0,1.0,0.86,0.85,0.76,0.36,0.17,0.13,0.21,0.07], [0,0.05,0,0,0.02,0,0,0,0.4,0.91,1.0,1.0,1.0,1.0,1.0,0.95,0.79,0.36,0.21,0.09,0.18,0.04], [0.06,0.08,0,0.18,0.21,0.1,0.03,0.38,0.92,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.64,0.31,0.12,0.07,0.25,0], [0.05,0.12,0.27,0.4,0.34,0.42,0.93,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.97,0.33,0.16,0.05,0.1,0.26,0], [0,0.25,0.21,0.39,0.99,1.0,1.0,1.0,1.0,1.0,1.0,0.86,0.89,0.94,0.83,0.13,0,0,0.04,0.21,0.18,0], [0,0.06,0.29,0.63,0.84,0.97,1.0,1.0,1.0,0.96,0.46,0.33,0.36,0,0,0,0,0,0.03,0.35,0,0], [0,0,0.13,0.22,0.59,0.85,0.99,1.0,0.98,0.25,0,0,0,0,0,0,0,0,0.34,0.14,0,0], [0,0,0,0,0.33,0.7,0.95,0.8,0.33,0.11,0,0,0,0,0,0,0,0.11,0.26,0,0,0], [0,0,0,0,0.16,0.56,0.52,0.51,0.4,0.18,0.01,0,0,0,0,0,0,0.42,0,0,0,0], [0,0,0,0,0.01,0,0.33,0.47,0.33,0.05,0,0,0,0,0,0,0.35,0,0,0,0,0], [0,0,0,0,0,0.26,0.32,0.13,0,0,0,0,0,0,0,0.34,0,0,0,0,0,0], [0,0,0,0,0,0.22,0.25,0.03,0,0,0,0,0,0,0.46,0,0,0,0,0,0,0], [0,0,0,0,0,0,0.09,0.2,0.22,0.23,0.23,0.22,0.3,0.3,0,0,0,0,0,0,0,0]]
    }
    self.multi_k = False
    self.n = 256
    self.A = np.zeros([self.n, self.n])
    self.T = 10
    self.R = 13
    self.m = 0.11
    self.s = 0.05
    
    self.k_core = self.kernel_core[0]
    self.growth = self.growth_func[0]
    self.dx = 1/self.R
    self.dt = 1/self.T
    self.beta =np.asarray([1])
    self.kernel, self.k_fft = self.calc_kernel()
    self.img = None
    self.fig = plt.figure()
    #self.sz = 1
    self.margin = 0
    self.offset = (25, 25)
    self.sz = 2
    self._fps = 30
    self._clock =pygame.time.Clock()
    self._screen_width = 900
    self.add_noise()
    self.add_noise()
   
  def start_ui(self):
    self._surface = pygame.display.set_mode((1600, 950), pygame.SRCALPHA)

    theme = pygame_menu.Theme(
            background_color=pygame_menu.themes.TRANSPARENT_COLOR,
            title=False,
            widget_font=pygame_menu.font.FONT_FIRACODE,
            widget_font_color=(255, 255, 255),
            widget_margin=(0, 0),
            widget_selection_effect=pygame_menu.widgets.NoneSelection()
        )
    self._menu = pygame_menu.Menu(
            height=950,
            mouse_motion_selection=True,
            position=(645, -50, False),
            theme=theme,
            title='',
            width=500
        )
    
    self._menu.add.text_input(
        'Beta: ',
        maxwidth= 10,
        textinput_id='Beta_Input',
        input_underline='_',
        font_size=20,
        width = 5
    )
    self._menu.add.button(
      'Add Beta',
      self.add_beta,
      button_id='add_beta',
      font_size=20,
      margin=(0, 30),
      shadow_width=10,
      )
    #selectable kernel equations
    kernel_items = [('Polynomial',0),
            ('Gaussian',1),
            ('Step',2),
            ('Staircase',3)]

    growth_items = [('Polynomial',0),
                ('Gaussian', 1),
                ('Step', 2),]

    creature_items = [('None', 0),
                    ('Orbium', 1),
                    ('Geminium', 2),
                    ('Fish', 3)]
    '''
    the_a_items = [('1','1')]

    self._menu.add.dropselect(
        'Select A:\t',
        the_a_items,
        selector_id='A',
        default=1
    )
    '''
    # Create selector with kernel options
    k_sel = self._menu.add.dropselect(
        'Select Kernel Shape: ',
        kernel_items,
        dropselect_id='kernel',
        default=0,
        font_size = 20
    )
    g_sel = self._menu.add.dropselect(
        'Select Growth:',
        growth_items,
        dropselect_id='growth',
        default=0,
        font_size = 20
    )
    c_sel = self._menu.add.dropselect(
        'Select Creature:',
        creature_items,
        dropselect_id='creature',
        default=0,
        font_size = 20
    )
    
    self._menu.add.button(
      'Add Creature',
      self.add_creature,
      button_id='add_creature',
      font_size=20,
      margin=(0, 30),
      shadow_width=10,
      )
    

    # Single value from range
    rslider = self._menu.add.range_slider('Choose R', 18, (0, 256), 1,
                                             rangeslider_id='R_value',
                                             value_format=lambda x: str(int(x)), font_size = 20)

    mslider = self._menu.add.range_slider('Choose M', 0.26,(0, 1),0.01,
                                            rangeslider_id='M_value',
                                            value_format=lambda x: str(x), font_size = 20)

    sslider = self._menu.add.range_slider('Choose S', 0.036,(0, 1),0.01,
                                            rangeslider_id='S_value',
                                            value_format=lambda x: str(x), font_size = 20)
                                            
    tslider = self._menu.add.range_slider('Choose T', 10,(1, 50),1,
                                            rangeslider_id='T_value',
                                            value_format=lambda x: str(x), font_size = 20)
    self._menu.add.button(
      'Clear Screen',
      self.clear_screen,
      button_id='clear_screen',
      font_size=20,
      margin=(0, 30),
      shadow_width=10,
      )
    self._menu.add.button(
      'Add Noise',
      self.add_some_noise,
      button_id='add_noise',
      font_size=20,
      margin=(0, 30),
      shadow_width=10,
      )
    kernel_items = [('1',1),
            ('2',2),
            ('3',3)]
    
    k_num = self._menu.add.dropselect(
        'Kernel Num:',
        kernel_items,
        dropselect_id='k_num',
        default=0,
        font_size = 15,
        height = 10
    )
    self._menu.add.text_input(
        'Ms: ',
        maxwidth= 10,
        textinput_id='M_s',
        input_underline='_',
        font_size=14,
        width = 3
    ).translate(-150,10)
    self._menu.add.text_input(
        'Rs: ',
        maxwidth= 10,
        textinput_id='R_s',
        input_underline='_',
        font_size=14,
        width = 3).translate(120,-20)
    self._menu.add.text_input(
        'Ss: ',
        maxwidth= 10,
        textinput_id='S_s',
        input_underline='_',
        font_size=14,
        width = 3
    ).translate(-150,10)
    self._menu.add.text_input(
        'Bs: ',
        maxwidth= 10,
        textinput_id='B_s',
        input_underline='_',
        font_size=14,
        width = 3).translate(120,-20)
    self._menu.add.button(
      'Start Multi-Growth/Multi-K',
      self.set_multi_k,
      button_id='multi_k',
      font_size=20,
      margin=(0, 30),
      shadow_width=10,
      ).translate(0,20)
  def rip_input(self,input):
    in_str = self._menu.get_widget(input).get_value()
    in_list = in_str.split(",")
    if len(in_list) == 1:
      return float(in_list[0])
    else:
      return np.array(in_list, dtype=float)
  def rip_bs(self,input):
    in_str = self._menu.get_widget(input).get_value()
    in_list = in_str.split(",")
    inner_list = []
    for i in in_list:
      inner_list.append(i[1:len(i)-1])
    self.bs= [np.array(i.split(":"), dtype =float) for i in inner_list]
    


  def set_multi_k(self):
    self.k_num = self._menu.get_widget("k_num").get_value()[1]
    self.Ss = self.rip_input("S_s")
    self.rip_bs("B_s")
    self.Rs = self.rip_input("R_s")
    self.Ms = self.rip_input("M_s")
    self.multi_k = True
    mid = self.n //2
    Ds = [np.linalg.norm(np.ogrid[-mid:mid, -mid:mid]) / self.Rs[i] * len(beta) for i, beta in enumerate(self.bs)]
    self.Ks = [(Ds[i]<len(beta)) * beta[np.minimum(Ds[i].astype(int),len(beta)-1)] * self.k_core(Ds[i] % 1) for i, beta in enumerate(self.bs)]
    nKs = [ K / np.sum(K) for K in self.Ks ]
    self.fKs = [ np.fft.fft2(np.fft.fftshift(K)) for K in nKs ]


  def figure_asset(self,K, growth, R,screen,cmap='inferno'):
    K_size = K.shape[0]; K_mid = K_size // 2
    fig, ax = plt.subplots(3, 1, figsize=(4,8), gridspec_kw={'width_ratios': [1]})
    ax[0].imshow(K, cmap=cmap, interpolation="nearest", vmin=0)
    ax[0].title.set_text('Kernel K')
    ax[1].plot(range(K_size), K[K_mid,:])
    x = np.linspace(0, 1, 1000) # K_sum must be 1
    ax[2].plot(x, self.growth(x,self.m,self.s))
    ax[2].axhline(y=0, color='grey', linestyle='dotted')
    ax[2].title.set_text('Growth G')
    canvas = agg.FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.tostring_rgb()
    surf = pygame.image.fromstring(raw_data, canvas.get_width_height(),'RGB')
    screen.blit(surf,(1200,20))  
  def calc_kernel(self):
    #R = 64
    if self.multi_k == False:
      mid = self.n //2
      D = np.linalg.norm(np.ogrid[-mid:mid, -mid:mid]) / self.R * len(self.beta)
      kernel = (D<len(self.beta)) * self.beta[np.minimum(D.astype(int),len(self.beta)-1)] * self.k_core(D % 1)
      k_fft = np.fft.fft2(np.fft.fftshift(kernel / np.sum(kernel)))
      return kernel, k_fft

  def fig_world(self, cmap='inferno'):
    #global img
    self.img = plt.imshow(self.A, cmap=cmap, interpolation="nearest", vmin=0)
    plt.close()
    return 
  '''
  def update(self,i):
    #global A, img
    #print(i)
    if i < 10 and i % 2 == 0:
      self.add_noise()
    U = np.real(np.fft.ifft2(self.k_fft * np.fft.fft2(self.A)))
    self.A = np.clip(self.A + 1/T * self.growth(U,self.m ,self.s), 0, 1)
    self.img.set_array(self.A)
    return self.img, 
  '''
  def update_grid(self):
    if self.multi_k == 0:
      U = np.real(np.fft.ifft2(self.k_fft * np.fft.fft2(self.A)))
      self.A = np.clip(self.A + 1/self.T * self.growth(U,self.m ,self.s), 0, 1)
      return self.A
    else:
      Us = [ np.real(np.fft.ifft2(fK * np.fft.fft2(self.A))) for fK in self.fKs ]
      Gs = [ self.growth(Us[i], self.Ms[i], self.Ss[i]) for i,stuff in enumerate(Us)]
      self.A = np.clip(self.A + 1/self.T * np.mean(np.asarray(Gs),axis=0), 0, 1)
      return self.A
  '''
  def run_sim(self):
    self.fig_world()
    disp = IPython.display.DisplayHandle()
    figure_asset(self.kernel, self.growth, self.R)
    disp.display(IPython.display.HTML(matplotlib.animation.FuncAnimation(self.fig, self.update, frames=500, interval=20).to_jshtml()))

    plt.show()
  '''
  def add_noise(self):
    cx = int(np.random.choice(np.linspace(0, 44, 53)))
    cy = int(np.random.choice(np.linspace(0, 44, 53)))
    C = np.random.choice(np.linspace(0,1,1000), (200, 200))
    self.A[cx:cx+C.shape[0], cy:cy+C.shape[1]] = C
  def draw_lenia(self, surface):

    # Sweep through every cell, take its information
    # Draw an appropriate square representing each cell
    if self.multi_k == 0:
      for i, tile in enumerate(self.A):
          for j, tile_contents in enumerate(tile):
              myrect = pygame.Rect((self.margin + self.sz) * i + self.margin + self.offset[0],(self.margin + self.sz) * j + self.margin + self.offset[1], self.sz, self.sz)
              #curr_x = (self.margin + self.sz) * i + self.margin + self.offset[0]
              #curr_y = (self.margin + self.sz) * j + self.margin + self.offset[1]
              #test = colormap(int(tile_contents*1000))
              #test.append(0)
              
              pygame.draw.rect(surface, colormap(int(tile_contents*1000)), myrect)
              #draw_alpha_rect(surface, colormap(int(tile_contents*1000)), curr_x, curr_y, myrect, 100)
          pygame.event.pump()

  def add_some_noise(self):
    self.add_noise()
    self.add_noise()
    self.add_noise()
  def clear_screen(self):
    self.A = np.zeros([self.n, self.n])
  
  def add_creature(self):
    cx = int(np.random.choice(np.linspace(0, 200, 200)))
    cy = int(np.random.choice(np.linspace(0, 200, 200)))
    creature_num = self._menu.get_widget('creature').get_value()[1]
    C = np.asarray(self.creatures[creature_num])
    self.A[cx:cx+C.shape[0], cy:cy+C.shape[1]] = C

  def add_beta(self):
    beta_str = self._menu.get_widget('Beta_Input').get_value()
    beta_list = beta_str.split(",")
    if len(beta_list) == 1:
      self.beta = float(beta_list[0])
    else:
      self.beta = np.array(beta_list, dtype=float)
  
  def _update_gui(self, draw_background=True, draw_menu=True, draw_grid=True) -> None:
      """
      Updates the gui.
      :param draw_background: Draw the background
      :param draw_menu: Draw the menu
      :param draw_grid: Draw the grid
      """
      if draw_background:
          # Draw a black background to set everything on
          self._surface.fill(BACKGROUND)
      #if self._clock.get_time() % 2==0:
      self.figure_asset(self.kernel, self.growth,self.R, self._surface, cmap='inferno')


      if draw_grid:
          # Draw the grid
          #for row in range(self._rows):
          #   for column in range(self._rows):
          #        self._draw_square(self._grid, row, column)
          self.draw_lenia(self._surface)
      if draw_menu:
          self._menu.draw(self._surface)
      pygame.event.pump()
  
  def set_vars(self):
    #self.A = grid
    self.T = self._menu.get_widget('T_value').get_value()
    self.R = self._menu.get_widget('R_value').get_value()
    self.m = self._menu.get_widget('M_value').get_value()
    self.s = self._menu.get_widget('S_value').get_value()
    core = self._menu.get_widget('kernel').get_value()
    self.k_core = self.kernel_core[core[1]]
    self.growth = self.growth_func[self._menu.get_widget('growth').get_value()[1]]
    self.dx = 1/self.R
    self.dt = 1/self.T
    if self.multi_k == 0:
      self.kernel, self.k_fft = self.calc_kernel()
    return
  def mainloop(self):
    self._update_gui()
    while True:
      # Application events
      events = pygame.event.get()

      # Update the menu
      self._menu.update(events)

      # If a menu widget disable its active state, disable the events, this is due to
      # user can click outside a dropselection box, and that triggers the disable active
      # state. If so, the event is destroyed, thus avoiding clicking the canvas
      if pygame_menu.events.MENU_LAST_WIDGET_DISABLE_ACTIVE_STATE in self._menu.get_last_update_mode()[0]:
          events = []

      for event in events:
          # User closes
          if event.type == pygame.QUIT:
              self._quit()
              pygame.display.flip()

      # Update the app
      self.set_vars()
      self.update_grid()
      self._update_gui()

      #self._grid[self._start_point[0]][self._start_point[1]].update(nodetype='start')
      #self._grid[self._end_point[0]][self._end_point[1]].update(nodetype='end')

      # Flip surface
      pygame.display.flip()

      # Update clock
      self._clock.tick(self._fps)
      
      # At first loop returns
      



if __name__ == "__main__":
  pygame.init()
  CYAN = (0, 255, 255)
  MAGENTA = (255, 0, 255)
  BACKGROUND = (34, 40, 44)

  lenia = Lenia()
  lenia.start_ui()
  colormap = Gradient([MAGENTA, CYAN], 1000).gradient
  lenia.mainloop()
  