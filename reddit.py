# coding: utf-8

import serial
ser = serial.Serial('/dev/ttyACM0', 9600)

while True:
	data = ser.readline()[:-2]
	if(data):
		print "┌──────────────────────────────────┐"
		print "│                                  │"
		print "│                 ,%&              │"
		print "│               ((/(&&&            │"
		print "│              @(%(((%%            │"
		print "│              ,,#(#%%#            │"
		print "│    ,,         @%#%#&&            │"
		print "│   *&&*(/,./../&%%&#@##%&*#(/     │"
		print "│.*%%&&@%%&@&###/((#(##&#%%#&*@@&&(│"
		print "│    &/(&#@%%%%%%####%%%%%%%%#/    │"
		print "│          ,%%#%%%#%%##%&#         │"
		print "│           ##(#%%&%%&(#%%         │"
		print "│           *%####(#%&%##%         │"
		print "│            #((#%#%%##(&          │"
		print "│            *###%&#%%%%.          │"
		print "│             .%%#&&&@@            │"
		print "│             ,(%@#%@&&&           │"
		print "│              %&(&%&#/            │"
		print "│                *%@&              │"
		print "│               ,#&%#              │"
		print "│               *#&&(              │"
		print "│               /(&@&              │"
		print "│               *(%&@              │"
		print "│                                  │"
		print "│               Decoy              │"
		print "└──────────────────────────────────┘"
