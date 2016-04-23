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
        self.databinHeader = [[0 for x in range(0)] for x in range(0)]
        self.databinData = [[0 for x in range(0)] for x in range(0)]

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


    def getDatabinMonth(self):
        """ bins the user data into months
            Example
            databinHeader = [          [2015, 12], [2016, 1], [2016, 2]]
            databinData   = [[userId1, 5,          0,         6],
                             [userId2, 9,          8,         8]]
        """

        # create dates
        now = datetime.datetime.now()
        year = int(now.strftime("%Y"))
        month = int(now.strftime("%m"))
        day = int(now.strftime("%d"))

        # first, find oldest date
        monthOldest = 13
        yearOldest = 2999
        for row in self.data:
            row[1] = int(row[1])
            row[2] = int(row[2])
            if row[1] < yearOldest:
                yearOldest = row[1]
                monthOldest = row[2]
            elif (row[1] == yearOldest) and (row[2] < monthOldest):
                monthOldest = row[2]

        # create header
        self.databinHeader = [[0 for x in range(0)] for x in range(0)]
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
                self.databinHeader.append([iYear, iMonth])
            monthMin = 1

        # create empty database to fill with stuff
        idMax = 13
        self.databinData = [[0 for x in range(len(self.databinHeader)+1)] for x in range(idMax+1)]
        counter = 0
        for row in self.databinData:
            row[0] = counter
            counter += 1

        # bin data
        for row in self.databinData:
            print(row)
        for row in self.data:
            self.databinData[row[0]] = 4


        print(self.databinHeader)


        return 0
