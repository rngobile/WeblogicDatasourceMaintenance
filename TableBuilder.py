#!/usr/bin/python
def buildTable(dictionaryList=[], headerNames=[] ):
    columnLength = [None] * len(headerNames)
    for i in range(0,len(headerNames)):
        columnLength[i] = len(headerNames[i])+2
        for item in dictionaryList:
            strItem = str(item.get(headerNames[i]))
            if columnLength[i] < len(strItem):
                columnLength[i] = len(strItem)+2
    print columnLength
    linebreak = "=" * sum(columnLength)
    print linebreak

def main():
    dictionaryList = [
        {'name': 'Richard','age': 32},
        {'name': 'Kanchalita', 'age': 25},
        {'name': 'Steven', 'age': 27}
    ]
    headerNames = ['name','age']

    buildTable(dictionaryList, headerNames)

if __name__ == '__main__':
    main()
