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
from lib import cmarks


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

        if (self.fileUser == "") or \
                (self.filePayment == "") or \
                (self.fileItem == ""):
            print("Broken config file \"config.ini\".")
            raise

        # create databases, if they do not exist.
        # TODO: this is a bad place as the ckeyboard class is supposed to be
        # the input interface and should not offer any internal functionality.
        # This code should be moved somewhere more appropriate.
        if not os.path.exists(self.fileUser):


        self.user = cuser.cuser(self.fileUser)
        self.payment = cpayment.cpayment(self.filePayment, self.user)
        self.item = citem.citem(self.fileItem)
        self.marks = cmarks.cmarks("test.csv", self.user)


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
        """ Adds a payment to the user database
        """

        user = self.getUserByTextname()

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

        return 0


    def itemAdd(self):
        """ Adds a user to the user database
        """

        itemDescription = ["Name", "Unit"]
        itemStandard = ["Coffee", "per cup"]

        inputItem = self.inputStandard(itemDescription, itemStandard)

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
        itemDescription = ["Name", "Unit"]
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

        marksDescription = [2, "Year", "Month", "Day", 5]
        #itemStandard = ["Coffee", "per cup"]

        #inputItem = self.inputStandard(itemDescription, itemStandard)

        self.marks.marksAdd(marksDescription)

        return 0


