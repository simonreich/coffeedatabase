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
import datetime

#coffeedatabase
from lib import cbase


class cprice(cbase.cbase):
    def __init__(self, filename, item):
        super().__init__(filename)
        self.item = item

        self.getDataBinMonth()
        self.fillDataBin()


    def priceAdd(self, price):
        """ Adds a price to the price database
            price: Price as array ["Id", "Year", "Month", "Day", "Price"].
        """

        if not len(price) == 5:
            print("The given price array has wrong format ([\"Id\", \"Year\", \"Month\", \"Day\", \"Price\"]): ", price)
            raise

        price[0] = int(price[0])
        price[1] = int(price[1])
        price[2] = int(price[2])
        price[3] = int(price[3])
        price[4] = "{:.2f}".format(float(price[4]))

        # check if id exists
        item = self.item.getRowById(price[0])

        # quick sanity check for year
        if not price[1] > 2000:
            print("Year is not in range", price)
            raise
        # quick sanity check for month
        if not price[2] > 0 or not price[2] < 13:
            print("Month is not in range", price)
            raise
        # quick sanity check for day
        if not price[3] > 0 or not price[3] < 32:
            print("Day is not in range", price)
            raise

        self.data.append(price)
        self.checkDouble()
        self.fileWrite()

        return 0


    def checkDouble(self):
        """ Checks, if for one month a double price has been entered
        """

        # create dates
        now = datetime.datetime.now()
        year = int(now.strftime("%Y"))
        month = int(now.strftime("%m"))

        # first, find oldest date and highest user id
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

        # create empty database to fill with stuff
        #dataBinMonth = [[-1 for x in range(((yearOldest-year-1)*12) + (month) + (12-monthOldest))] for x in range(idMax+1)]
        #counter = 0
        #for row in self.dataBinMonth:
        #    row[0] = counter
        #    counter += 1
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
        self.dataBinMonth = [[-1 for x in range(len(self.dataBinMonthHeader)+1)] for x in range(idMax+1)]
        counter = 0
        for row in self.dataBinMonth:
            row[0] = counter
            counter += 1

        # bin data
        for row in self.data:
            #                                      [year   , month ] + field for id
            column = self.dataBinMonthHeader.index([row[1] , row[2]])+1
            if self.dataBinMonth[row[0]][column] == -1:
                if float(row[4]) == 0.0:
                    self.dataBinMonth[row[0]][column] = 0
                else:
                    self.dataBinMonth[row[0]][column] += float(row[4])
            else:
                print("There is a double entry in the price database for item id ", row)
                print("Item Id: ", row[0])
                print("Year: ", row[1])
                print("Month: ", row[2])
                raise

        return 0


    def fillDataBin(self):
        """ self.dataBinMonthHeader, self.dataBinMonth, self.dataBinYearHeader, self.dataBinYear are sparse. Fill them with the last value
        """

        for row in self.dataBinMonth:
            counter = 0
            priceOld = 0.0
            for cell in row:
                if counter == 1:
                    priceOld = float(cell)
                if counter > 1:
                    if float(cell) == 0.0:
                        row[counter] = float(priceOld)
                    else:
                        priceOld = float(cell)
                counter += 1
