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

# coffeedatabase
from lib import cuser


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
    def __init__(self, user):
        self.user = user


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
            user: Class cuser object. User is added to this database
        """

        userDescription = ["Name", "Mail"]
        userStandard = ["", "institut@gwdg.de"]


        inputUser = self.inputStandard(userDescription, userStandard)
        inputUser.append("auto")

        self.user.userAdd(inputUser)

        return 0


    def getUserByTextname(self):
        """ Displays a name field and returns id of user.
        """
        completer = MyCompleter(self.user.getNamelist())
        readline.set_completer(completer.complete)
        readline.parse_and_bind('tab: complete')

        inputText = input("Name: ")

        return self.user.getUserByName(inputText)



    def userChangeInfo(self):
        """ Displays user information and allows to change them.
        """

        user = self.getUserByTextname()

        # remove id
        print (user)
        del user[0]

        userDescription = ["Name", "Mail", "Status"]
        inputUser = self.inputStandard(userDescription, user)

        # add user id
        inputUser.insert(0, userId)

        # save in database
        self.user.setUser(inputUser)

        return 0
