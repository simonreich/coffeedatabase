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


######################################################


# file name for price information
global filePrice
filePrice="price.csv"

# file name for user database
global fileUser
fileUser="user.csv"

# how many months of being inactive is acceptable to be still on
# the final lsit
global userInactiveMonth
userInactiveMonth = 6


######################################################
## No Configuration after this
######################################################


# system
import sys

# coffeedatabase
from lib import payment
from lib import user
from lib import item

# global variables
global userHeader
userHeader = ["id", "name", "mail", "status"]
global userHeaderLen
userHeaderLen = len(userHeader)


# print help
def printHelp (programname):
    """ Gibt einen Hilfetext auf den Bildschirm aus.
    """
    text = "Usage: " + programname + (" [OPTION]\n"
           "  -h, --hilfe, --help       Dieser Hilfetext.")

    print(text)

    return 0


# main function
def main(argv=None):
    """ main function
        argv: possible arguments, will be replaced by sys.argv if none are 
              given.
    """
    if argv is None:
        argv = sys.argv

    for arg in argv:
        if (arg == "-h" or
                arg == "-help" or
                arg == "--help" or
                arg == "-hilfe" or
                arg == "--hilfe" or
                arg == "-?" or
                arg == "--?" or
                arg == "?"):
            printHelp(sys.argv[0])

        elif(arg == "--payment" or
                arg == "-p" or
                arg == "p"):
            payment.makePayment(fileUser)

        elif(arg == "--payment2userdatabase" or
                arg == "-p2u" or
                arg == "p2u"):
            payment.payment2userdatabase(fileUser, filePrice)

        elif(arg == "--useradd" or
                arg == "-ua" or
                arg == "ua"):
            user.userAdd(fileUser)

        elif(arg == "--userlist" or
                arg == "-ul" or
                arg == "ul"):
            user.userList(fileUser, filePrice, userInactiveMonth)
            userInactiveMonth

        elif(arg == "--userstatus" or
                arg == "-us" or
                arg == "us"):
            user.userStatus(fileUser)

        elif(arg == "--markslist" or
                arg == "-ml" or
                arg == "ml"):
            item.makeMarksList(fileUser, filePrice, userInactiveMonth)

        elif(len(sys.argv) == 1):
            printHelp(sys.argv[0])

    # Ende
    sys.exit(0)


if __name__ == "__main__":
    main()