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


######################################################




######################################################
## No Configuration after this
######################################################


# system
import sys

# coffeedatabase
from lib import ckeyboard


# print help
def printHelp (programname):
    """ Gibt einen Hilfetext auf den Bildschirm aus.
    """
    text = "Usage: " + programname + (" [OPTION]\n"
           "  -h, --hilfe, --help       Dieser Hilfetext.")

    print(text)

    return 0


# main function
def main(argv=None):
    """ main function
        argv: possible arguments, will be replaced by sys.argv if none are 
              given.
    """
    if argv is None:
        argv = sys.argv

    for arg in argv:
        if (arg == "-h" or
                arg == "-help" or
                arg == "--help" or
                arg == "-hilfe" or
                arg == "--hilfe" or
                arg == "-?" or
                arg == "--?" or
                arg == "?"):
            printHelp(sys.argv[0])

        elif(arg == "--useradd" or
                arg == "-ua" or
                arg == "ua"):
            keyboard = ckeyboard.ckeyboard()
            keyboard.userAdd()

        elif(arg == "--userchange" or
                arg == "-uc" or
                arg == "uc"):
            keyboard = ckeyboard.ckeyboard()
            keyboard.userChangeInfo()

        elif(arg == "--paymentadd" or
                arg == "-pa" or
                arg == "pa"):
            keyboard = ckeyboard.ckeyboard()
            keyboard.paymentAdd()

        elif(arg == "--itemadd" or
                arg == "-ia" or
                arg == "ia"):
            keyboard = ckeyboard.ckeyboard()
            keyboard.itemAdd()

        elif(arg == "--itemchange" or
                arg == "-ic" or
                arg == "ic"):
            keyboard = ckeyboard.ckeyboard()
            keyboard.itemChangeInfo()

        elif(arg == "--markadd" or
                arg == "-ma" or
                arg == "ma"):
            keyboard = ckeyboard.ckeyboard()
            keyboard.marksAdd()

        elif(arg == "--markaddall" or
                arg == "-maa" or
                arg == "maa"):
            keyboard = ckeyboard.ckeyboard()
            keyboard.marksAddAll()

        elif(arg == "--priceadd" or
                arg == "-pra" or
                arg == "pra"):
            keyboard = ckeyboard.ckeyboard()
            keyboard.priceAdd()

        elif(arg == "--pricefill" or
                arg == "-prf" or
                arg == "prf"):
            keyboard = ckeyboard.ckeyboard()
            keyboard.priceFill()

        elif(arg == "--balancecheck" or
                arg == "-bc" or
                arg == "bc"):
            keyboard = ckeyboard.ckeyboard()
            keyboard.balanceCheck()

        elif(arg == "--balanceexportpdf" or
                arg == "-bep" or
                arg == "bep"):
            keyboard = ckeyboard.ckeyboard()
            keyboard.balanceExportPDF()

        elif(arg == "--listexportpdf" or
                arg == "-lep" or
                arg == "lep"):
            keyboard = ckeyboard.ckeyboard()
            keyboard.listExportPDF()

        elif(arg == "--temp" or
                arg == "-t" or
                arg == "t"):
            keyboard = ckeyboard.ckeyboard()
            keyboard.temp()

        elif(len(sys.argv) == 1):
            printHelp(sys.argv[0])

    # Ende
    sys.exit(0)


if __name__ == "__main__":
    main()
