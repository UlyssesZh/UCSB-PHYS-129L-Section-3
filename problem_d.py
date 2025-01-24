#!/usr/bin/env python

import random

from matplotlib import pyplot as plt

from problem_abc import steps_count

random.seed(1108)

for a, b in [(2,3), (3,2), (3,5), (5,3), (3,12), (12,3)]:
	plt.hist(steps_count(a, b))
	plt.title(f'$L_{{{a},{b}}}$')
	plt.xlabel('Steps')
	plt.show()
