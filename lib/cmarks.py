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


class cmarks(cbase.cbase):
    def __init__(self, filename, user):
        super().__init__(filename)
        self.user = user


    def marksAdd(self, marks):
        """ Adds marks to the marks database
            marks: Marks as array ["Id", "Year", "Month", "Day", "Marks"].
        """

        if not len(marks) == 5:
            print("The given marks array has wrong format ([\"Id\", \"Year\", \"Month\", \"Day\", \"Marks\"]): ", marks)
            raise

        marks[0] = int(marks[0])
        marks[1] = int(marks[1])
        marks[2] = int(marks[2])
        marks[3] = int(marks[3])
        marks[4] = int(marks[4])

        # check if id exists
        user = self.user.getRowById(marks[0])

        # quick sanity check for year
        if not marks[1] > 2000:
            print("Year is not in range", marks)
            raise
        # quick sanity check for month
        if not marks[2] > 0 or not marks[2] < 13:
            print("Month is not in range", marks)
            raise
        # quick sanity check for day
        if not marks[3] > 0 or not marks[3] < 32:
            print("Day is not in range", marks)
            raise

        self.data.append(marks)
        self.fileWrite()

        return 0
