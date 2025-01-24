#!/usr/bin/env python

from numpy import arange, meshgrid, random, vectorize, average
from matplotlib import pyplot as plt

from problem_abc import steps_count

random.seed(1108)

low = 2
high = 30

heat = vectorize(lambda a, b: average(steps_count(a, b, 100)))
a, b = meshgrid(arange(low, high+1), arange(low, high+1))
im = plt.imshow(heat(a, b), origin='lower', extent=(low-0.5,high+0.5,low-0.5,high+0.5))
cbar = plt.colorbar(im)
cbar.set_label('Average steps')
plt.xlabel('$a$')
plt.ylabel('$b$')
plt.xticks(arange(low, high+1))
plt.yticks(arange(low, high+1))
plt.show()
