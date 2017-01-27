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
from operator import itemgetter
import copy
import numpy as np

# coffeedatabase
from lib import cbase


class cbalance(cbase.cbase):
    def __init__(self, user, payment, price, item, inactiveMonths, fileTemplateBalanceMonth, fileOutBalanceMonth, fileTemplateListMonth, fileOutListMonth, fileOutFolder):
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
        self.fileTemplateListMonth = fileTemplateListMonth
        self.fileOutListMonth = fileOutListMonth
        self.fileOutFolder = fileOutFolder

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
        #self.price.getDataBinMonth()       #price is already loaded. getDataBinMonth() create only sparse database.
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

        # next, find oldest payments
        for row in self.payment.dataBinMonthHeader:
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
                    payment = float(self.payment.dataBinMonth[counter][self.payment.dataBinMonthHeader.index(_cDate)+1])
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
                    self.dataBinMonth[counter][counter1+1] -= float("{0:.2f}".format(float(markArray[counter2])*float(priceArray[counter2])))
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

        # This list holds all our active and auto active users
        userActive = self.getAcitvatedUser ()

        # Create an array, which will hold all our balance data as [id, old balance, payment, new balance, marks]. This will allow us to sort
        userActiveBalance = [[0 for x in range(0)] for x in range(0)]
        counter = 0
        for row in self.dataBinMonth:
            # query user
            user = self.user.getRowById(row[0])

            userActiveBalanceRow = []
            # user needs to be on list
            if user[0] in userActive:
                userActiveBalanceRow = [user[0]]

                # compute old date
                monthOld = month-1
                yearOld = year
                monthOld2 = month-2
                yearOld2 = year
                if monthOld == 0:
                    yearOld = year - 1
                    monthOld = 12
                if monthOld2 == 0:
                    yearOld2 = year - 1
                    monthOld2 = 12
                elif monthOld2 == -1:
                    yearOld2 = year - 1
                    monthOld2 = 11

                # get old balance
                try:
                    balanceOld = self.dataBinMonth[counter][self.dataBinMonthHeader.index([yearOld2, monthOld2])+1]
                except:
                    print("For user", user[1], "there is no balance information for year", yearOld, "and month", monthOld)
                    raise
                userActiveBalanceRow.append(float(balanceOld))

                # get payments
                try:
                    payment = self.payment.dataBinMonth[counter][self.payment.dataBinMonthHeader.index([yearOld, monthOld])+1]
                except:
                    payment = 0.0;
                userActiveBalanceRow.append(float(payment))

                # get new balance
                try:
                    balanceNew = self.dataBinMonth[counter][self.dataBinMonthHeader.index([year, month])+1]
                except:
                    print("For user", user[1], "there is no balance information for year", year, "and month", month)
                    raise
                userActiveBalanceRow.append(float(balanceNew))

                # get marks
                markArray = []
                for markclass in self.item.marks:
                    try:
                        markArray.append(markclass.dataBinMonth[counter][markclass.dataBinMonthHeader.index([yearOld, monthOld])+1])
                    except:
                        markArray.append(0)
                for _m in markArray:
                    userActiveBalanceRow.append(float(_m))

                userActiveBalance.append(userActiveBalanceRow)
            counter += 1

        self.userActiveBalance = userActiveBalance


        # This will hold the balance table
        expT = []
        expT.append("\\begin{longtable}{lrr")
        # Add all items
        for _item in self.item.data:
            if _item[3] == "active":
                expT.append("c")
        expT.append("r}\n")
        expT.append("  \\toprule\n")
        expT.append("  \\multicolumn{1}{c}{\\multirow{2}{*}{Name}} & \\multicolumn{1}{c}{\\multirow{2}{*}{Balance old}} & \\multicolumn{1}{c}{\\multirow{2}{*}{Payment}} & ")
        # Add all items
        for _item in self.item.data:
            if _item[3] == "active":
                expT.append(_item[1] + " & ")
        expT.append(" \\multicolumn{1}{c}{Balance}\\\\\n")
        expT.append("                         &                               &         & ")
        # Add all items
        for _item in self.item.data:
            if _item[3] == "active":
                p = self.price.getDataBinMonthByDate(_item[0],  int(year), int(month))
                expT.append("\\unit[" + str("{:.2f}".format(p)) + "]{\euro} " + _item[2] + " & ")
        expT.append(str(day) + "." + str(month) + "." + str(year) + "\\\\")
        expT.append("\n  \\midrule\n")

        # sort by highest debt
        userActiveBalance = sorted(userActiveBalance, key=itemgetter(3))

        counter = 0
        for row in userActiveBalance:
            # get old balance
            if float(row[1]) < 0:
                balanceOld = "\\textcolor{red}{\\unit[" + str("{0:.2f}".format(row[1])) + "]{\euro}}"
            else:
                balanceOld = "\\unit[" + str("{0:.2f}".format(row[1])) + "]{\euro}"

            # get payments
            if float(row[2]) < 0:
                payment = "\\textcolor{red}{\\unit[" + str("{0:.2f}".format(row[2])) + "]{\euro}}"
            elif float(row[2]) == 0:
                payment = ""
            else:
                payment = "\\unit[" + str("{0:.2f}".format(row[2])) + "]{\euro}"

            # get new balance
            if float(row[3]) < 0:
                balanceNew = "\\textcolor{red}{\\unit[" + str("{0:.2f}".format(row[3])) + "]{\euro}}"
            else:
                balanceNew = "\\unit[" + str("{0:.2f}".format(row[3])) + "]{\euro}"

            # get marks
            marks = ""
            for _m in range(len(row)-4):
                if row[_m+4] == 0:
                    marks += "& "
                else:
                    marks += str("{0:.0f}".format(row[_m+4])) + " & "

            expT.append("    " + self.user.getRowById(row[0])[1] + " & "+ str(balanceOld) + " & "+ str(payment) + " & " + marks + balanceNew)
            expT.append("\\\\\n")
            if counter < len(userActive)-1:
                expT.append("    \\midrule\n")

            counter += 1
        expT.append("  \\bottomrule\n")
        expT.append("\\end{longtable}\n")


        # Create Month template
        expM = "\lhead{" + datetime.date(1900, monthOld, 1).strftime('%B') + " " + str(yearOld) + "}"


        # Compute total consumption of all items
        expS = []
        expS.append("\\begin{longtable}{lc}\n")
        expS.append("  \\toprule\n")
        expS.append("  & Total Sum\\\\\n")
        expS.append("  \\midrule\n")

        if len(userActiveBalance) == 0:
            print("It seems that the current balance is empty.")
            raise

        sumTotal = [0 for x in range(len(userActiveBalance[0]))]
        for row in userActiveBalance:
            for _m in range(len(row)):
                sumTotal[_m] += row[_m]

        counter = 0
        for _item in self.item.data:
            if _item[3] == "active":
                expS.append("    " + _item[1] + " & " + str("{0:.0f}".format(sumTotal[counter+4])) + "\\\\\n")
                if counter < len(self.item.data)-1:
                    expS.append("    \\midrule\n")

            counter += 1
        expS.append("  \\bottomrule\n")
        expS.append("\\end{longtable}\n")


        # Create Coffee King template - this does not generalize very well...
        expC = []
        expC.append("\\begin{longtable}{clc}\n")
        expC.append("  \\toprule\n")
        expC.append("  & Name & Coffee\\\\\n")
        expC.append("  \\midrule\n")

        # sort by highest coffee
        userActiveCoffeeking = sorted(userActiveBalance, key=itemgetter(4))
        userActiveCoffeeking.reverse ()

        if len(userActiveCoffeeking) > 3:
            userActiveCoffeeking = userActiveCoffeeking[0:3]

        counter = 0
        sum = 0
        for row in userActiveCoffeeking:
            marks = str("{0:.0f}".format(row[4]))
            expC.append("    " + str(counter+1) + ". & " + self.user.getRowById(row[0])[1] + " & " + marks + " (" + str("{0:.1f}".format(100/float(sumTotal[4])*float(row[4]))) + "\%)\\\\\n")
            expC.append("    \\midrule\n")
            sum += float(row[4])

            counter += 1

        expC.append("    & Sum & " + str("{0:.0f}".format(sum)) + " (" + str("{0:.1f}".format(100/float(sumTotal[4])*float(sum))) + "\%)\\\\\n")
        expC.append("  \\bottomrule\n")
        expC.append("\\end{longtable}\n")


        # Create Dairy Queen template - this does not generalize very well...
        expD = []
        expD.append("\\begin{longtable}{clc}\n")
        expD.append("  \\toprule\n")
        expD.append("  & Name & Milk\\\\\n")
        expD.append("  \\midrule\n")

        # sort by highest coffee
        userActiveDairyqueen = sorted(userActiveBalance, key=itemgetter(5))
        userActiveDairyqueen.reverse ()

        if len(userActiveDairyqueen) > 3:
            userActiveDairyqueen = userActiveDairyqueen[0:3]

        counter = 0
        sum = 0
        for row in userActiveDairyqueen:
            marks = str("{0:.0f}".format(row[5]))
            expD.append("    " + str(counter+1) + ". & " + self.user.getRowById(row[0])[1] + " & " + marks + " (" + str("{0:.1f}".format(100/float(sumTotal[5])*float(row[4]))) + "\%)\\\\\n")
            expD.append("    \\midrule\n")
            sum += float(row[5])

            counter += 1

        expD.append("    & Sum & " + str("{0:.0f}".format(sum)) + " (" + str("{0:.1f}".format(100/float(sumTotal[5])*float(sum))) + "\%)\\\\\n")
        expD.append("  \\bottomrule\n")
        expD.append("\\end{longtable}\n")


        # open file
        template = self.fileOpenTemplate(self.fileTemplateBalanceMonth)

        expL = []
        for row in template:
            if not row.find("<template:balancetable>") == -1:
                for row1 in expT:
                    expL.append(row1)
            elif not row.find("<template:month>") == -1:
                expL.append(expM)
            elif not row.find("<template:coffeeking>") == -1:
                for row1 in expC:
                    expL.append(row1)
            elif not row.find("<template:dairyqueen>") == -1:
                for row1 in expD:
                    expL.append(row1)
            elif not row.find("<template:totalsum>") == -1:
                for row1 in expS:
                    expL.append(row1)
            else:
                expL.append(row)

        # write file
        self.fileWriteTemplate( self.fileOutBalanceMonth + str(year) + "-" + str(month) + "-" + str(day) + ".tex", expL)


        # create crazy statistics
        self.getStatistics(year, month, day)


    def exportMonthListPDF(self, year, month, day):
        """ This function exports the list of names of year, month to a latex file
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

        # compute old date
        monthOld = month-1
        yearOld = year
        monthOld2 = month-2
        yearOld2 = year
        if monthOld == 0:
            yearOld = year - 1
            monthOld = 12


        # This list holds all our active and auto active users
        userActive = self.getAcitvatedUser ()


        # This will hold the list table
        expT = []
        expT.append("\\begin{longtable}{l")
        # Add all items
        for _item in self.item.data:
            if _item[3] == "active":
                expT.append("|p{5.5cm}")
        expT.append("}\n")
        expT.append("  \\toprule\n")
        expT.append("  \\multicolumn{1}{c}{Name} ")
        # Add all items
        itemPlaceholder = ""
        for _item in self.item.data:
            if _item[3] == "active":
                expT.append(" & \\multicolumn{1}{c}{" + _item[1] + "}")
                itemPlaceholder += "& "
        expT.append("\\\\\n  \\midrule\n")

        counter = 0
        for row in userActive:
            expT.append("    " + self.user.getRowById(row)[1] + itemPlaceholder + "\\vspace{0.72cm}\\\\\n")
            if counter < len(userActive)-1:
                expT.append("    \\midrule\n")

            counter += 1
        expT.append("  \\bottomrule\n")
        expT.append("\\end{longtable}\n")


        # Create Month template
        expM = "\lhead{" + datetime.date(1900, monthOld, 1).strftime('%B') + " " + str(yearOld) + "}"


        # open file
        template = self.fileOpenTemplate(self.fileTemplateListMonth)

        expL = []
        for row in template:
            if not row.find("<template:listtable>") == -1:
                for row1 in expT:
                    expL.append(row1)
            elif not row.find("<template:month>") == -1:
                expL.append(expM)
            else:
                expL.append(row)

        # write file
        self.fileWriteTemplate( self.fileOutListMonth + str(year) + "-" + str(month) + "-" + str(day) + ".tex", expL)


    def getAcitvatedUser (self):
        """ Returns array of ids with status either (active) or (auto and active within inactiveMonths)
            status: Status as string: active, inactive, or auto
        """

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

        return userActive


    def getStatistics (self, year, month, day):
        """ Creates tons of crazy statistics to use with gnuplot
            year: year to create
            month: month to create
        """

        year = int(year)
        month = int(month)

        # quick sanity check for year
        if not year > 2000:
            print("Year is not in range", year)
            raise
        # quick sanity check for month
        if not month > 0 or not month < 13:
            print("Month is not in range", month)
            raise

        # compute old date
        monthOld = month-1
        yearOld = year
        if monthOld == 0:
            yearOld = year - 1
            monthOld = 12

        # Compute total consumption
        markSum = [[0 for x in range(0)] for x in range(0)]
        for _markclass in self.item.marks:
            markSumRow = [0 for x in range(len(self.item.marks[0].dataBinMonthHeader))]
            for _marks in _markclass.dataBinMonth:
                # add all vectors
                markSumRow = [sum(x) for x in zip(markSumRow, _marks)]
            # remove ids
            del markSumRow[0]
            markSum.append(markSumRow)

        # get marks
        markArrayH = []
        for _markclass in self.item.marks:
            markArrayH = copy.deepcopy(_markclass.dataBinMonthHeader)


        ######################################################
        # Months vs. Total Item Consumption

        expMonthsVsTotalitem = []
        for _row in markArrayH:
            expMonthsVsTotalitem.append(str(_row[0]) + "-" + str("{0:02d}".format(_row[1])))
        expMonthsVsTotalitem = [expMonthsVsTotalitem] + markSum
        del expMonthsVsTotalitem[0][-1]

        expMonthsVsTotalitem = self.getTranspose(expMonthsVsTotalitem)
        expMonthsVsTotalitem_t = []
        for _row in expMonthsVsTotalitem:
            for _row1 in _row:
                expMonthsVsTotalitem_t.append(str(_row1) + "\t")
            expMonthsVsTotalitem_t.append("\n")

        # write file
        self.fileWriteTemplate( self.fileOutFolder + "/month-totalitem.dat", expMonthsVsTotalitem_t)


        ######################################################
        # Coffee King and Dairy Queen

        markArray = [[0 for x in range(0)] for x in range(0)]
        for _markclass in self.item.marks:
            markArray.append(copy.deepcopy(_markclass.dataBinMonth))

        # markMax
        # [item [month [id, value]]]
        markMax = [[[0 for x in range(0)] for x in range(0)] for x in range(0)]
        for _item in markArray:
            _item = self.getTranspose(_item)
            # remove ids
            del _item[0]
            # remove last month
            del _item[-1]

            markMaxMonth = [[0 for x in range(0)] for x in range(0)]
            for _month in _item:
                max_value = max(_month)
                max_index = _month.index(max_value)
                markMaxMonth.append([max_index, max_value])

            markMax.append(markMaxMonth)

        # Compute Histogram
        markMaxHistogram = [[0 for x in range(len(self.user.data))] for x in range(len(markMax))]
        counter = 0
        for _item in markMax:
            for month in _item:
                markMaxHistogram[counter][month[0]] += 1
            counter += 1

        #for _item in markMax:
        #    counter = 0
        #    for month in _item:
        #        print(markArrayH[counter], month, self.user.getRowById(month[0]))
        #        counter += 1

        #for _user in self.user.data:
        #    print(_user, markMaxHistogram[0][_user[0]], markMaxHistogram[1][_user[0]])


        ######################################################
        # Person vs. Consumption

        # get marks
        markPerson = [[0 for x in range(0)] for x in range(0)]
        userActive = self.getAcitvatedUser ()
        for _counter in range(0, len(self.dataBinMonth)):
            user = self.user.getRowById(_counter)

            # get marks
            markArray = []
            for _markclass in self.item.marks:
                markArray.append(copy.deepcopy(_markclass.dataBinMonth[_counter]))
                del markArray[-1][0]
            if _counter in userActive:
                markPerson.append([user[1], markArray[0][-2], markArray[1][-2]])

        # sort by coffee/milk
        markPerson1 = sorted(markPerson, key=itemgetter(1), reverse=True)
        markPerson2 = sorted(markPerson, key=itemgetter(2), reverse=True)

        # write file
        expPersonVsConsumption = []
        for _row in markPerson1:
            expPersonVsConsumption.append("\"" + str(_row[0]) + "\" " + str(_row[1]) + "\n")
        self.fileWriteTemplate( self.fileOutFolder + "/person-consumption-0.dat", expPersonVsConsumption)
        expPersonVsConsumption = []
        for _row in markPerson2:
            expPersonVsConsumption.append("\"" + str(_row[0]) + "\" " + str(_row[2]) + "\n")
        self.fileWriteTemplate( self.fileOutFolder + "/person-consumption-1.dat", expPersonVsConsumption)

        # create histogram
        markPersonHist1 = []
        markPersonEdges1 = []
        counter = -4.5
        for _row in markPerson1:
            markPersonHist1.append(_row[1])
            markPersonEdges1.append(counter)
            counter += 5
        markPersonHist2 = []
        markPersonEdges2 = []
        counter = -4.5
        for _row in markPerson2:
            markPersonHist2.append(_row[2])
            markPersonEdges2.append(counter)
            counter += 5

        [markPersonHist1, markPersonHistEdges1] = np.histogram(markPersonHist1, markPersonEdges1)
        [markPersonHist2, markPersonHistEdges2] = np.histogram(markPersonHist2, markPersonEdges2)

        for _counter in range(len(markPersonHist1)-1, 0, -1):
            if markPersonHist1[_counter] == 0:
                markPersonHist1 = np.delete(markPersonHist1, _counter)
                markPersonHistEdges1 = np.delete(markPersonHistEdges1, _counter)
            else:
                break
        for _counter in range(len(markPersonHist2)-1, 0, -1):
            if markPersonHist2[_counter] == 0:
                markPersonHist2 = np.delete(markPersonHist2, _counter)
                markPersonHistEdges2 = np.delete(markPersonHistEdges2, _counter)
            else:
                break

        # write file
        expPersonVsConsumption = []
        counter = 0
        for _row in zip(markPersonHist1, markPersonHistEdges1):
            if counter == 0:
                expPersonVsConsumption.append("\"0\" " + str(_row[0]) + "\n")
            else:
                expPersonVsConsumption.append("\"" + str(int(_row[1])) + " < n ≤ " + str(int(_row[1]+5)) + "\" " + str(_row[0]) + "\n")
            counter += 1
        self.fileWriteTemplate( self.fileOutFolder + "/person-consumption-hist-0.dat", expPersonVsConsumption)
        expPersonVsConsumption = []
        counter = 0
        for _row in zip(markPersonHist2, markPersonHistEdges2):
            if counter == 0:
                expPersonVsConsumption.append("\"0\" " + str(_row[0]) + "\n")
            else:
                expPersonVsConsumption.append("\"" + str(int(_row[1])) + " < n ≤ " + str(int(_row[1]+5)) + "\" " + str(_row[0]) + "\n")
            counter += 1
        self.fileWriteTemplate( self.fileOutFolder + "/person-consumption-hist-1.dat", expPersonVsConsumption)


        ######################################################
        # Create a gnuplot script

        expGnuplot = []
        expGnuplot.append("reset\n")
        expGnuplot.append("set terminal png size 1024,768\n")
        expGnuplot.append("set grid\n")
        expGnuplot.append("set xlabel \' '\n")
        expGnuplot.append("set ylabel \' \'\n")
        expGnuplot.append("set xtics nomirror\n")
        expGnuplot.append("set ytics nomirror\n")
        expGnuplot.append("set style line 1 lc rgb \'#AA0000\' lt 1 lw 2 pt 1 ps 1.5\n")
        expGnuplot.append("set style line 2 lc rgb \'#0000AA\' lt 2 lw 2 pt 2 ps 1.5\n")
        expGnuplot.append("set style line 3 lc rgb \'#00AA00\' lt 3 lw 2 pt 3 ps 1.5\n")
        expGnuplot.append("set style line 11 lc rgb \'#ff8d2a\' lt 1 lw 2 pt 1 ps 1.5\n")
        expGnuplot.append("set style line 12 lc rgb \'#31e2ff\' lt 2 lw 2 pt 2 ps 1.5\n")
        expGnuplot.append("\n")
        expGnuplot.append("\n")
        expGnuplot.append("set xtics rotate by 60 offset -2,-2.5\n")
        expGnuplot.append("set style fill solid\n")
        expGnuplot.append("set output 'month-totalitem.png\'\n")
        expGnuplot.append("set ylabel \'Consumption\'\n")
        expGnuplot.append("set yrange[0:*]\n")
        expGnuplot.append("set boxwidth 0.8\n")
        expGnuplot.append("set style data histogram\n")
        expGnuplot.append("set style histogram clustered gap 1\n")
        expGnuplot.append("set key inside right top box opaque\n")
        expGnuplot.append("everyfifth(col) = ((int(column(col)) % 2 == 0) ? stringcolumn(1) : \'\')\n")
        expGnuplot.append("plot \'month-totalitem.dat\' using 2:xticlabel((everyfifth(0))) ls 1 ti \'Coffee\', \'\' u 3 ls 2 ti \'Milk\'\n")
        expGnuplot.append("\n")
        expGnuplot.append("\n")
        expGnuplot.append("set output \'person-consumption-0.png\'\n")
        expGnuplot.append("set multiplot\n")
        expGnuplot.append("set nogrid\n")
        expGnuplot.append("set xtics rotate by 60 offset 0.2,0.1 right\n")
        expGnuplot.append("set xtics font \', 10\'\n")
        expGnuplot.append("set xlabel \'\'\n")
        expGnuplot.append("set ylabel \'Consumption\'\n")
        expGnuplot.append("set title \'\'\n")
        expGnuplot.append("set bmargin 8.5\n")
        expGnuplot.append("plot \'person-consumption-0.dat\' using 2:xticlabel(1) ls 1 ti \'Coffee\'\n")
        expGnuplot.append("\n")
        expGnuplot.append("set grid\n")
        expGnuplot.append("set xtics rotate by 60 offset 0.2,0.1 right\n")
        expGnuplot.append("set xtics font \', 12\'\n")
        expGnuplot.append("set xlabel \'\'\n")
        expGnuplot.append("set ylabel \'People\'\n")
        expGnuplot.append("set title \'Histogram\'\n")
        expGnuplot.append("set bmargin 4.5\n")
        expGnuplot.append("set size 0.5, 0.5\n")
        expGnuplot.append("set origin 0.48,0.46\n")
        expGnuplot.append("set nokey\n")
        expGnuplot.append("set object 1 rectangle from graph 0,0 to graph 1,1 behind fillcolor rgb \'white\' fillstyle solid noborder\n")
        expGnuplot.append("plot 'person-consumption-hist-0.dat' using 2:xticlabel(1) ls 1 ti \'\'\n")
        expGnuplot.append("unset multiplot\n")
        expGnuplot.append("\n")
        expGnuplot.append("\n")
        expGnuplot.append("set output \'person-consumption-1.png\'\n")
        expGnuplot.append("set multiplot\n")
        expGnuplot.append("set nogrid\n")
        expGnuplot.append("set xtics rotate by 60 offset 0.2,0.1 right\n")
        expGnuplot.append("set xtics font \', 10\'\n")
        expGnuplot.append("set xlabel \'\'\n")
        expGnuplot.append("set ylabel \'Consumption\'\n")
        expGnuplot.append("set title \'\'\n")
        expGnuplot.append("set bmargin 8.5\n")
        expGnuplot.append("set size 1,1\n")
        expGnuplot.append("set origin 0,0\n")
        expGnuplot.append("set key inside right top box opaque\n")
        expGnuplot.append("plot \'person-consumption-1.dat\' using 2:xticlabel(1) ls 2 ti \'Milk\'\n")
        expGnuplot.append("\n")
        expGnuplot.append("set grid\n")
        expGnuplot.append("set xtics rotate by 60 offset 0.2,0.1 right\n")
        expGnuplot.append("set xtics font \', 12\'\n")
        expGnuplot.append("set xlabel \'\'\n")
        expGnuplot.append("set ylabel \'People\'\n")
        expGnuplot.append("set title \'Histogram\'\n")
        expGnuplot.append("set bmargin 4.5\n")
        expGnuplot.append("set size 0.5, 0.5\n")
        expGnuplot.append("set origin 0.48,0.46\n")
        expGnuplot.append("set nokey\n")
        expGnuplot.append("set object 1 rectangle from graph 0,0 to graph 1,1 behind fillcolor rgb \'white\' fillstyle solid noborder\n")
        expGnuplot.append("plot 'person-consumption-hist-1.dat' using 2:xticlabel(1) ls 2 ti \'\'\n")
        expGnuplot.append("unset multiplot\n")

        # write file
        self.fileWriteTemplate( self.fileOutFolder + "/all.plot", expGnuplot)


        # loop through all users
        for _counter in range(0, len(self.dataBinMonth)):
            user = self.user.getRowById(_counter)
            paymentH = copy.deepcopy(self.payment.dataBinMonthHeader)
            payment = copy.deepcopy(self.payment.dataBinMonth[_counter])
            del payment[0]
            balanceH = copy.deepcopy(self.dataBinMonthHeader)
            balance = copy.deepcopy(self.dataBinMonth[_counter])
            del balance[0]

            # get marks
            markArray = []
            markArrayH = []
            for _markclass in self.item.marks:
                markArray.append(copy.deepcopy(_markclass.dataBinMonth[_counter]))
                del markArray[-1][0]
                markArrayH = copy.deepcopy(_markclass.dataBinMonthHeader)


            ######################################################
            # Months vs. Item Consumption

            expMonthsVsItem = []
            for _row in markArrayH:
                expMonthsVsItem.append(str(_row[0]) + "-" + str("{0:02d}".format(_row[1])))
            expMonthsVsItem = [expMonthsVsItem] + markArray

            expMonthsVsItem = self.getTranspose(expMonthsVsItem)
            expMonthsVsItem_t = []
            for _row in expMonthsVsItem:
                for _row1 in _row:
                    expMonthsVsItem_t.append(str(_row1) + "\t")
                expMonthsVsItem_t.append("\n")

            # write file
            self.fileWriteTemplate( self.fileOutFolder + "/month-item_" + str(user[0]) + ".dat", expMonthsVsItem_t)


            ######################################################
            # Months vs. Payment

            expMonthsVsPayment = []
            for _row in zip(paymentH, payment):
                expMonthsVsPayment.append(str(_row[0][0])+ "-" + str("{0:02d}".format(_row[0][1])) + "\t" + str(_row[1]) + "\n")

            # write file
            self.fileWriteTemplate( self.fileOutFolder + "/month-payment_" + str(user[0]) + ".dat", expMonthsVsPayment)


            ######################################################
            # Months vs. Balance

            expMonthsVsBalance = []
            for _row in zip(balanceH, balance):
                expMonthsVsBalance.append(str(_row[0][0])+ "-" + str("{0:02d}".format(_row[0][1])) + "\t" + str("{:.2f}".format(_row[1])) + "\n")

            # write file
            self.fileWriteTemplate( self.fileOutFolder + "/month-balance_" + str(user[0]) + ".dat", expMonthsVsBalance)


            ######################################################
            # Percentage of Consumption

            marksConsumption = []
            for _marks in markArray:
                marksConsumption.append(_marks[markArrayH.index([yearOld, monthOld])])

            counter = 0
            for _row in zip(markSum, marksConsumption):
                expPercentage = [str(counter) + "\t" + str("{:.2f}".format(1-(1/float(_row[0][markArrayH.index([yearOld, monthOld])-1])*float(_row[1])))) + "\t" + str("{:.2f}".format(1/float(_row[0][markArrayH.index([yearOld, monthOld])-1])*float(_row[1]))) + "\n"]
                # write file
                self.fileWriteTemplate( self.fileOutFolder + "/percentage-" + str(counter) + "_" + str(user[0]) + ".dat", expPercentage)
                counter += 1


            ######################################################
            # Create a gnuplot script

            expGnuplot = []
            expGnuplot.append("reset\n")
            expGnuplot.append("set terminal png size 1024,768\n")
            expGnuplot.append("set grid\n")
            expGnuplot.append("set xlabel \' '\n")
            expGnuplot.append("set ylabel \' \'\n")
            expGnuplot.append("set xtics nomirror\n")
            expGnuplot.append("set ytics nomirror\n")
            expGnuplot.append("set style line 1 lc rgb \'#AA0000\' lt 1 lw 2 pt 1 ps 1.5\n")
            expGnuplot.append("set style line 2 lc rgb \'#0000AA\' lt 2 lw 2 pt 2 ps 1.5\n")
            expGnuplot.append("set style line 3 lc rgb \'#00AA00\' lt 3 lw 2 pt 3 ps 1.5\n")
            expGnuplot.append("set style line 11 lc rgb \'#ff8d2a\' lt 1 lw 2 pt 1 ps 1.5\n")
            expGnuplot.append("set style line 12 lc rgb \'#31e2ff\' lt 2 lw 2 pt 2 ps 1.5\n")
            expGnuplot.append("\n")
            expGnuplot.append("\n")
            expGnuplot.append("set output \'month-balance_" + str(user[0]) + ".png\'\n")
            expGnuplot.append("set timefmt \'%Y-%m\'\n")
            expGnuplot.append("set xdata time\n")
            expGnuplot.append("set format x \'%Y-%m\'\n")
            expGnuplot.append("set xtics rotate by 60 offset -2,-2.5\n")
            expGnuplot.append("set style histogram\n")
            expGnuplot.append("set style data histogram\n")
            expGnuplot.append("set style fill solid\n")
            expGnuplot.append("set ylabel \'Balance [€]\'\n")
            expGnuplot.append("plot \'month-balance_" + str(user[0]) + ".dat\' using 1:2:($2 >= 0 ? 0x00AA00 : 0xAA0000) ti \'\' linecolor rgb variable w boxes\n")
            expGnuplot.append("\n")
            expGnuplot.append("\n")
            expGnuplot.append("set output \'month-payment_" + str(user[0]) + ".png\'\n")
            expGnuplot.append("set ylabel \'Payment [€]\'\n")
            expGnuplot.append("plot \'month-payment_" + str(user[0]) + ".dat\' using 1:2:($2 >= 0 ? 0x00AA00 : 0xAA0000) ti \'\' linecolor rgb variable w boxes\n")
            expGnuplot.append("\n")
            expGnuplot.append("\n")
            expGnuplot.append("set output 'month-item_" + str(user[0]) + ".png\'\n")
            expGnuplot.append("unset timefmt\n")
            expGnuplot.append("unset xdata\n")
            expGnuplot.append("unset format x\n")
            expGnuplot.append("set ylabel \'Consumption\'\n")
            expGnuplot.append("set yrange[0:*]\n")
            expGnuplot.append("set boxwidth 0.8\n")
            expGnuplot.append("set style data histogram\n")
            expGnuplot.append("set style histogram clustered gap 2\n")
            expGnuplot.append("set key inside right top box opaque\n")
            expGnuplot.append("everyfifth(col) = ((int(column(col)) % 2 == 0) ? stringcolumn(1) : \'\')\n")
            expGnuplot.append("plot \'month-item_" + str(user[0]) + ".dat\' using 2:xticlabel((everyfifth(0))) ls 1 ti \'Coffee\', \'\' u 3 ls 2 ti \'Milk\'\n")
            expGnuplot.append("\n")
            expGnuplot.append("\n")
            expGnuplot.append("set output \'month-percentage_" + str(user[0]) + ".png\'\n")
            expGnuplot.append("set ylabel \'Normalized Consumption\'\n")
            expGnuplot.append("unset yrange\n")
            expGnuplot.append("unset style data\n")
            expGnuplot.append("unset style histogram\n")
            expGnuplot.append("set style fill solid\n")
            expGnuplot.append("set style data boxes\n")
            expGnuplot.append("set boxwidth 0.8\n")
            expGnuplot.append("set xtics (\'Coffee\' 0, \'Milk\' 1)\n")
            expGnuplot.append("set xtics rotate by 0 offset 0,0\n")
            expGnuplot.append("set xrange [-1:2]\n")
            expGnuplot.append("set yrange [0:1]\n")
            expGnuplot.append("set key inside right bottom box opaque\n")
            expGnuplot.append("plot \'percentage-0_" + str(user[0]) + ".dat\' u 1:($2+$3) ti \'" + str(user[1]) + "\' ls 1, \\\n")
            expGnuplot.append("                       \'\' u 1:2 ti \'other\' ls 11 w boxes, \\\n")
            expGnuplot.append("     \'percentage-1_" + str(user[0]) + ".dat\' u 1:($2+$3) ti \'" + str(user[1]) + "\' ls 2, \\\n")
            expGnuplot.append("                       \'\' u 1:2 ti \'other\' ls 12\n")

            # write file
            self.fileWriteTemplate( self.fileOutFolder + "/" + str(user[0]) + ".plot", expGnuplot)
         

        ######################################################
        # Create webpage: main page

        now = datetime.datetime.now()
        year = int(now.strftime("%Y"))
        month = int(now.strftime("%m"))
        expWebMain = [] 
        expWebMain.append(".. title: DPI Coffee Page\n")
        expWebMain.append(".. slug: main\n")
        expWebMain.append(".. date: " + now.strftime("%Y") + "-" + now.strftime("%m") + "-" + now.strftime("%d") + " " + now.strftime("%H") + ":" + now.strftime("%M") + ":" + now.strftime("%S") + " UTC+01:00\n")
        expWebMain.append(".. tags:\n")
        expWebMain.append(".. author: Simon Reich\n")
        expWebMain.append(".. category:\n")
        expWebMain.append(".. link: https://coffee.physik3.gwdg.de\n")
        expWebMain.append(".. description: \n")
        expWebMain.append(".. type: text\n")
        expWebMain.append("\n")
        expWebMain.append("\n")
        expWebMain.append("Balance\n")
        expWebMain.append("=======\n")
        expWebMain.append("\n")
        expWebMain.append("Download the `latest balance <https://coffee.physik3.gwdg.de/" + self.fileOutBalanceMonth + str(year) + "-" + str(month) + "-" + str(day) + ".pdf>`_ as pdf. \n")
        expWebMain.append("\n")
        expWebMain.append("Consumption\n")
        expWebMain.append("===========\n")
        expWebMain.append("\n")
        expWebMain.append("The graph below shows the total coffee and milk usage.\n")
        expWebMain.append("\n")
        expWebMain.append(".. thumbnail:: ../galleries/statistics/month-totalitem.png\n")
        expWebMain.append("\n")
        expWebMain.append("In " + datetime.date(1900, monthOld, 1).strftime('%B') + " " + str(yearOld) + " " + self.user.getRowById(markMax[0][-1][0])[1] + " drank the most coffee and became Coffee King with " + str("{0:.0f}".format(markMax[0][-1][1])) + " cups. Runner ups:\n")
        expWebMain.append("\n")

        # sort by highest coffee
        userActiveCoffeeking = sorted(self.userActiveBalance, key=itemgetter(4))
        userActiveCoffeeking.reverse ()

        if len(userActiveCoffeeking) > 3:
            userActiveCoffeeking = userActiveCoffeeking[0:3]

        counter = 0
        for row in userActiveCoffeeking:
            expWebMain.append(str(counter+1) + ". " + self.user.getRowById(row[0])[1] + " (" + str("{0:.0f}".format(row[4])) + ")\n")
            counter += 1

        expWebMain.append("\n")
        expWebMain.append("Dairy Queen is " + self.user.getRowById(markMax[1][-1][0])[1] + ":\n")
        expWebMain.append("\n")

        # sort by highest milk
        userActiveCoffeeking = sorted(self.userActiveBalance, key=itemgetter(5))
        userActiveCoffeeking.reverse ()

        if len(userActiveCoffeeking) > 3:
            userActiveCoffeeking = userActiveCoffeeking[0:3]

        counter = 0
        for row in userActiveCoffeeking:
            expWebMain.append(str(counter+1) + ". " + self.user.getRowById(row[0])[1] + " (" + str("{0:.0f}".format(row[5])) + ")\n\n")
            counter += 1

        expWebMain.append("\n")
        expWebMain.append("In case you are still wondering how you rank, here is the full list:\n")
        expWebMain.append("\n")
        expWebMain.append(".. thumbnail:: ../galleries/statistics/person-consumption-0.png\n")
        expWebMain.append("\n")
        expWebMain.append(".. thumbnail:: ../galleries/statistics/person-consumption-1.png\n")
        expWebMain.append("\n")
        expWebMain.append("All Coffee Drinkers\n")
        expWebMain.append("===================\n")
        expWebMain.append("\n")

        userActive = self.getAcitvatedUser ()
        counter = 0
        for _counter in range(0, len(self.dataBinMonth)):
            if _counter in userActive:
                expWebMain.append(str(counter+1) + ". `" + self.user.getRowById(_counter)[1] + " <https://coffee.physik3.gwdg.de/posts/" + str(_counter) + ".html>`_ (Current Balance: " + str("{0:.2f}".format(self.dataBinMonth[_counter][-1])) + "€)\n\n")
            counter += 1

        expWebMain.append("\n")
        expWebMain.append("----\n")
        expWebMain.append("\n")
        expWebMain.append(".. image:: https://coffee.physik3.gwdg.de/images/main_footer.jpg\n")
        expWebMain.append("    :width: 100 %\n")
        expWebMain.append("    :alt: \n")
        expWebMain.append("    :align: center\n")

        # write file
        self.fileWriteTemplate( self.fileOutFolder + "/main.rst", expWebMain)
         

        ######################################################
        # Create webpage: user pages

        # loop through all users
        for _counter in range(0, len(self.dataBinMonth)):
            user = self.user.getRowById(_counter)
            paymentH = copy.deepcopy(self.payment.dataBinMonthHeader)
            payment = copy.deepcopy(self.payment.dataBinMonth[_counter])
            del payment[0]
            balanceH = copy.deepcopy(self.dataBinMonthHeader)
            balance = copy.deepcopy(self.dataBinMonth[_counter])
            del balance[0]

            # get marks
            markArray = []
            markArrayH = []
            for _markclass in self.item.marks:
                markArray.append(copy.deepcopy(_markclass.dataBinMonth[_counter]))
                del markArray[-1][0]
                markArrayH = copy.deepcopy(_markclass.dataBinMonthHeader)

            expWebUser = []
            expWebUser.append(".. title: DPI Coffee Page: " + user[1] + "\n")
            expWebUser.append(".. slug: " + str(_counter) + "\n")
            expWebUser.append(".. date: " + now.strftime("%Y") + "-" + now.strftime("%m") + "-" + now.strftime("%d") + " " + now.strftime("%H") + ":" + now.strftime("%M") + ":" + now.strftime("%S") + " UTC+01:00\n")
            expWebUser.append(".. tags: " + user[1] + "\n")
            expWebUser.append(".. author: Simon Reich\n")
            expWebUser.append(".. link: https://coffee.physik3.gwdg.de/posts/" + str(_counter) + ".html\n")
            expWebUser.append(".. description:\n")
            expWebUser.append(".. category: All Coffeeusers\n")
            expWebUser.append("\n")
            expWebUser.append(user[1] + " drank " + str("{0:.0f}".format(markArray[0][-2])) + " Coffee and " + str("{0:.0f}".format(markArray[1][-2])) + " Milk in " + datetime.date(1900, monthOld, 1).strftime('%B') + " " + str(yearOld) + ". Measured on the total consumption in " + datetime.date(1900, monthOld, 1).strftime('%B') + " " + str(yearOld) + " this is:\n")
            expWebUser.append("\n")
            expWebUser.append(".. thumbnail:: ../galleries/statistics/month-percentage_" + str(_counter) + ".png\n")
            expWebUser.append("\n")
            expWebUser.append("The time line of all items is:\n")
            expWebUser.append("\n")
            expWebUser.append(".. thumbnail:: ../galleries/statistics/month-item_" + str(_counter) + ".png\n")
            expWebUser.append("\n")
            if markMaxHistogram[0][user[0]] == 1:
                expWebUser.append(user[1] + " was 1 time Coffee King:\n")
            elif markMaxHistogram[0][user[0]] > 1:
                expWebUser.append(user[1] + " was " + str(markMaxHistogram[0][_counter]) + " times Coffee King:\n")
            expWebUser.append("\n")
            for _month in zip(markMax[0], markArrayH):
                if _month[0][0] == user[0]:
                    expWebUser.append("* " + datetime.date(1900, _month[1][1], 1).strftime('%B') + " " + str(_month[1][0])  + ": Coffee King (coffee: " + str("{0:2.0f}".format(_month[0][1])) + ")\n")
            expWebUser.append("\n")
            if markMaxHistogram[1][user[0]] == 1:
                expWebUser.append(user[1] + " was 1 time Dairy Queen:\n")
            elif markMaxHistogram[1][user[0]] > 1:
                expWebUser.append(user[1] + " was " + str(markMaxHistogram[1][_counter]) + " times Dairy Queen:\n")
            expWebUser.append("\n")
            for _month in zip(markMax[1], markArrayH):
                if _month[0][0] == user[0]:
                    expWebUser.append("* " + datetime.date(1900, _month[1][1], 1).strftime('%B') + " " + str(_month[1][0])  + ": Dairy Queen (milk: " + str("{0:2.0f}".format(_month[0][1])) + ")\n")
            expWebUser.append("\n")
            expWebUser.append("Balance\n")
            expWebUser.append("=======\n")
            expWebUser.append("\n")
            expWebUser.append("The current balance is at: " + str("{0:.2f}".format(self.dataBinMonth[_counter][-1])) + "€. Here is a full list of all payments:\n")
            expWebUser.append("\n")
            for _row in self.payment.data:
                if _row[0] == _counter:
                    if float(_row[4]) != 0:
                        expWebUser.append("* " + str("{0:02.0f}".format(int(_row[3]))) + "." + str("{0:02.0f}".format(int(_row[2]))) + "." + str("{0:04.0f}".format(int(_row[1]))) + " " + str("{0:.2f}".format(float(_row[4])))+ "€\n")
            expWebUser.append("\n")
            expWebUser.append(".. thumbnail:: ../galleries/statistics/month-payment_" + str(_counter) + ".png\n")
            expWebUser.append("\n")
            expWebUser.append("The time line of the balance is as follows:\n")
            expWebUser.append("\n")
            expWebUser.append(".. thumbnail:: ../galleries/statistics/month-balance_" + str(_counter) + ".png\n")
            expWebUser.append("\n")
            expWebUser.append("`Back <https://coffee.physik3.gwdg.de/>`_\n")
            expWebUser.append("\n")
            expWebUser.append("----\n")
            expWebUser.append("\n")
            expWebUser.append(".. image:: https://coffee.physik3.gwdg.de/images/DSC_0058.jpg\n")
            expWebUser.append("    :width: 100 %\n")
            expWebUser.append("    :alt: \n")
            expWebUser.append("    :align: center\n")

            # write file
            self.fileWriteTemplate( self.fileOutFolder + "/" + str(_counter) + ".rst", expWebUser)


    def getTranspose (self, M):
        """ Transposes an array
            see https://stackoverflow.com/questions/23392986/how-to-transpose-an-array-in-python-3
        """
        return [[M[j][i] for j in range(len(M))] for i in range(len(M[0]))]


    def getBalance (self, userid):
        """ Prints the latest balance user with id userid
            userid: id of user
        """
        now = datetime.datetime.now()

        print("")
        print("Balance on " + now.strftime("%d") + "." + now.strftime("%m") + "." + now.strftime("%Y") + ": " + str("{0:.2f}".format(self.dataBinMonth[userid][-1])) + "€.\n")
