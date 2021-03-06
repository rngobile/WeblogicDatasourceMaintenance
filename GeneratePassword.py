#!/usr/bin/python
from os import urandom
from random import choice

class GeneratePassword:

    def __init__(self):
        #\8f(F%hL?y6Hh[BaT]o2Fw\aZ did not work.
        self.char_set = {'small': 'abcdefghijklmnopqrstuvwxyz',
                    'nums': '0123456789',
                    'big': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                    'special': '^!%=?{[]}+~#-_.:,;<>|\\'
                    }

    def generate_pass(self, length=25):
        """Function to generate a password"""

        password = []

        while len(password) < length:
            key = choice(self.char_set.keys())
            a_char = urandom(1)
            if a_char in self.char_set[key]:
                if self.check_prev_char(password, self.char_set[key]):
                    continue
                else:
                    password.append(a_char)
        return ''.join(password)


    def check_prev_char(self, password, current_char_set):
        """Function to ensure that there are no consecutive 
        UPPERCASE/lowercase/numbers/special-characters."""

        index = len(password)
        if index == 0:
            return False
        else:
            prev_char = password[index - 1]
            if prev_char in current_char_set:
                return True
            else:
                return False
