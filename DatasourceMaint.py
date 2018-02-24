#!/usr/bin/python
from OracleDB import *
from GeneratePassword import *

def main():
    password1 = GeneratePassword()
    db = OracleDB("192.168.254.134",1521,"soadb","rn_test",'\8f(F%hL?y6Hh[BaT]o2Fw\aZ',1)
    db.changePassword(password1.generate_pass())

if __name__ == '__main__':
    main()