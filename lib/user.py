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
from lib import helper


def userAdd(fileUser):
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


def userStatus(fileUser):
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


def userList(fileUser, filePrice, userInactiveMonth):
    """ Creates a list of all users who had some activity within the last userInactiveMonth month
        fileUser: file name as string
        userInactiveMonth: integer that specifies the months of inactiveness
    """

    now = datetime.datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")

    filePrice = year + "/" + month + "/" + filePrice
    dataPrice = helper.fileOpen(filePrice)
    dataU = helper.fileOpen(fileUser, True)

    # list last userInactiveMonth months
    searchM = [[year, month]]
    monthS = int(month)
    monthCurr = int(month)
    yearCurr = int(year)
    for n in range(1, userInactiveMonth):
        monthCurr = monthS - int(n)
        if monthCurr == 0:
            monthCurr = 12
            monthS += 12
            yearCurr -= 1
        searchM.append([yearCurr, monthCurr])
            
    # create search vector
    search = []
    for item in searchM:
        search.append(str(item[0]) + "-" + str(item[1]) + "-payment")
        counter = 0
        for row in dataPrice:
            search.append(str(item[0]) + "-" + str(item[1]) + "-" + str(counter))
            counter += 1
        search.append(str(item[0]) + "-" + str(item[1]) + "-balance")

    # search for columns in header of dataU
    searchColumn = []
    for itemS in search:
        counter = 0
        for itemU in dataU[0]:
            if itemS == itemU:
                searchColumn.append(counter)
            counter += 1

    # loop throuch user database
    # inactive users are always ignored
    # active users are always added
    # auto is computed based on search vector
    nameList= [[0 for x in range(0)] for x in range(0)]
    for row in dataU:
        if row[3] == "active":
            nameList.append([row[0], row[1]])
        elif row[3] == "auto":
            for column in searchColumn:
                if row[column] != "":
                    nameList.append([row[0], row[1]])
                    break


    # sort by id
    nameList= helper.sort_table_low(nameList, [0,1])

    return nameList
