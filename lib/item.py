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
import os.path

# coffeedatabase
from lib import helper
from lib import user


def makeMarksList(fileUser, filePrice, userInactiveMonth):
    """ Somebody wants to add marks
        fileUser: file name as string
        filePrice: file name as string
        userInactiveMonth: nr of inactive months
    """

    now = datetime.datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")

    # load user data
    dataU= helper.fileOpen(fileUser)
    dataPrice = helper.fileOpen(filePrice)

    # create path and file name
    fileMarks = year + "/" + month + "/" + "marks.csv"

    # get list of active users
    if os.path.exists(fileMarks):
        userList = helper.fileOpen(fileMarks)
    else:
        userList = user.userList(fileUser, filePrice, userInactiveMonth)
        for item in dataPrice:
            userList = [x + [""] for x in userList]

    # display input mask
    counter = 0
    for row in userList:
        print("\nName: " + row[1])
        counter1 = 2
        for item in dataPrice:
            default = userList[counter][counter1]
            if default == "":
                default = 0
            inputText = input(item[1] + " [" + str(default) + "]: ")
            if inputText == "":
                inputText = default
            userList[counter][counter1] = int(inputText)
            counter1 += 1
        counter += 1

    # add header
    header = ["id", "name"]
    for item in dataPrice:
        header.append(item[1])
    userList.insert(0, header)

    # save
    helper.fileWrite(fileMarks, userList)

    return 0


def makeMarksUser(fileUser, filePrice, userInactiveMonth):
    """ Somebody wants to add marks
        fileUser: file name as string
        filePrice: file name as string
        userInactiveMonth: nr of inactive months
    """

    now = datetime.datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")

    # load user data
    dataU= helper.fileOpen(fileUser)
    dataN = helper.column(dataU, 1)
    dataPrice = helper.fileOpen(filePrice)

    # create path and file name
    fileMarks = year + "/" + month + "/" + "marks.csv"

    user = helper.autocompletion(dataN)

    # get id to name
    matching = [s for s in dataU if user in s]

    # check for existing marks
    defaultList = [matching[0][0], user]
    defaultFound = False
    for item in dataPrice:
        defaultList.append("0")
    if os.path.exists(fileMarks):
        userList = helper.fileOpen(fileMarks)
        for row in userList:
            if int(row[0]) == int(matching[0][0]):
                if len(defaultList) == len(row):
                    defaultList = list(row)
                    defaultFound = True
                else:
                    print("Length mismatch in marks file " + fileMarks + ". Something is really wrong and needs to be manually fixed. There are less items in the database file than in the price database.")
                    raise
                break

    # display input mask
    print("\nName: " + defaultList[1])
    counter = 2
    for item in dataPrice:
        default = defaultList[counter]
        if default == "":
            default = 0
        inputText = input(item[1] + " [" + str(default) + "]: ")
        if inputText == "":
            inputText = default
        defaultList[counter] = int(inputText)
        counter += 1

    if defaultFound:


    # add header
    header = ["id", "name"]
    for item in dataPrice:
        header.append(item[1])
    userList.insert(0, header)

    # save
    helper.fileWrite(fileMarks, userList)

    return 0
