# coffeedatabase

## Features

This program manages a coffee account list for an office environment:

 - People pay in advance roughly the amount of money they expect to drink coffee and/or milk.
 - Next to the coffee machine there is a list and a person makes a mark if coffee and/or milk is taken.
 - At the end of the month the list is manually added to the coffee database.

 The script performs:

 - Keeps the balance of how much coffee and/or milk was used for every person.
 - Keeps the money balance for every person.
 - Creates a list, which can be put next to the coffee machine and where people can make their mark.
 - Creates a monthly balance cheet, detailing how much coffee and/or milk every person drank and detailing their money balance.
 - Creates a web page with personalized coffee statistics and some fun overall statistics.

## Installation

Clone coffeedatabase

```bash
git clone https://github.com/simonreich/coffeedatabase.git
cd coffeedatabase
python ./coffee.py
```

Optional: install a local virtual environment for Python. The only dependency is numpy.

```bash
cd coffeedatabase
virtualenv -p python3 ./
source bin/activate
pip install numpy
```

## Usage

| Parameter | Description |
|-----------|-------------|
| `--useradd`, `-ua`, `ua` | Adds a new user to the database. The new user is appended to the file `user.csv`.|
| `--userchange`, `-uc`, `uc` | Allows to search for a user in the database and change his/her info. The user's data in `user.csv` is directly manipulated.|
| `--paymentadd`, `-pa`, `pa` | Allows to search for a user in the database and adds a payment to the user's money balance. The new payment is appended to the file `payment.csv`.|
| `--itemadd`, `-ia`, `ia` | Adds a new item to the item's list, e.g. coffee, milk, or sugar. Usually, this is only done once when setting up the list. The new item is appended to the file `item.csv`.|
| `--itemchange`, `-ic`, `ic` | Allows to search for an item in the database and change its info. The item's data in `item.csv` is directly manipulated.|
| `--markadd`, `-ma`, `ma` | Allows to search for a user in the database and add marks from the marks list next to the coffee machine to the user's account. The new marks are appended to the file `markx.csv`, where x is the item's id.|
| `--markaddall`, `-maa`, `maa` | The same as `--markadd`, except the program asks for marks in the same order as people are listed in the marks list next to the coffee machine. This allows for fast adding of marks at the end of months. The new marks are appended to the file `markx.csv`, where x is the item's id.|
| `--priceadd`, `-pra`, `pra` | Adds a new price to an item. The new price is added to the file `price.csv`. This allows for changing prices, for example if the coffee price needs to be raised (something, that should never happen!)|
| `--pricefill`, `-prf`, `prf` | The program asks for any missing prices, e.g. all items without a price are presented. The new price is added to the file `price.csv`.|
| `--balancecheck`, `-bc`, `bc` | Allows to search for a user in the database and ckecks the user's money balance.|
| `--balanceexportpdf`, `-bep`, `bep` | Exports the balance for all users for one specific month to pdf. This is done via `Latex` and `pdflatex` needs to be installed. Furthermore, the data for the web page is generated.|
| `--listexportpdf`, `-lep`, `lep` | Generates a list with all users and all items. This list can be placed next to the coffee machine and people can make their marks on this list. This is done via `Latex` and `pdflatex` needs to be installed. |

## Generating pdfs

The program expects a functional `pdflatex` installation. The tex template files can be found in the folder `template` and can be adapted to your needs.

## Web page

The parameter `--balanceexportpdf` creates a web page in the `out` folder. Plots are generated via `gnuplot` and the plotting scripts are also placed in the `out` folder. The web page itself is exported in markdown and can be read, for example, by the static site generator [Nikola](https://getnikola.com/).

Your pipeline for the web page should be as follows:

 1. Run `--balanceexportpdf`.
 2. Execute `gnuplot *.plot` in the `out` folder.
 3. Use `rsync` to copy all resulting `png` files into the nikola workspace.
 3. Use `rsync` to copy all resulting `md` files into the nikola workspace.
 3. Execute `nikola build` inside the nikola workspace.
 4. Execute `nikola deploy` inside the nikola workspace.
 5. Have fun.
