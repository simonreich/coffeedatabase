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


# coffeedatabase
from lib import helper


def useradd(fileUser):
    """ Adds a user to the user database
        fileUser: file name as string
    """

    dataU = helper.fileOpen(fileUser, True)

    inputName = input("Name: ")
    inputMail = input("Mail [institut@gwdg.de]: ")

    # check if name exists and search for highest id
    highid = -1
    counter = 0
    for row in dataU:
        if counter > 0:
            if int(row[0]) > highid:
                highid = int(row[0])
        if row[1] == inputName:
            print("The name " + inputName + " already exists in user databse.")
            raise
        counter += 1

    # standard mail address
    if inputMail == "":
        inputMail = "institut@gwdg.de"

    newuser = [highid+1, inputName, inputMail, "auto"]

    # fill rest of list and append
    for n in range(len(newuser), len(dataU[0])):
        newuser.append("")
    dataU.append(newuser)

    helper.fileWrite(fileUser, dataU)

    return 0


def userstatus(fileUser):
    """ Changes user status
        fileUser: file name as string
    """

    dataU = helper.fileOpen(fileUser, True)
    dataN = helper.column(dataU, 1)

    inputName = helper.autocompletion(dataN)

    # Search for user in database
    nameFound = False
    counter = 0
    for row in dataU:
        if row[1] == inputName:
            rowNr = counter
            nameFound = True
            break
        counter += 1

    if not nameFound:
        print("The user " + inputName + " was not found in the database.")
        raise

    print("Found user " + inputName + ". Current Status: " + dataU[rowNr][3])
    print("New status:")
    print("1 - inactive")
    print("2 - auto")
    print("3 - active")

    inputStatus = input("New Status [2]: ")

    if inputStatus == "1":
        status = "inactive"
    elif inputStatus == "2":
        status = "auto"
    elif inputStatus == "3":
        status = "active"
    elif inputStatus == "":
        status = "auto"
    else:
        print("Your input must be 1, 2, 3")
        raise

    dataU[rowNr][3] = status

    helper.fileWrite(fileUser, dataU)

    return 0
