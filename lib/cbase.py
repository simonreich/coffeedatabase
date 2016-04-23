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
import os.path
import sys
import csv
import datetime


class cbase:
    def __init__(self, filename):
        self.data = [[0 for x in range(0)] for x in range(0)]
        self.header = []
        self.filename = filename
        self.dataBinMonthHeader = [[0 for x in range(0)] for x in range(0)]
        self.dataBinMonth = [[0 for x in range(0)] for x in range(0)]
        self.dataBinYearHeader = [[0 for x in range(0)] for x in range(0)]
        self.dataBinYear = []

        self.fileOpen()



    def fileOpen(self):
        """ Opens a cvs file and loads the data into specific variables: data, header, months.
            filename: Name of file to be opened
            header: If set to False, header will be ignored. If set to True, header will be loaded into self.header.
        """
    
        if not os.path.exists(self.filename):
            print("File " + self.filename + " not found.")
            raise

        # populate data
        self.data = [[0 for x in range(0)] for x in range(0)]

        try:
            f = open(self.filename, 'rt')
            r = csv.reader(f)
        except OSError as err:
            print("OS error: {0}".format(err))
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise
        else:
            counter = 0
            for row in r:
                # first column is always id. Make it int to search faster later on.
                if counter > 0:
                    row[0] = int(row[0])
                self.data.append(row)

                counter += 1

        f.close ()

        # populate header
        self.header = list(self.data[0])
        del self.data[0]

        return 0


    def fileWrite(self):
        """ writes to to a cvs file
        """
        if self.filename == "":
            print("No filename given.")
            raise

        try:
            f = open(self.filename, 'wt')
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
            w.writerow(self.header)
            for row in self.data:
                w.writerow(row)
            f.close ()

        return 0


    def dataCreatemonth(self, year, month):
        """ searches for entry in user database and creates year-month, quadruple if not existant
            year: year to create
            month: month to create
        """

        searchVector = [str(year), str(month)]


        # create result vector for search
        searchFound = list(self.months)
        counter = 0
        for i in searchFound:
            searchFound[counter] = False
            counter += 1

        # search
        counter = 0
        for i in self.months:
            if searchVector == i:
                searchFound[counter] = True
                break
            counter += 1

        # How many occurances were found
        searchCount = 0
        for i in searchFound:
            if i:
                searchCount += 1

        # parse results
        if searchCount > 1:
            print("Multiple Entries found for " + searchVector + ". Your database in " + self.filename + " is corrupt.")
            raise
        elif searchCount == 1:
            return 0
        else:
            self.months.append(searchVector)
            self.header.append(year + "-" + month)
            self.data = [x + [""] for x in self.data]

        # write data changes to file
        fileWrite()

        return 0


    def getRowById (self, rowId):
        """ Returns a row array for given id (entry in column 0 = row[0])
            rowId: Row id as int
        """

        rowId = int(rowId)

        rowFound = False
        row = []
        for r in self.data:
            if int(r[0]) == rowId:
                rowFound = True
                row = list(r)
                break

        if not rowFound:
            print("The id " + str(rowId) + " could not be found in database.")
            raise

        return row


    def getRowByName(self, name, column):
        """ Returns row as array
            name: Name as string.
            column: Column as int
        """

        name = str(name)
        column = int(column)

        nameFound = False
        for row in self.data:
            if row[column] == name:
                nameFound = True
                break

        if not nameFound:
            print("Could not find name: " + str(name) + " in column: " + str(column))
            raise

        # search for multiple entries
        matching = [s for s in self.getColumn(column) if name in s]
        if len(matching) > 1:
            raise NameError("Found user " + str(name) + " text multiple times in name database. Names found: ", matching)

        return row


    def getColumn(self, column):
        """ returns a column data matrix
            column: Column as int
        """
        return [row[column] for row in self.data]


    def getDataBinMonth(self):
        """ bins the user data into months
            Example
            dataBinMonthHeader = [          [2015, 12], [2016, 1], [2016, 2]]
            dataBinMonth       = [[userId1, 5,          0,         6],
                                  [userId2, 9,          8,         8]]
        """
        # create dates
        now = datetime.datetime.now()
        year = int(now.strftime("%Y"))
        month = int(now.strftime("%m"))

        # first, find oldest date and highes user id
        monthOldest = 13
        yearOldest = 2999
        idMax = 0
        for row in self.data:
            row[0] = int(row[0])
            row[1] = int(row[1])
            row[2] = int(row[2])
            if row[1] < yearOldest:
                yearOldest = row[1]
                monthOldest = row[2]
            elif (row[1] == yearOldest) and (row[2] < monthOldest):
                monthOldest = row[2]
            if row[0] > idMax:
                idMax = row[0]

        # create header
        self.dataBinMonthHeader = [[0 for x in range(0)] for x in range(0)]
        monthMin = monthOldest
        monthMax = 0
        yearMin = yearOldest
        yearMax = year+1
        for iYear in range(yearMin, yearMax):
            if iYear == year:
                monthMax = month+1
            else:
                monthMax = 13
            for iMonth in range(monthMin, monthMax):
                self.dataBinMonthHeader.append([iYear, iMonth])
            monthMin = 1

        # create empty database to fill with stuff
        self.dataBinMonth = [[0 for x in range(len(self.dataBinMonthHeader)+1)] for x in range(idMax+1)]
        counter = 0
        for row in self.dataBinMonth:
            row[0] = counter
            counter += 1

        # bin data
        for row in self.data:
            #                                 [year   , month ] + field for id
            column = self.dataBinMonthHeader.index([row[1] , row[2]])+1
            self.dataBinMonth[row[0]][column] += float(row[4])

        return 0


    def getDataBinYear(self):
        """ bins the user data into years
            Example
            dataBinYearHeader = [          2014, 2015, 2016]
            dataBinYear       = [[userId1, 5,    0,    6],
                                 [userId2, 9,    8,    8]]
        """
        # create dates
        now = datetime.datetime.now()
        year = int(now.strftime("%Y"))

        # first, find oldest date and highes user id
        yearOldest = 2999
        idMax = 0
        for row in self.data:
            row[0] = int(row[0])
            row[1] = int(row[1])
            if row[1] < yearOldest:
                yearOldest = row[1]
            if row[0] > idMax:
                idMax = row[0]

        # create header
        self.dataBinYearHeader = [x for x in range(yearOldest, year+1)]

        # create empty database to fill with stuff
        self.dataBinYear = [[0 for x in range(len(self.dataBinYearHeader)+1)] for x in range(idMax+1)]
        counter = 0
        for row in self.dataBinMonth:
            row[0] = counter
            counter += 1

        # bin data
        for row in self.data:
            #                                     year   + field for id
            column = self.dataBinYearHeader.index(row[1])+1
            self.dataBinYear[row[0]][column] += float(row[4])

        return 0


    def getDataBinMonthActive(self, months):
        """ Returns an array of user ids, which were active during the last months. If the database has less months than requested, all existing months are used without raising an error.
            months: Search depth in months as int
        """
        # create dates
        now = datetime.datetime.now()
        year = int(now.strftime("%Y"))
        month = int(now.strftime("%m"))

        months = int(months)

        # check, if database was filled with data
        if len(self.dataBinMonth) == 0:
            self.getDataBinMonth()

        if len(self.dataBinMonth) > 0:
            if len(self.dataBinMonth[0])-1 < months:
                months = len(self.dataBinMonth[0])-1
        else:
            print("Database self.dataBinMonth seems to be empty.")
            raise

        activeIds = []

        # check for activity
        for row in self.dataBinMonth:
            activeRow = False
            for iMonth in range(months):
                if int(row[-1-iMonth]) != 0:
                    activeRow = True

            if activeRow:
                activeIds.append(int(row[0]))

        return activeIds.sort()


    def sortArrayHigh(array, cols):
        """ sort an array by multiple columns, first element is highest
            array: a list of lists (or tuple of tuples) where each inner list 
                   represents a row
            cols:  a list (or tuple) specifying the column numbers to sort by
                   e.g. (1,0) would sort by column 1, then by column 0
        """
        for col in reversed(cols):
            table = sorted(table, key=operator.itemgetter(col))
        table.reverse()
        return table


    def sortArrayLow(array, cols):
        """ sort an array by multiple columns, first element is lowest
            array: a list of lists (or tuple of tuples) where each inner list 
                   represents a row
            cols:  a list (or tuple) specifying the column numbers to sort by
                   e.g. (1,0) would sort by column 1, then by column 0
        """
        for col in reversed(cols):
            table = sorted(table, key=operator.itemgetter(col))
        return table
