#!/usr/bin/python
import random 

class NewGeneratePassword:

    def __init__(self):
	self.char_set = 'abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ^!%/=?{[]}+~#-_.:,;<>|\\'

    def generate_pass(self, length=25):
	return "".join(random.sample(self.char_set,length))
