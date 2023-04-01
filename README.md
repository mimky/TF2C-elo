# TF2C-elo
Calculates winrate for each player added up in given tf2c lobby. 
Different stats for each class, pulls data from player's trends.tf profile.
Only takes into account recent lobbies played. Anything from >3 months ago will likely not be calculated.
Once calculated, it compares the average winrates of both teams to predict who will win.
## Usage
Can be used to determine which team to play on. Simply paste the raw lobby link

`https://tf2center.com/lobbies/xxxxxxx`

into the command line. The program will do the rest.

## Requirements
[Python 3.x](https://www.python.org/downloads/)

[Git](https://git-scm.com/downloads/)

Once these are installed, navigate to a folder you would like this script to be in, then clone the repo with:
```
git clone https://github.com/mimky/TF2C-elo/
```
Next, run `install_requirements.bat` to install the required modules.
