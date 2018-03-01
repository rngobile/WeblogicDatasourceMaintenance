#!/usr/bin/python
def printTable(dictionaryList, headerNames, columnLength):
    linebreak = "=" * (sum(columnLength) + len(headerNames))
    print linebreak
    for i in range(0, len(headerNames)):
        if i == 0:
            print '|%s' % headerNames[i].ljust(columnLength[i]),
        elif i == (len(headerNames)-1):
            print '|%s|' % headerNames[i].center(columnLength[i])
        else:
            print '|%s' % headerNames[i].center(columnLength[i]),
    print linebreak


def buildTable(dictionaryList=[], headerNames=[] ):
    columnLength = [None] * len(headerNames)
    for i in range(0,len(headerNames)):
        columnLength[i] = len(headerNames[i])+2
        for item in dictionaryList:
            strItem = str(item.get(headerNames[i]))
            if columnLength[i] < len(strItem):
                columnLength[i] = len(strItem)+2
    return columnLength

def main():
    dictionaryList = [
        { "name": "Tom", "age": 10, "level": 55, "handle": "tomkinstool"},
        { "name": "Mark", "age": 5, "level": 900, "handle": "markymark"},
        { "name": "Pam", "age": 7, "level": 560, "handle": "pamela_olives"},
        { "name": "Dick", "age": 12, "level": 1000, "handle": "Sup3rL0ngUb3RL33tH@ndl3" }
    ]
    headerNames = ['name','age','level','handle']

    columnLength = buildTable(dictionaryList, headerNames)
    printTable(dictionaryList, headerNames, columnLength)

if __name__ == '__main__':
    main()
