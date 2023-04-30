import requests
import re
import html
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from sty import fg, bg, ef, rs
from sty import Style, RgbFg
from prettytable import PrettyTable
os.system('cls')

def start_gui(last_link):
    lobbylink = input('Lobby Link: ')
    if not lobbylink and last_link:
        get_stats(last_link)
    else:
        get_stats(lobbylink)


def get_stats(lobbylink):
    try:
        rawhtml_inp = requests.get(lobbylink).text
    except:
        print('Wrong format.\nExample: https://tf2center.com/lobbies/xxxxxxx\n')
        start_gui(False)
        return
    
    rawhtml_inp = rawhtml_inp.replace('\t', '')
    rawhtml_inp = rawhtml_inp.replace('\r', '')
    
    lines = rawhtml_inp.split("\n")
    non_empty_lines = [line for line in lines if line.strip() != ""]
    rawhtml = ""
    for line in non_empty_lines:
        rawhtml += line + "\n"

    rawhtml = re.sub('''\n<span class="icons donator"></span>''', '', rawhtml) #removes donor tag
    rawhtml = re.sub('''\n<span class="icons person friend"></span>''', '', rawhtml) #removes friend tag
    rawhtml = re.sub('''\n<span class="name friend">''', '''<span class="name">''', rawhtml) #removes friend tag2

    try:
        v1 = re.compile('''<div class="ym-gl playerSlot header">''' + r'(.*?)' + '''<div class="specsLabel">Spectators</div>''', re.DOTALL) #grabs slots/playerdata from rawhtml
        v2 = v1.search(rawhtml).group(1)
        v3 = (v2.split('''<div class="details">''')) #splits v1 into players
    except AttributeError:
        print('Invalid Lobby.\n\n')
        start_gui(False)

    slots = {
    1: '',
    2: '',
    3: '',
    4: '',
    5: '',
    6: '',
    7: '',
    8: '',
    9: '',
    10: '',
    11: '',
    12: ''
    }
    slot_conversion = {
    1: ['Blue1', 'Scout'],
    2: ['Blue2', 'Scout'],
    3: ['Blue1', 'Soldier'],
    4: ['Blue2', 'Soldier'],
    5: ['Blue', 'Demo'],
    6: ['Blue', 'Medic'],
    7: ['Red1', 'Scout'],
    8: ['Red2', 'Scout'],
    9: ['Red1', 'Soldier'],
    10: ['Red2', 'Soldier'],
    11: ['Red', 'Demo'],
    12: ['Red', 'Medic']
    }

    counter = 1
    for i in v3:
        if counter > 12:
            break
        empty = i.count('''<span class="slotIconInner icons slot unavailable"></span>''') #checks to see how many spots are taken after player's slot
            
        try:
            name = html.unescape((re.compile('''<i>\n''' + r'(.*?)' + '''\n</i>''', re.DOTALL)).search(i).group(1)) #HTML library used for unicode characters
            steamID = (re.compile('''href="/profile/''' + r'(.*?)' + '''">''', re.DOTALL)).search(i).group(1)
        except AttributeError:
            counter += empty
            continue
        if '''<span class="icons ''' in name:
            name = re.sub(r'^.*?\n', '', name)
        if '''__cf_email__''' in name:
            #grabs user's name in case of an @ symbol, which breaks the page source and makes it think it's an email
            email_fix = re.compile('''{"steamId":"''' + steamID + '''","playerName":"''' + r'(.*?)' + '''"}''', re.DOTALL)
            name = email_fix.search(rawhtml).group(1)
            
        slots[counter] = [steamID, name]
        
        counter += (empty+1)

    winrate_dict = {
    'Blue1 Scout': '',
    'Blue2 Scout': '',
    'Blue1 Soldier': '',
    'Blue2 Soldier': '',
    'Blue Demo': '',
    'Blue Medic': '',
    'Red1 Scout': '',
    'Red2 Scout': '',
    'Red1 Soldier': '',
    'Red2 Soldier': '',
    'Red Demo': '',
    'Red Medic': ''
    }

    def get_trends(i):
        if not slots[i]:
            return
        ID = (slots[i])[0]
        trends_html = requests.get('''https://trends.tf/player/''' + ID + '''/logs''').text
        tf2c_lobbies = trends_html.split('''TF2Center Lobby ''')[1:]
        mercenary_needed = (slot_conversion[i])[1]
        outcomes = []

        lobbies_played = 0
        for e in tf2c_lobbies:
            mercenary_played = (re.compile('''alt="''' + r'(.*?)' + '''"''', re.DOTALL)).search(e).group(1)
            if mercenary_played != mercenary_needed: #filters out correct class
                continue
            pos1 = [u.start() for u in re.finditer(r'''<td class="left">''', e)] #gets index of gamemode of match
            if len(pos1)>= 2:
                gamemode_played = e[pos1[2]+17:pos1[2]+18]
            if gamemode_played != 's' and gamemode_played != 'p': #checks if gamemode is sixes (p for prolander, sometimes subs make games 7 players)
                continue
            
            pos2 = [u.start() for u in re.finditer(r'''<td class="''', e)] #gets index of outcome of match
            if len(pos2)>= 2:
                outcome = e[pos2[2]+11:pos2[2]+12]
                
            if outcome == 'w':
                outcomes.append(1)
            if outcome == 'l':
                outcomes.append(0)
            if outcome == 't':
                outcomes.append(0.5)
            lobbies_played += 1

        if not outcomes:
            winrate = '??? (0)'
        else:
            winrate = str(round((sum(outcomes)/len(outcomes))*100)) + '% (' + str(lobbies_played) + ')'

        winrate_dict[(slot_conversion[i])[0] + ' ' + (slot_conversion[i])[1]] = [(slots[i])[1], winrate] #format is 'Team Class': [playername, win% & (lobbies played)]
        return


    processes = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        for e in slots:
            executor.submit(get_trends, e)

    blue_winrate_raw = []
    red_winrate_raw = []
    for i in winrate_dict:
        stats = winrate_dict[i]
        if stats: #checks if player exists in slot
            if 'Blue' in i and stats[1] != '??? (0)': #filters team & inconclusive elo
                blue_winrate_raw.append(int((stats[1]).split('%', 1)[0]))
            if 'Red' in i and stats[1] != '??? (0)':
                red_winrate_raw.append(int((stats[1]).split('%', 1)[0]))

    try:
        #total_winrate = sum(blue_winrate_raw)/6 + sum(red_winrate_raw)/6 calculates by dividing by 6
        total_winrate = sum(blue_winrate_raw)/len(blue_winrate_raw) + sum(red_winrate_raw)/len(red_winrate_raw) #divides by player count
    except ZeroDivisionError:
        total_winrate = 100
    try:
        #blue_winrate = round(100*(sum(blue_winrate_raw)/6 / total_winrate)) divides total winrate by 6
        blue_winrate = round(100*(sum(blue_winrate_raw)/len(blue_winrate_raw) / total_winrate)) #divides by player count
    except ZeroDivisionError:
        blue_winrate = 0
    try:
        #red_winrate = round(100*(sum(red_winrate_raw)/6 / total_winrate)) same thing here
        red_winrate = round(100*(sum(red_winrate_raw)/len(red_winrate_raw) / total_winrate))
    except ZeroDivisionError:
        red_winrate = 0

    fg.lightblue = Style(RgbFg(0, 150, 255))
    fg.lighterblue = Style(RgbFg(135,206,235))
    fg.lightgreen = Style(RgbFg(102,255,102))
    fg.lightred = Style(RgbFg(255,102,102))
    fg.pink = Style(RgbFg(255,105,180))

    if blue_winrate > red_winrate:
        bw_printed = (fg.lightgreen + str(blue_winrate) + '%' + fg.rs)
        rw_printed = (fg.red + str(red_winrate) + '%' + fg.rs)
    if blue_winrate < red_winrate:
        bw_printed = (fg.red + str(blue_winrate) + '%' + fg.rs)
        rw_printed = (fg.lightgreen + str(red_winrate) + '%' + fg.rs)
    if blue_winrate == red_winrate:
        bw_printed = (fg.yellow + str(blue_winrate) + '%' + fg.rs)
        rw_printed = (fg.yellow + str(red_winrate) + '% ' + fg.rs)

    printable_wd1 = {}
    for i in winrate_dict:
        try:
            if type((winrate_dict[i])[1]) == int: #if winrate calculated
                printable_wd1[i] = [(winrate_dict[i])[0], str((winrate_dict[i])[1])+'%']
            else: #if winrate unknown (??? (0))
                printable_wd1[i] = winrate_dict[i] 
        except IndexError: #if no player
            printable_wd1[i] = ['', '']
            
    printable_wd2 = {}
    counter = 1
    for i in printable_wd1:
        if counter > 12:
            break
            
        if counter <= 6: #for blue team
            if not (printable_wd1[i])[0]: #if no player
                printable_wd2[i] = printable_wd1[i]
            else:
                if (printable_wd1[i])[1] == '??? (0)':
                    printable_wd2[i] = [fg.lightblue + (printable_wd1[i])[0] + fg.rs, fg.yellow + '??? (0)' + fg.rs]
                else:
                    printable_wd2[i] = [fg.lightblue + (printable_wd1[i])[0] + fg.rs, fg.pink + (printable_wd1[i])[1] + fg.rs]
                    
        if counter > 6: #for red team
            if not (printable_wd1[i])[0]:
                printable_wd2[i] = printable_wd1[i]
            else:
                if (printable_wd1[i])[1] == '??? (0)':
                    printable_wd2[i] = [fg.lightred + (printable_wd1[i])[0] + fg.rs, fg.yellow + '??? (0)' + fg.rs]
                else:
                    printable_wd2[i] = [fg.lightred + (printable_wd1[i])[0] + fg.rs, fg.pink + (printable_wd1[i])[1] + fg.rs]
        counter += 1

    stat_table = PrettyTable([bw_printed, ' ', 'Class', rw_printed, ''])

    stat_table.add_row([(printable_wd2['Blue1 Scout'])[0], (printable_wd2['Blue1 Scout'])[1], 'Scout', (printable_wd2['Red1 Scout'])[0], (printable_wd2['Red1 Scout'])[1]])
    stat_table.add_row([(printable_wd2['Blue2 Scout'])[0], (printable_wd2['Blue2 Scout'])[1], 'Scout', (printable_wd2['Red2 Scout'])[0], (printable_wd2['Red2 Scout'])[1]])
    stat_table.add_row([(printable_wd2['Blue1 Soldier'])[0], (printable_wd2['Blue1 Soldier'])[1], 'Soldier', (printable_wd2['Red1 Soldier'])[0], (printable_wd2['Red1 Soldier'])[1]])
    stat_table.add_row([(printable_wd2['Blue2 Soldier'])[0], (printable_wd2['Blue2 Soldier'])[1], 'Soldier', (printable_wd2['Red2 Soldier'])[0], (printable_wd2['Red2 Soldier'])[1]])
    stat_table.add_row([(printable_wd2['Blue Demo'])[0], (printable_wd2['Blue Demo'])[1], 'Demoman', (printable_wd2['Red Demo'])[0], (printable_wd2['Red Demo'])[1]])
    stat_table.add_row([(printable_wd2['Blue Medic'])[0], (printable_wd2['Blue Medic'])[1], 'Medic', (printable_wd2['Red Medic'])[0], (printable_wd2['Red Medic'])[1]])
    print(stat_table)
    
    start_gui(lobbylink)

start_gui(False)
