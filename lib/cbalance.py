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
        self.getStatistics(year, month)


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


    def getStatistics (self, year, month):
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
                expMonthsVsItem.append(str(_row[0]) + "-" + str(_row[1]))
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
                expMonthsVsPayment.append(str(_row[0][0])+ "-" + str(_row[0][1]) + "\t" + str(_row[1]) + "\n")

            # write file
            self.fileWriteTemplate( self.fileOutFolder + "/month-payment_" + str(user[0]) + ".dat", expMonthsVsPayment)


            ######################################################
            # Months vs. Balance

            expMonthsVsBalance = []
            for _row in zip(balanceH, balance):
                expMonthsVsBalance.append(str(_row[0][0])+ "-" + str(_row[0][1]) + "\t" + str("{:.2f}".format(_row[1])) + "\n")

            # write file
            self.fileWriteTemplate( self.fileOutFolder + "/month-balance_" + str(user[0]) + ".dat", expMonthsVsBalance)


            ######################################################
            # Percentage of Consumption

            marksConsumption = []
            for _marks in markArray:
                marksConsumption.append(_marks[markArrayH.index([yearOld, monthOld])])

            expPercentage = [str(user[1])]
            for _row in zip(markSum, _marks):
                expPercentage.append("\t" + str("{:.2f}".format(1/float(_row[0][markArrayH.index([yearOld, monthOld])])*float(_row[1]))))
            expPercentage.append("\nOther")
            for _row in zip(markSum, _marks):
                expPercentage.append("\t" + str("{:.2f}".format(1-(1/float(_row[0][markArrayH.index([yearOld, monthOld])])*float(_row[1])))))
            expPercentage.append("\n")

            # write file
            self.fileWriteTemplate( self.fileOutFolder + "/percentage_" + str(user[0]) + ".dat", expPercentage)



    def getTranspose (self, M):
        """ Transposes an array
            see https://stackoverflow.com/questions/23392986/how-to-transpose-an-array-in-python-3
        """
        return [[M[j][i] for j in range(len(M))] for i in range(len(M[0]))]
