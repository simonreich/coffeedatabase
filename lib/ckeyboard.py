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
import readline
import datetime
import configparser

# coffeedatabase
from lib import cuser
from lib import cpayment
from lib import citem
from lib import cdatabase
from lib import cprice
from lib import cbalance


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


class ckeyboard:
    def __init__(self):
        # First, load the config
        config = configparser.ConfigParser()
        config.sections()
        config.read('config.ini')

        if not ('FILENAME' in config) or not ('LIST' in config):
            print("Broken config file \"config.ini\".")
            raise

        self.fileUser = config['FILENAME']['fileUser']
        self.filePayment = config['FILENAME']['filePayment']
        self.fileItem = config['FILENAME']['fileItem']
        self.fileMarks = config['FILENAME']['fileMarks']
        self.filePrice = config['FILENAME']['filePrice']
        self.inactiveMonths = config['LIST']['inactiveMonths']
        self.fileTemplateBalanceMonth = config['FILENAME']['fileTemplateBalanceMonth']
        self.fileOutBalanceMonth = config['FILENAME']['fileOutBalanceMonth']
        self.fileTemplateListMonth = config['FILENAME']['fileTemplateListMonth']
        self.fileOutListMonth = config['FILENAME']['fileOutListMonth']
        self.fileOutFolder = config['FILENAME']['fileOutFolder']

        if (self.fileUser == "") or \
                (self.filePayment == "") or \
                (self.fileMarks == "") or \
                (self.filePrice == "") or \
                (self.fileItem == ""):
            print("Broken config file \"config.ini\".")
            raise

        # create databases, if they do not exist.
        database = cdatabase.cdatabase(self.fileUser, self.filePayment, self.fileItem, self.fileMarks, self.filePrice)

        self.user = cuser.cuser(self.fileUser, self.inactiveMonths)
        self.payment = cpayment.cpayment(self.filePayment, self.user)
        self.item = citem.citem(self.fileItem, self.fileMarks, self.user)
        self.price = cprice.cprice(self.filePrice, self.item)
        self.balance = cbalance.cbalance(self.user, self.payment, self.price, self.item, self.inactiveMonths, self.fileTemplateBalanceMonth, self.fileOutBalanceMonth, self.fileTemplateListMonth, self.fileOutListMonth, self.fileOutFolder)


    def inputStandard(self, valueDescription, valueStandard):
        """ Displays an input field, nicely formatted. If valueDescription contains \"Name\" or \"name\", autocompletion for the name database will be activated.
            valueDescription: List of description for input values.
            valueStandard: List of standard values.
        """

        if not len(valueDescription) == len(valueStandard):
            print("Input vector", valueDescription, "has not the same length as standard value vector", valueStandard)
            raise

        counter = 0
        for description in valueDescription:
            if description.lower() == "status":
                # display special user input field
                print("New status:")
                print("1 - active")
                print("2 - auto")
                print("3 - inactive")
                textInput = input(str(description) + " [" + valueStandard[counter] + "]: ")

                if textInput == "":
                    textInput = valueStandard[counter]

                if textInput == "1" or textInput == "active":
                    valueStandard[counter] = "active"
                elif textInput == "2" or textInput == "auto":
                    valueStandard[counter] = "auto"
                elif textInput == "3" or textInput == "inactive":
                    valueStandard[counter] = "inactive"
                else:
                    print("The input " + str(textInput) + " was not understood. Please use 1, 2, or 3, active, auto, or inactive.")
                    raise
            else:
                if not valueStandard[counter] == "":
                    textInput = input(str(description) + " [" + valueStandard[counter] + "]: ")
                else:
                    textInput = input(str(description) + ": ")
                if not textInput == "":
                    valueStandard[counter] = textInput
            counter += 1

        return valueStandard


    def userAdd(self):
        """ Adds a user to the user database
        """

        userDescription = ["Name", "Mail"]
        userStandard = ["", "institut@gwdg.de"]

        inputUser = self.inputStandard(userDescription, userStandard)
        inputUser.append("auto")

        self.user.userAdd(inputUser)

        # Make a dummy payment
        now = datetime.datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        day = now.strftime("%d")
        user = self.user.getRowByName(inputUser[0])
        payment = [user[0], year, month, day, 0]
        self.payment.paymentAdd(payment)

        # Make dummy marks
        mark = [user[0], year, month, day, 0]
        for _marks in self.item.marks:
            _marks.marksAdd(mark)

        return 0


    def userChangeInfo(self):
        """ Displays user information and allows to change them.
        """

        user = self.getRowByTextname(self.user.getNamelist(), self.user)

        # remove id
        userId = user[0]
        del user[0]

        print("")
        userDescription = ["Name", "Mail", "Status"]
        inputUser = self.inputStandard(userDescription, user)

        # add user id
        inputUser.insert(0, userId)

        # save in database
        self.user.setUser(inputUser)

        return 0


    def paymentAdd(self):
        """ Adds a payment to the payment database
        """

        user = self.getRowByTextname(self.user.getNamelist(), self.user)

        # create dates
        now = datetime.datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        day = now.strftime("%d")

        payment1 = [user[0], int(year), int(month), int(day)]

        print("")
        userDescription = ["Payment"]
        payment2 = [""]
        inputUser = self.inputStandard(userDescription, payment2)

        # fill payment
        payment = payment1 + payment2

        # save in database
        self.payment.paymentAdd(payment)

        # print new balance
        self.payment.getDataBinMonth()
        self.balance.getDataBinMonth()
        self.balance.getBalance(user[0])

        return 0


    def itemAdd(self):
        """ Adds a user to the user database
        """

        itemDescription = ["Name", "Unit"]
        itemStandard = ["Coffee", "per cup"]

        inputItem = self.inputStandard(itemDescription, itemStandard)
        inputItem.append("active")

        self.item.itemAdd(inputItem)

        return 0


    def itemChangeInfo(self):
        """ Displays item information and allows to change them.
        """

        item = self.getRowByTextname(self.item.getColumn(1), self.item)

        # remove id
        itemId = item[0]
        del item[0]

        print("")
        itemDescription = ["Name", "Unit", "Status"]
        inputItem = self.inputStandard(itemDescription, item)

        # add item id
        inputItem.insert(0, itemId)

        # save in database
        self.item.setItem(inputItem)

        return 0


    def getRowByTextname(self, array, database):
        """ Displays a name field and returns row.
        array: Array used for auto completion in text input field.
        database: Reference to database class, e.g. self.item, self.user, ...
        """
        completer = MyCompleter(array)
        readline.set_completer(completer.complete)
        readline.parse_and_bind('tab: complete')

        print("Search in item database:")
        inputText = input("Name: ")

        return database.getRowByName(inputText, 1)


    def marksAdd(self):
        """ Adds marks to the marks database
        """

        # create dates
        now = datetime.datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        day = now.strftime("%d")

        self.item.data

        # get user
        user = self.getRowByTextname(self.user.getNamelist(), self.user)

        # get item list
        markDescription = []
        markDefault = []
        for row in self.item.data:
            if str(row[3]) == "active":
                markDescription.append(row[1])
                markDefault.append("0")

        # query user input
        print("")
        inputMark = self.inputStandard(markDescription, markDefault)
 
        # create array for cmark class
        markArray = [[0 for x in range(0)] for x in range(0)]
        counter = 0
        for row in self.item.data:
            if str(row[3]) == "active":
                markArray.append([user[0], int(year), int(month), int(day), int(inputMark[counter])])
                counter += 1
            else:
                markArray.append([user[0], int(year), int(month), int(day), 0])

        # save in database
        self.item.marksAdd(markArray)

        return 0


    def marksAddAll(self):
        """ Adds marks to the marks database for all active users
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

        # create dates
        now = datetime.datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        day = now.strftime("%d")

        for userId in userActive:
            user = self.user.getRowById(userId)

            print("\n", user[1])

            # get item list
            markDescription = []
            markDefault = []
            for row in self.item.data:
                if str(row[3]) == "active":
                    markDescription.append(row[1])
                    markDefault.append("0")

            # query user input
            print("")
            inputMark = self.inputStandard(markDescription, markDefault)
 
            # create array for cmark class
            markArray = [[0 for x in range(0)] for x in range(0)]
            counter = 0
            for row in self.item.data:
                if str(row[3]) == "active":
                    markArray.append([user[0], int(year), int(month), int(day), int(inputMark[counter])])
                    counter += 1
                else:
                    markArray.append([user[0], int(year), int(month), int(day), 0])

            # save in database
            self.item.marksAdd(markArray)

        return 0


    def priceAdd(self):
        """ Adds a price the price database
        """

        priceDescription = []
        priceStandard = []
        itemId = []
        priceOld = [[0 for x in range(0)] for x in range(0)]

        # acquiere old prices, save as [itemId, price]
        for row in self.price.dataBinMonth:
            if len(row) >= 2:
                for x in range(0, len(row)-1):
                    if not float(row[-1-x]) == 0:
                        priceOld.append([row[0], str(row[-1-x])])
                        break

        # create input fields
        for row in self.item.data:
            priceDescription.append(str(row[1]) + " " + str(row[2]))
            priceOldAdded = False
            for row1 in priceOld:
                if row[0] == row1[0]:
                    priceStandard.append(row1[1])
                    priceOldAdded = True
            if not priceOldAdded:
                priceStandard.append("0")
            itemId.append(row[0])

        inputPrice= self.inputStandard(priceDescription, priceStandard)

        # create dates
        now = datetime.datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        day = now.strftime("%d")

        counter = 0
        for row in itemId:
            self.price.priceAdd([row, year, month, day, inputPrice[counter]])
            counter += 1

        return 0


    def priceFill(self):
        """ Checks the marks database and matches marks with prices. If a price does not exist, it is requested and added to the price database.
        """

        itemId=0
        for row in self.item.data:
            print ("Checking for item " + str(row[1]))

            # Check for marks
            self.item.marks[itemId].getDataBinMonth()
            marks = self.item.marks[itemId].dataBinMonthHeader

            # Check for prices
            pricesH = self.price.dataBinMonthHeader
            pricesF = self.price.dataBinMonth
            prices = []

            # Find Id in pricesF
            for rowId in pricesF:
                if rowId[0] == row[0]:
                    prices = rowId
                    del prices[0]

            # If Id was not found, we create an empty array
            if len(prices) == 0:
                if len(pricesF) >= 1:
                    prices = [0 for x in range(len(pricesF[0])-1)]

            # Find missing prices in Header
            for mark in marks:
                priceFound = False
                for price in pricesH:
                    if mark == price:
                        priceFound = True
                if not priceFound:
                    pricesH.append(mark)
                    prices.append(0)

            # Find empty prices
            priceMissing = [[0 for x in range(0)] for x in range(0)]
            counter = 0
            for price in prices:
                if price == 0:
                    priceMissing.append(pricesH[counter])
                counter += 1

            # Request user input for missing prices
            princeLatest = "0"
            for price in priceMissing:
                priceDescription = ["Enter price for " + str(row[1]) + " for year " + str(price[0]) + " and month " + str(price[1])]
                priceStandard = [princeLatest]
                inputPrice= self.inputStandard(priceDescription, priceStandard)
                princeLatest = inputPrice[0]

                # save prices
                self.price.priceAdd([row[0], price[0], price[1], 1, str(inputPrice[0])])

            itemId += 1

        return 0


    def balanceExportPDF(self):
        """ Compute the balance
        """

        # create dates
        now = datetime.datetime.now()
        year = int(now.strftime("%Y"))
        month = int(now.strftime("%m"))

        dateDescription = ["Year", "Month"]
        dateStandard = [str(year), str(month)]

        inputDate = self.inputStandard(dateDescription, dateStandard)

        # create balance class
        self.balance.exportMonthPDF(inputDate[0], inputDate[1], 1)


    def listExportPDF(self):
        """ Compute the name list
        """

        # create dates
        now = datetime.datetime.now()
        year = int(now.strftime("%Y"))
        month = int(now.strftime("%m"))

        dateDescription = ["Year", "Month"]
        dateStandard = [str(year), str(month)]

        inputDate = self.inputStandard(dateDescription, dateStandard)

        # create balance class
        self.balance.exportMonthListPDF(inputDate[0], inputDate[1], 1)


    def balanceCheck(self):
        """ Prints a users balance
        """

        user = self.getRowByTextname(self.user.getNamelist(), self.user)

        # print balance
        self.balance.getBalance(user[0])

        return 0
