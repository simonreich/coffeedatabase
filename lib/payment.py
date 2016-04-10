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


def makePayment(fileUser):
    """ Somebody wants to make a payment
        fileInputMeldeliste: 
    """

    # load user data
    userFull = helper.fileOpen(fileUser)
    userName = helper.column(userFull, 1)

    inputText= helper.autocompletion(userName)

    # search for multiple entries
    matching = [s for s in userName if inputText in s]
    if len(matching) > 1:
        raise NameError("Found user input text multiple times in name database. Names found: ", matching)

    # input field for paymend
    inputPayment = input("Payment [€]: ")
    try:
        inputPayment = "{:.2f}".format(float(inputPayment))
    except ValueError:
        raise ValueError("Payment seems to contain errors: ", inputPayment)

    # get id to name
    matching = [s for s in userFull if inputText in s]
    print ("\nID: " + matching[0][0] + " Name: " + matching[0][1] + " Payment: " + inputPayment + "€")

    # create path and file name
    now = datetime.datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")
    day = now.strftime("%d")
    filePayment = year + "/" + month + "/" + "payment.csv"

    # array to save stuff
    save = [year, month, day, matching[0][0], matching[0][1], inputPayment]

    if os.path.exists(filePayment):
        helper.fileAppend(filePayment, save)
    else:
        if not os.path.exists(year):
            os.makedirs(year)
        if not os.path.exists(year + "/" + month):
            os.makedirs(year + "/" + month)

        save2 = [[0 for x in range(0)] for x in range(0)]
        save2 = [["year", "month", "day", "id", "name", "payment"]]
        save2.append(save)
        helper.fileWrite(filePayment, save2)

    # update user database
    payment2userdatabase(fileUser, filePayment)

    return 0


def payment2userdatabase(fileUser, filePrice, filePayment="",):
    """ Transfers a list of payments into the user database
        fileUser: file name as string 
        filePayment: file name as string 
    """

    now = datetime.datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")

    # create path and file name
    if filePayment == "":
        filePayment = year + "/" + month + "/" + "payment.csv"

    # check if we need to create entries in user database
    helper.userdatabaseCreatemonth(fileUser, filePrice, year, month)

    dataP = helper.fileOpen(filePayment)
    dataU = helper.fileOpen(fileUser, True)

    if len(dataP) == 0:
        print("Payment file seems to be empty")
        raise
    
    # sort by id
    dataP = helper.sort_table_low(dataP, [3,5])

    # create dummy entry for last payment, see algorithm below
    dataP.append(["", "", "", "-1", "", ""])

    dataP2 = [[0 for x in range(0)] for x in range(0)]
    rowOld = [0 for x in range(0)]
    counter = 0
    for row in dataP:
        if counter == 0:
            rowOld = list(row)
        else:
            if row[3] == rowOld[3]:     # id is identical
                rowOld[5] = float(rowOld[5])
                rowOld[5] += float(row[5])
            else:
                dataP2.append(rowOld)
                rowOld = list(row)
                
        counter += 1

    # search for column in user database
    item = year + "-" + month + "-payment"
    cellNr = -1
    counter = 0
    for cell in dataU[0]:
        if cell == item:
            cellNr = counter
            break
        counter += 1

    if cellNr == -1:
        print("Could not find item " + item + " in user database.")
        raise

    # match payment ids to user ids
    for rowP in dataP2:
        cellFound = False
        counter = 0
        for rowU in dataU:
            if counter > 0:
               if int(rowP[3]) == int(rowU[0]):
                   dataU[counter][cellNr] = '{0:.2f}'.format(float(rowP[5]))
                   cellFound = True
            counter +=1

        if not cellFound:
            print ("There is a payment for which there is no id in the user database:", rowP)
            raise

    # save data
    helper.fileWrite(fileUser, dataU)

    return 0
