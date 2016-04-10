# -*- coding: utf-8 -*-
"""
This file is part of coffeedatabase.

    coffeedatabase is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    coffeedatabase is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with coffeedatabase..  If not, see <http://www.gnu.org/licenses/>.
"""


# system
from datetime import date
from datetime import datetime
import operator
import subprocess
import os.path
import csv
import readline


# Completer Class
# For further reference please see
# https://stackoverflow.com/questions/7821661/how-to-code-autocompletion-in-python
class MyCompleter(object):  # Custom completer

    def __init__(self, options):
        self.options = sorted(options)

    def complete(self, text, state):
        if state == 0:  # on first trigger, build possible matches
            if text:  # cache matches (entries that start with entered text)
                self.matches = [s for s in self.options 
                        if text in s]
            else:  # no text entered, all matches possible
                self.matches = self.options[:]

        # return match indexed by state
        try: 
            return self.matches[state]
        except IndexError:
            return None


def fileOpen(fileName, header=False):
    """ Opens a cvs file. Warning: First line is header and ALWAYS ignored.
        fileName: Name of file to be opened
    """
    data = [[0 for x in range(0)] for x in range(0)]
    
    if not os.path.exists(fileName):
        print("File " + fileName + " not found.")
        raise

    try:
        f = open(fileName, 'rt')
        r = csv.reader(f)
    except OSError as err:
        print("OS error: {0}".format(err))
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise
    else:
        for row in r:
            data.append(row)
        if not header:
            del data[0]
        f.close ()

    return data


def fileWrite(fileName, data):
    """ writes to to a cvs file
        fileName: file name as string
        data: data list to write. Warning: First line must be header!
    """

    try:
        f = open(fileName, 'wt')
        w = csv.writer (f, 
            delimiter=',', 
            quotechar='"', 
            quoting=csv.QUOTE_ALL)
    except OSError as err:
        print("OS error: {0}".format(err))
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise
    else:
        for row in data:
            w.writerow(row)
        f.close ()

    return 0


def fileAppend(fileName, data):
    """ writes to to a cvs file
        fileName: file name as string
        data: data list to write
    """

    dataLoad = [[0 for x in range(0)] for x in range(0)]

    try:
        f = open(fileName, 'rt')
        r = csv.reader(f)
    except OSError as err:
        print("OS error: {0}".format(err))
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise
    else:
        for row in r:
            dataLoad.append(row)

        f.close ()

    if len(dataLoad[0]) == len(data):
        dataLoad.append(data)
    else:
        print("data length does not seem to equal data to append length")
        raise

    fileWrite (fileName, dataLoad)

    return 0


def autocompletion(namelist):
    """ creates an input field with auto completion
        namelist: list of words to use for auto completion
    """

    # load auto completer and create user input
    completer = MyCompleter(namelist)
    readline.set_completer(completer.complete)
    readline.parse_and_bind('tab: complete')

    inputText = input("Input: ")

    nameFound = False
    for row in namelist:
        if row == inputText:
            nameFound = True

    if not nameFound:
        print("Could not find name: " + inputText)
        raise

    # search for multiple entries
    matching = [s for s in userName if inputText in s]
    if len(matching) > 1:
        raise NameError("Found user input text multiple times in name database. Names found: ", matching)

    return inputText


def userdatabaseCreatemonth(fileUser, filePrice, year, month):
    """ searches for entry in user database and creates year-month, quadruple if not existant
        fileName: file name as string
        year: year to create
        month: month to create
    """

    filePrice = year + "/" + month + "/" + filePrice
    dataPrice = fileOpen(filePrice)
    dataU = fileOpen(fileUser, True)

    # create search vector
    item = [year + "-" + month + "-payment"]
    counter = 0
    for row in dataPrice:
        item.append(year + "-" + month + "-" + str(counter))
        counter += 1
    item.append(year + "-" + month + "-balance")

    # create result vector for search
    itemFound = list(item)
    counter = 0
    for i in itemFound:
        itemFound[counter] = False
        counter += 1

    # search
    counter = 0
    for i in item:
        for cell in dataU[0]:
            if cell == i:
                itemFound[counter] = True
                break
        counter += 1

    # How many occurances were found
    counter = 0
    for i in itemFound:
        if i:
           counter += 1

    if counter == len(itemFound):
        return 0        # all items were found
    elif counter == 0:
        for i in item:      # no items were found
            dataU = [x + [""] for x in dataU]
            dataU[0][-1] = i
    else:
        print("The user database seems to be corrupt. Fix it manually. Items that are missing in some order:")
        counter = 0
        for i in itemFound:
            if not itemFound:
                print(item[counter])
            counter += 1
        raise

    fileWrite(fileUser, dataU)

    return 0


    # no column found, add a new one
    if not cellFound:
        dataU[0][-1] = cellStr
        cellNr = -1
    return 0


def column(matrix, i):
    """ returns a column from matrix
        matrix: simple 2d array
        i: column to extract
    """
    return [row[i] for row in matrix]


def sort_table_high(table, cols):
    """ sort a table by multiple columns, first element is highest
        table: a list of lists (or tuple of tuples) where each inner list 
               represents a row
        cols:  a list (or tuple) specifying the column numbers to sort by
               e.g. (1,0) would sort by column 1, then by column 0
    """
    for col in reversed(cols):
        table = sorted(table, key=operator.itemgetter(col))
    table.reverse()
    return table


def sort_table_low(table, cols):
    """ sort a table by multiple columns, first element is lowest
        table: a list of lists (or tuple of tuples) where each inner list 
               represents a row
        cols:  a list (or tuple) specifying the column numbers to sort by
               e.g. (1,0) would sort by column 1, then by column 0
    """
    for col in reversed(cols):
        table = sorted(table, key=operator.itemgetter(col))
    return table


