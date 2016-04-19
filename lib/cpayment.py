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


class cpayment(cbase.cbase):
    def __init__(self, filename, user):
        super().__init__(filename)
        self.user = user


    def paymentAdd(self, payment):
        """ Adds a payment to the payment database
            payment: Payment as array ["Id", "Year", "Month", "Day", "Payment"].
        """

        payment[0] = int(payment[0])
        payment[1] = int(payment[1])
        payment[2] = int(payment[2])
        payment[3] = int(payment[3])
        payment[4] = "{:.2f}".format(float(payment[4]))

        if not len(payment) == 5:
            print("The given payment array has wrong format ([\"Id\", \"Year\", \"Month\", \"Day\", \"Payment\"]): ", payment)
            raise

        # check if id exists
        user = self.user.getRowById(payment[0])

        # quick sanity check for year
        if not payment[1] > 2000:
            print("Year is not in range", payment)
            raise
        # quick sanity check for month
        if not payment[2] > 0 or not payment[2] < 13:
            print("Month is not in range", payment)
            raise
        # quick sanity check for day
        if not payment[3] > 0 or not payment[3] < 32:
            print("Day is not in range", payment)
            raise

        self.data.append(payment)
        self.fileWrite()

        return 0
