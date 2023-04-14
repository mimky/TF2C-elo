# TF2C-elo
Calculates winrate for each player added up in given tf2c lobby. 
Different stats for each class, pulls data from player's trends.tf profile.
Only takes into account the first two pages of a player's logs on trends.tf. (Usually ~6 months)
Once calculated, it compares the average winrates of both teams to predict who will win. 
The number you see in parenthesis next to the winrate represents how many TF2C logs it's pulling from.
## Usage
Can be used to determine which team to play on. Simply paste the raw lobby link

`https://tf2center.com/lobbies/xxxxxxx`

into the command line. The program will do the rest.
The same lobby can be calculated multiple times without having to paste the link again, just press enter. Other lobbies can be calculated as well in the same instance of the script. Simply paste the new lobby link in.

## Requirements
[Python 3.x](https://www.python.org/downloads/)

[Git](https://git-scm.com/downloads/)

Once these are installed, navigate to a folder you would like this script to be in, then clone the repo with:
```
git clone https://github.com/mimky/TF2C-elo/
```
Next, run `install_requirements.bat` to install the required modules.
