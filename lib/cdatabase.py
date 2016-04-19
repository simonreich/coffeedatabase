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
import os.path
import sys
import csv

# coffeedatabase
from lib import citem


class cdatabase:
    def __init__(self, fileUser, filePayment, fileItem, fileMarks):
        fileUser = str(fileUser)
        filePayment = str(filePayment)
        fileItem = str(fileItem)
        fileMarks = str(fileMarks)

        # create databases, if they do not exist.
        if not os.path.exists(fileUser):
            self.fileWrite(fileUser, ["Name", "Mail", "Status"])
        if not os.path.exists(filePayment):
            self.fileWrite(filePayment, ["Id", "Year", "Month", "Day", "Payment"])
        if not os.path.exists(fileItem):
            self.fileWrite(fileItem, ["Id", "Name", "Unit"])
        else:
            item = citem.citem(fileItem)
            for itemId in item.getColumn(0):
                fileMarks = fileMarks + str(itemId) + ".csv"
                if not os.path.exists(fileMarks):
                    self.fileWrite(fileMarks, ["Id", "Year", "Month", "Day", "Marks"])


    def fileWrite(self, filename, array):
        """ writes an array to a cvs file
        filename: Filename as string.
        array: Array to save as array.
        """
        if filename == "":
            print("No filename given.")
            raise

        try:
            f = open(filename, 'wt')
            w = csv.writer (f, 
                delimiter=',', 
                quotechar='"', 
                quoting=csv.QUOTE_ALL)
        except OSError as err:
            print("OS error: {0}".format(err))
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise
        else:
            w.writerow(array)
            f.close ()

        return 0
