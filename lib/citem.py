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


from lib import cbase
from lib import cmarks


class citem(cbase.cbase):
    def __init__(self, fileItem, fileMarks, user):
        super().__init__(fileItem)

        # this will hold an array of marks classes
        self.marks = []
        for itemId in self.getColumn(0):
            fileMarks2 = fileMarks + str(itemId) + ".csv"
            self.marks.append(cmarks.cmarks(fileMarks2, user))


    def itemAdd(self, item):
        """ Adds an item to the item database
            item: Item as array ["Name", "Unit"].
        """

        if not len(item) == 2:
            print("The given item array has wrong format ([\"Name\", \"Unit\"]): ", item)
            raise

        item[0] = str(item[0])
        item[1] = str(item[1])

        # check if name exists and search for highest id
        highid = -1
        for row in self.data:
            if int(row[0]) > highid:
                highid = int(row[0])
            if row[1] == item[0]:
                print("The name " + str(item[0]) + " already exists in item database: ", row)
                raise

        item.insert(0, highid+1)

        self.data.append(item)
        self.fileWrite()

        return 0


    def setItem (self, item):
        """ Sets variables of existing item
            item: Item as array ["Id", "Name", "Unit"]
        """

        if not len(item) == 3:
            print("The given item array has wrong format ([\"Id\", \"Name\", \"Unit\"]): ", item)
            raise

        item[0] = int(item[0])
        item[1] = str(item[1])
        item[2] = str(item[2])

        itemFound = False
        counter = 0
        for row in self.data:
            if int(row[0]) == item[0]:
                itemFound = True
                self.data[counter] = item
                break
            counter += 1

        if not itemFound:
            print("The id " + str(item[0]) + " could not be found in item database.")
            raise

        self.fileWrite()

        return 0
