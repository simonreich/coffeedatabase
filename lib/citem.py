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
#from lib import cmarks


class citem(cbase.cbase):
    def __init__(self, filename, user):
        super().__init__(filename)

       # self.dataMarks = []
       # for row in self.data:
     #       self.dataMarks.append(


    def itemAdd(self, item):
        """ Adds a payment to the payment database
            item: Item as array ["Name", "Unit"].
        """

        if not len(item) == 2:
            print("The given item array has wrong format ([\"Name\", \"Unit\"]): ", item)
            raise

        item[0] = str(item[0])
        item[1] = str(item[1])

        # check if name exists and search for highest id
        highid = 0
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
