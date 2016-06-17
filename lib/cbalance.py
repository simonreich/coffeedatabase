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

# coffeedatabase
from lib import cbase


class cbalance(cbase.cbase):
    def __init__(self, user, payment, price, item, inactiveMonths, fileTemplateBalanceMonth, fileOutBalanceMonth):
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

        self.inactiveMonths = inactiveMonths

        self.fileTemplateBalanceMonth = fileTemplateBalanceMonth
        self.fileOutBalanceMonth = fileOutBalanceMonth

        # compute balance
        self.getDataBinMonth()

    
    def getDataBinMonth(self):
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
        # we compute +payment - (marks*prices) per id per month
        counter = 0
        for _c in self.dataBinMonth:
            counter1 = 0
            for _cDate in self.dataBinMonthHeader:
                # date[0] year
                # date[1] month
                # now, first check marks
                markArray = []
                for markclass in self.item.marks:
                    try:
                        markArray.append(markclass.dataBinMonth[counter][markclass.dataBinMonthHeader.index(_cDate)+1])
                    except:
                        markArray.append(0)

                # next, get prices
                priceArray = []
                for row in self.price.dataBinMonth:
                    try:
                        priceArray.append(row[self.price.dataBinMonthHeader.index(_cDate)+1])
                    except:
                        priceArray.append(0)

                # get payments
                try:
                    payment = self.payment.dataBinMonth[counter][self.payment.dataBinMonthHeader.index(_cDate)+1]
                except:
                    payment = 0.0;

                #print("ID: ", counter, " Date: ", _cDate, " Marks: ", markArray, " Price: ", priceArray, " Payment: ", payment)

                # sanity checks
                if not len(markArray) == len(priceArray):
                    print("On date year:", _cDate[0], "Month:", _cDate[1], "something weird happened: there are more marks then prices. This should not have happened. Check your databases.")
                    print("Marks:", markArray, "Prices:", priceArray)
                    raise

                counter2 = 0
                for row in markArray:
                    if not int(markArray[counter2]) == 0 and float(priceArray[counter2]) == 0:
                        print("On date year:", _cDate[0], "Month:", _cDate[1], "User Id:", counter, "Name:", self.user.getRowById(counter)[1], "There are marks for item with Id", counter2, "but there is no price information or the price is 0.")
                        print ("")
                        raise
                    counter2 += 1

                                                   # first cell contains user id
                self.dataBinMonth[counter][counter1+1] = payment
                counter2 = 0
                for row in markArray:
                    self.dataBinMonth[counter][counter1+1] -= float(markArray[counter2])*float(priceArray[counter2])
                    counter2 += 1

                counter1 += 1

            counter += 1

        # we need to add up all cells in one row for final balance
        counter = 0
        for row in self.dataBinMonth:
            counter1 = 0
            for cell in row:
                # first cell contains user id, second cell is first cell and does not need to be add up
                if counter1 > 1:
                    self.dataBinMonth[counter][counter1] += float(self.dataBinMonth[counter][counter1-1])
                counter1 += 1
            counter += 1


    def exportMonthPDF(self, year, month, day):
        """ This function exports the balance of year, month to a latex file
            year: year to create
            month: month to create
        """

        year = int(year)
        month = int(month)
        day = int(day)

        # quick sanity check for year
        if not year > 2000:
            print("Year is not in range", year)
            raise
        # quick sanity check for month
        if not month > 0 or not month < 13:
            print("Month is not in range", month)
            raise
        # quick sanity check for day
        if not day > 0 or not day < 32:
            print("Day is not in range", day)
            raise

        # This will hold the balance table
        expT = []
        expT.append("\\begin*{table}[]\n")
        expT.append("  \\centering\n")
        expT.append("  \\begin{tabular}{lrrccr}\n")
        expT.append("    \\toprule\n")
        expT.append("    \\multirow{2}{*}{Name} & balance & \\multirow{2}{*}{Name} & coffee & milk & balance \\\\\n")
        expT.append("                           & old     &                        & 0.42\\euro / cup & 0.08\\euro / \\unit[50]{ml} & " + str(day) + "." + str(month) + "." + str(year))
        expT.append("\n    \\midrule\n")

        # This list holds all our active and auto active users
        userActive = self.user.getIdByStatus("active")

        # Check for auto active users in payment and marks
        userAuto = self.user.getIdByStatus("auto")
        userAutoM = self.payment.getIdDataBinMonthActive(self.inactiveMonths)
        for marks in self.item.marks:
            userAutoT = marks.getIdDataBinMonthActive(self.inactiveMonths)
            userAutoM = userAutoM + userAutoT
        userAutoM = list(set(userAutoM))

        # which user is active in last n months and auto active?
        userAuto = list(set(userAuto).intersection(userAutoM))

        # merge both lists
        userActive = userActive + userAuto

        # remove double entries
        userActive = list(set(userActive))

        # remove inactive users
        userInactive = self.user.getIdByStatus("inactive")
        userInactive = list(set(userActive).intersection(userInactive))
        userActive = [x for x in userActive if x not in userInactive]

        # sort
        userActive.sort()

        counter = 0
        for row in self.dataBinMonth:
            # query user
            user = self.user.getRowById(row[0])

            # user needs to be on list
            if user[0] in userActive:
                # get new balance
                try:
                    balance = self.dataBinMonth[counter][self.dataBinMonthHeader.index([year, month])+1]
                except:
                    print("For user", user[1], "there is no balance information for year", year, "and month", month)
                    raise

                # get old balance
                try:
                    balanceOld = self.dataBinMonth[counter][self.dataBinMonthHeader.index([year, month-1])+1]
                except:
                    print("For user", user[1], "there is no balance information for year", year, "and month", month-1)
                    raise

                # get payments
                try:
                    payment = self.payment.dataBinMonth[counter][self.payment.dataBinMonthHeader.index([year, month])+1]
                except:
                    payment = 0.0;
                if payment == 0.0:
                    payment = ""

                # get marks
                markArray = []
                for markclass in self.item.marks:
                    try:
                        markArray.append(markclass.dataBinMonth[counter][markclass.dataBinMonthHeader.index([year, month])+1])
                    except:
                        markArray.append(0)
                marks = ""
                for _m in markArray:
                    if _m == 0:
                        marks += "& "
                    else:
                        marks += str(_m) + " & "

                expT.append("    " + user[1]+ "&"+ str(balanceOld)+ "&"+ str(payment)+ "&"+ marks)
                expT.append("\n")
                if counter < len(self.dataBinMonth)-1:
                    expT.append("    \\midrule\n")

            counter += 1

        expT.append("    \\bottomrule\n")
        expT.append("  \\end{tabular}\n")
        expT.append("\\end*{table}\n")

        # open file
        template = self.fileOpenTemplate(self.fileTemplateBalanceMonth)

        expD = []
        for row in template:
            if not row.find("<template:balancetable>") == -1:
                for row1 in expT:
                    expD.append(row1)
            else:
                expD.append(row)

        print(expD)

        # write file
        self.fileWriteTemplate( self.fileOutBalanceMonth, expD)


