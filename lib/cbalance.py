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


from lib import cbase


class cbalance(cbase.cbase):
    def __init__(self, user, payment, price, item):
        self.user = user
        self.payment = payment
        self.price = price
        self.item = item

        self.data = [[0 for x in range(0)] for x in range(0)]
        self.header = []
        self.dataBinMonthHeader = [[0 for x in range(0)] for x in range(0)]
        self.dataBinMonth = [[0 for x in range(0)] for x in range(0)]
        self.dataBinYearHeader = [[0 for x in range(0)] for x in range(0)]
        self.dataBinYear = []

    
    def balanceCompute(self):
        """ Compute the balance
        """
        # create dates
        now = datetime.datetime.now()
        year = int(now.strftime("%Y"))
        month = int(now.strftime("%m"))

        # do precomputations
        self.payment.getDataBinMonth()
        self.price.getDataBinMonth()
        for markclass in self.item.marks:
            markclass.getDataBinMonth()

        # First, find oldest marks
        if len(self.item.marks) == 0:
            print("No marks found in marks database.")
            raise

        # first, find oldest date
        monthOldest = 13
        yearOldest = 2999
        for markclass in self.item.marks:
            for row in markclass.dataBinMonthHeader:
                row[0] = int(row[0])
                row[1] = int(row[1])
                if row[0] < yearOldest:
                    yearOldest = row[0]
                    monthOldest = row[1]
                elif (row[0] == yearOldest) and (row[1] < monthOldest):
                    monthOldest = row[1]

        # find highest id
        idMax = -1
        for row in self.user.data:
            if row[0] > idMax:
                idMax = row[0]
        if idMax == -1:
            print("No active users found in user database")
            raise

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

        # now, fill empty database
        counter = 0
        for _c in self.dataBinMonth:
            for _cDate in self.dataBinMonthHeader:
                # date[0] year
                # date[1] month
                # now, first check marks
                markArray = []
                for markclass in self.item.marks:
                    try:
                        markArray.append(markclass.dataBinMonth[counter][dataBinMonthHeader.index(_cDate)])
                    except:
                        markArray.append(0)

                # next, get prices
                priceArray = []
                for row in self.price.dataBinMonth:
                    try:
                        markArray.append(markclass.dataBinMonth[counter][dataBinMonthHeader.index(_cDate)])
                    except:
                        markArray.append(0)




            counter += 1
