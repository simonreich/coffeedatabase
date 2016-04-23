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


class cprice(cbase.cbase):
    def __init__(self, filename, item):
        super().__init__(filename)
        self.item = item


    def priceAdd(self, price):
        """ Adds a price to the price database
            price: Price as array ["Id", "Year", "Month", "Day", "Price"].
        """

        if not len(price) == 5:
            print("The given price array has wrong format ([\"Id\", \"Year\", \"Month\", \"Day\", \"Price\"]): ", price)
            raise

        price[0] = int(price[0])
        price[1] = int(price[1])
        price[2] = int(price[2])
        price[3] = int(price[3])
        price[4] = "{:.2f}".format(float(price[4]))

        # check if id exists
        item = self.item.getRowById(price[0])

        # quick sanity check for year
        if not price[1] > 2000:
            print("Year is not in range", price)
            raise
        # quick sanity check for month
        if not price[2] > 0 or not price[2] < 13:
            print("Month is not in range", price)
            raise
        # quick sanity check for day
        if not price[3] > 0 or not price[3] < 32:
            print("Day is not in range", price)
            raise

        self.data.append(price)
        self.checkDouble()
        self.fileWrite()

        return 0


    def checkDouble(self):
        """ Checks, if for one month a double price has been entered
        """

        dataSorted = self.sortArrayLow(self.data,[1, 2, 0])

        for row in self.dataSorted:
            print(row)


        return 0
