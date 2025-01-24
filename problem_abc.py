#!/usr/bin/env python

import random

class TuringMachine:
	def __init__(self, states, initial_state, final_states, initial_head=0, blank_symbol='B', wildcard_symbol='*', output_file=None):
		self.initial_head = initial_head
		self.initial_state = initial_state
		self.states = states
		self.state = initial_state
		self.blank_symbol = blank_symbol
		self.wildcard_symbol = wildcard_symbol
		self.final_states = final_states
		self.output_file = output_file

	def step(self):
		if self.head >= len(self.tape):
			self.tape.extend([self.blank_symbol] * (self.head - len(self.tape) + 1))
		if self.head < 0:
			self.tape = [self.blank_symbol] * (-self.head) + self.tape
			self.head = 0
		#print(f'{self.state}\t{''.join(self.tape[:self.head])}\033[96m{self.tape[self.head]}\033[0m{''.join(self.tape[self.head + 1:])}')

		current_symbol = self.tape[self.head]
		if (self.state, current_symbol) in self.states:
			new_symbol, direction, new_state = self.states[(self.state, current_symbol)]
		elif (self.state, self.wildcard_symbol) in self.states:
			new_symbol, direction, new_state = self.states[(self.state, self.wildcard_symbol)]
		else:
			raise ValueError(f"No transition defined for state '{self.state}' and symbol '{current_symbol}'.")
		if new_symbol == self.wildcard_symbol:
			new_symbol = current_symbol

		self.tape[self.head] = new_symbol
		self.state = new_state

		if direction == 'R' or direction == 'r':
			self.head += 1
		elif direction == 'L' or direction == 'l':
			self.head -= 1

	def run(self, tape):
		self.tape = list(tape)
		self.head = self.initial_head
		self.state = self.initial_state
		step_count = 0
		while self.state not in self.final_states:
			self.step()
			step_count += 1
		if self.output_file:
			with open(self.output_file, 'a') as f:
				f.write(self.get_tape_content())
				f.write('\n')
		return step_count

	def get_tape_content(self):
		return ''.join(self.tape).strip(self.blank_symbol)
	
	def states_count(self):
		states = set()
		for (state, symbol), (new_symbol, direction, new_state) in self.states.items():
			states.add(state)
			states.add(new_state)
		return len(states)
	
	@classmethod
	def from_code(cls, code):
		lines = [line.split(';')[0].strip() for line in code.split('\n')]
		lines = [line for line in lines if line]
		states = dict()
		final_states = set()
		for line in lines:
			state, symbol, new_symbol, direction, new_state = line.split()
			states[(state, symbol)] = (new_symbol, direction, new_state)
			if new_state.startswith('halt'):
				final_states.add(new_state)
		initial_state = lines[0].split()[0]
		return cls(states, initial_state, final_states)

mul_machine = TuringMachine.from_code("""
90 # B r 90
90 $ B l 91
90 * * r 90
91 B B l 92
91 * * l 91
92 B B l 2
92 * * l 92

; Set up tally
0 * * l 1
1 B B l 2
2 B 0 r 3
3 B B r 10

; Find end of num1
10 B B l 11
10 # # l 11
10 0 0 r 10
10 1 1 r 10


; If last digit of num1 is 0, multiply num2 by 2
11 0 # r 20
; If last digit of num1 is 1, add num2 to tally and then multiply num2 by 2
11 1 # r 30


; Multiply num2 by 2
20 B B r 20
20 # # r 20
20 * * r 21
21 B 0 l 25 ; Multiplication by 2 done, return to end of num1
21 * * r 21
25 B B l 26
25 * * l 25
26 B B r 80 ; Finished multiplying. Clean up
26 # # l 26
26 0 0 * 11
26 1 1 * 11

; Add num2 to tally
30 B B r 30
30 # # r 30
30 * * r 31
31 B B l 32
31 * * r 31
32 0 y l 40 ; Add a zero
32 1 x l 50 ; Add a one
32 y y l 32
32 x x l 32
32 B B r 70 ; Finished adding

; Adding a 0 to tally
40 B B l 41
40 * * l 40 ; Found end of num2
41 B B l 41
41 * * l 42 ; Found start of num1
42 B B l 43 ; Found end of num1
42 * * l 42
43 y y l 43
43 x x l 43
43 0 y r 44
43 1 x r 44
43 B y r 44
44 B B r 45 ; Found end of tally
44 * * r 44
45 B B r 45
45 * * r 46 ; Found start of num1
46 B B r 47 ; Found end of num1
46 * * r 46
47 B B r 47
47 * * r 48
48 B B l 32 ; Found end of num2
48 * * r 48

; Adding a 1 to tally
50 B B l 51 ; Found end of num2
50 * * l 50
51 B B l 51
51 * * l 52 ; Found start of num1
52 B B l 53 ; Found end of num1
52 * * l 52
53 y y l 53
53 x x l 53
53 B x r 55
53 0 x r 55 ; return to num2
53 1 y l 54
54 0 1 r 55
54 1 0 l 54
54 B 1 r 55
55 B B r 56 ; Found end of tally
55 * * r 55
56 B B r 56
56 * * r 57 ; Found start of num1
57 B B r 58 ; Found end of num1
57 * * r 57
58 B B r 58
58 * * r 59
59 B B l 32 ; Found end of num2
59 * * r 59

; Finished adding, clean up
70 x 1 r 70
70 y 0 r 70
70 B B l 71
71 B B l 72 ; Found end of num2
71 * * l 71
72 B B l 72
72 * * l 73 ; Found start of num1
73 B B l 74
73 * * l 73
74 y 0 l 74
74 x 1 l 74
74 * * r 75 ; Finished cleaning up tally
75 B B r 76
75 * * r 75
76 B B r 20 ; Multiply num2 by 2
76 * * r 76

; Finished multiplying, clean up
80 # B r 80
80 B B r 81
81 B B l 82
81 * B r 81
82 B B l 82
82 * * * halt
""")

def steps_count(a, b, sample_count=1000):
	result = []
	if 2**(a-1) * 2**(b-1) > sample_count:
		def samples():
			for _ in range(sample_count):
				yield random.randrange(2**(a-1), 2**a), random.randrange(2**(b-1), 2**b)
	else:
		def samples():
			for num1 in range(2**(a-1), 2**a):
				for num2 in range(2**(b-1), 2**b):
					yield num1, num2
	for num1, num2 in samples():
		result.append(multiply(f'1{num1:b}#1{num2:b}$'))
	return result

def multiply(input_tape):
	return mul_machine.run(input_tape)

if __name__ == '__main__':
	# b
	mul_machine.output_file = 'output.dat'
	with open('output.dat', 'w') as f:
		f.write('')
	multiply('101001010111#101000101$')
	multiply('101111#101001$')
	mul_machine.output_file = None

	# c
	with open('states_count.txt', 'w') as f:
		f.write(str(mul_machine.states_count()) + '\n')
