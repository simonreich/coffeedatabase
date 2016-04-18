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

        if not str(user[2]) == "active" and not str(user[2]) == "inactive" and not str(user[2]) == "auto":
            print("The given user array has wrong format ([\"Name\", \"Mail\", \"status:active, inactive, auto\"]): ", user)
            raise
    
        # check if name exists and search for highest id
        highid = 0
        for row in self.data:
            if int(row[0]) > highid:
                highid = int(row[0])
            if row[1] == user[0]:
                print("The name " + str(user[0]) + " already exists in user database: ", row)
                raise

        user.insert(0, highid+1)

        self.data.append(user)
        self.fileWrite()

        return 0


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


    def getNamelist (self):
        """ Returns array of all names in database.
        """

        return self.getColumn(1)


    def getUserByName(self, name):
        """ Returns user as array ["Name", "Mail", "status:active, inactive, auto"]
            name: Name as string.
        """

        name = str(name)

        nameFound = False
        for row in self.data:
            if row[1] == name:
                nameFound = True
                break

        if not nameFound:
            print("Could not find name: " + str(name))
            raise

        # search for multiple entries
        matching = [s for s in self.getNamelist() if name in s]
        if len(matching) > 1:
            raise NameError("Found user " + str(name) + " text multiple times in name database. Names found: ", matching)

        return row


    def getUserById(self, userid):
        """ Returns user as array ["Name", "Mail", "status:active, inactive, auto"]
            userid: Id as int.
        """

        userid = int(userid)

        return self.getRowById(userid)
