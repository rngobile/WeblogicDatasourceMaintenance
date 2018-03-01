#!/usr/bin/python
class TableBuilder:
    def __init__(self, headerNames, dictionaryList):
        self.dictionaryList = dictionaryList
        self.headerNames = headerNames

    def printTable(headerNames, dictionaryList, columnLength):
        linebreak = "=" * (sum(columnLength) + len(self.headerNames))
        print linebreak
        for i in range(0, len(self.headerNames)):
            if i == 0:
                print '|%s' % self.headerNames[i].ljust(columnLength[i]),
            elif i == (len(headerNames)-1):
                print '|%s|' % self.headerNames[i].center(columnLength[i])
            else:
                print '|%s' % self.headerNames[i].center(columnLength[i]),
        print linebreak


    def buildTable(headerNames=[], dictionaryList=[] ):
        columnLength = [None] * len(self.headerNames)
        for i in range(0,len(self.headerNames)):
            columnLength[i] = len(self.headerNames[i])+2
            for item in self.dictionaryList:
                strItem = str(item.get(self.headerNames[i]))
                if columnLength[i] < len(strItem):
                    columnLength[i] = len(strItem)+2
        return columnLength