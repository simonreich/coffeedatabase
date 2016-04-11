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


class cuser(cbase.cbase):
    def userAdd(self, user):
        """ Adds a user to the user database
            user: User as array ["Name", "Mail", "status:active, inactive, auto"]
        """

        if not len(user) == 3:
            print("The given user array has wrong format ([\"Name\", \"Mail\", \"status:active, inactive, auto\"]): ", user)
            raise

        if not user[2] == "active" and not user[2] == "inactive" and not user[2] == "auto":
            print("The given user array has wrong format ([\"Name\", \"Mail\", \"status:active, inactive, auto\"]): ", user)
            raise
    
        # check if name exists and search for highest id
        highid = 0
        for row in self.data:
            if int(row[0]) > highid:
                highid = int(row[0])
            if row[1] == user[0]:
                print("The name " + user[0] + " already exists in user databse.")
                raise

        # standard mail address
        if user[2] == "":
            user[2] = "institut@gwdg.de"

        user.insert(0, highid+1)

        self.data.append(user)
        self.fileWrite()

        return 0


    def getUserById (self, userId):
        """ Returns a user array for given user id
            userId: User id as int
        """

        userId = int(userId)

        userFound = False
        user = []
        for row in self.data:
            if int(row[0]) == userId:
                userFound = True
                user = list(row)
                break

        if not userFound:
            print("The id " + str(userId) + " could not be found in user database.")
            raise

        return user


    def setUser (self, user):
        """ Sets variables of existing user
            user: User as array ["Name", "Mail", "status:active, inactive, auto"]
        """

        if not len(user) == 4:
            print("The given user array has wrong format ([\"Id\", \"Name\", \"Mail\", \"status:active, inactive, auto\"]): ", user)
            raise

        if not user[3] == "active" and not user[3] == "inactive" and not user[3] == "auto":
            print("The given user array has wrong format ([\"Id\", \"Name\", \"Mail\", \"status:active, inactive, auto\"]): ", user)
            raise

        user[0] = int(user[0])

        userFound = False
        counter = 0
        for row in self.data:
            if int(row[0]) == user[0]:
                userFound = True
                self.data[counter] = user
                break
            counter += 1

        if not userFound:
            print("The id " + str(user[0]) + " could not be found in user database.")
            raise

        self.fileWrite()

        return 0

