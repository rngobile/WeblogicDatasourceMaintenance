#!/usr/bin/python
import random 

class NewGeneratePassword:

    def __init__(self):
        self.char_set = 'abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ^!%/=?{[]}+~#-_.:,;<>|\\'
        self.passwordList = []
        self.oldChar = ''
        self.newChar = ''
        self.password = ''

    def generate_pass(self, length=25):
        #return "".join(random.sample(self.char_set,length))
        for i in range(length):
            self.newChar =  self.char_set[random.randrange(len(self.char_set))]
            if (i == 0) or (self.newChar != self.oldChar):
                self.passwordList.append(self.newChar)
                self.oldChar = self.newChar
            else:
                i-=1
        
        self.password = ''.join(self.passwordList)
        return self.password
