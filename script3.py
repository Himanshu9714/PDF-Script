import pdfplumber
import re
from datetime import datetime
import pprint
pp = pprint.PrettyPrinter(indent=4)
import time
start = time.time()

def add_game(participants, winning_selections, inner_game_dct, game):
    inner_game_dct['pariticipants'] = participants
    inner_game_dct['winning_selection'] = winning_selections
    game.append(inner_game_dct)
    return game

def pages_of_pdf_in_string(filename):
    out = []
    buff = []
    with pdfplumber.open(filename) as f:
        extracted = ''
        for page_no in range(0,50):
            fpage = f.pages[page_no]
            extracted = extracted + fpage.extract_text()
        
        for c in extracted:
            if c == '\n':
                out.append(''.join(buff))
                buff = []
            else:
                buff.append(c)
        else:
            if buff:
                out.append(''.join(buff))
    return out    

def pages_of_pdf_in_list(out):
    lst = []
    new_lst = []
    is_dup = None
    for l in out:
        if l.startswith('IGT Margin Maker') or l.startswith('Event Outcome Report') or l.startswith('SuperBook'): continue
        if l.startswith('SPORT: '):
            if is_dup!=None:
                if is_dup == l:continue
                else:
                    new_lst.append(lst)
            lst = []
            lst.append(l)
            is_dup = l
        else: 
            if lst != None:
                lst.append(l)
    new_lst.append(lst)
    out.clear()
    return new_lst

def pdf_processing(filename):
    events = []
    game_dct = {}

    out = pages_of_pdf_in_string(filename)
    new_lst = pages_of_pdf_in_list(out)

    participant_rounds = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', 'Final/OT']

    game_dct = {}
    game = []
    inner_game_dct = {}
    participants = []
    participants_dct = {}
    winning_selections = []
    winning_selections_dct = {}
    winning_selections_flag = False
    for lst in new_lst:
        for line in lst:      
            if line.startswith('SPORT: '):
                if participants != [] and winning_selections != []:
                    add_game(participants, winning_selections, inner_game_dct, game)

                    participants = []
                    winning_selections = []
                    game_dct = {}
                    game = []
                game_dct['name'] = line

            elif re.match(r'([a-zA-Z]|\s|[\,\/\+\-\&\.\:]|\w)+[@]([a-zA-Z]|\s|[\,\/\+\-\&\.\:\?\(\)]|\w|)+\s\d{2}/\d{2}/\d{4}', line):
                if participants != [] and winning_selections != []:
                    add_game(participants, winning_selections, inner_game_dct, game)

                    participants = []
                    winning_selections = []
                inner_game_dct = {}
                inner_game_dct['date'] = line[-37:-15]
                inner_game_dct['id'] = line[-9:-1]

            elif (("Away" in line) or ("Home" in line)) and (re.search('\(\d+\.\d\)',line)==None):
                winning_selections_flag = False
                participants_dct = {}
                pattern = "(?:\d{1}|----)"
                BI = re.search(r"(\d{2,6})", line)
                if BI:
                    participants_dct['BI'] = BI[0]
                else:
                    participants_dct['BI'] = ''
                
                participants_dct['HA'] = "Away" if "Away" in line else "Home"
                if len(participants_dct['BI'])==0 and line.index(participants_dct['HA'])==0:
                    participants_dct['participant'] = ''
                else:
                    participants_dct['participant'] = line[len(participants_dct['BI']):line.index(participants_dct['HA'])-1]
                values = re.findall(pattern, line[4:])

                for indx in range(len(participant_rounds)):
                    participants_dct[participant_rounds[indx]] = values[indx]
                if len(participants_dct) == 13:
                    if not participants_dct in participants:
                        participants.append(participants_dct)
                    else: continue
        
            elif "Market Name" in line:
                winning_selections_flag = True
            
            elif winning_selections_flag:
                try:
                    check_continued_new_line = re.search('\(\d+\.\d\)', line)
                    BIP = line.startswith('BIParticipant')
                    WinSel = line.startswith("Winning Selections")
                    bet_end = line.startswith("Bet End Market")
                    mtchh = re.search('([a-zA-Z]|\s|/)+[@]([a-zA-Z]|\s|/)+', line)

                    if (check_continued_new_line == None) and (not BIP) and (not WinSel) and (not bet_end) and (mtchh==None):
                        winning_selections_dct['winning_selection'] += line
                        continue
                except: pass

                winning_selections_dct = {}
                dates = re.findall("(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2} (?:am|pm)|-----)", line)
                try:
                    if line.index(dates[0]) != 0:
                        dates.append('')
                        dates[0], dates[1] = dates[1], dates[0]
                except:pass

                if len(dates)>2: dates.pop()
                if len(dates) != 2: continue
                winning_selections_dct['bet_end'] = dates[0]

                market_name = re.search("([a-zA-Z]|\s|/|\d|\w|\([a-zA-Z\s|\d|(\.|\+)?]+\)|[\.\-\+\?\&\'])+\(\d+\.\d\)", line)[0]
                market_name_ind = market_name.find(" am " if " am " in market_name else " pm ")
                if market_name_ind>-1:
                    market_name = market_name[market_name_ind+4:]
                winning_selections_dct['market_name'] = market_name
                winning_selections_dct['set_results'] = dates[1]

                l = len(line)
                p = line.find(" am " if " am " in line else " pm ", l//2, l)
                if p>-1:
                    winning_selections_dct['winning_selection'] = line[p+4:]
                else:
                    if '-----' in line:
                        dash_ind = line.index('-----')
                        winning_selections_dct['winning_selection'] = line[dash_ind+6:]
                    else:
                        winning_selections_dct['winning_selection'] = '-----'
                if winning_selections_dct in winning_selections:continue
                else:winning_selections.append(winning_selections_dct)

        game_dct['game'] = game
        if not game_dct in events:
            events.append(game_dct)

    try:
        if participants != [] and winning_selections != []:
            add_game(participants, winning_selections, inner_game_dct, game)
    except: pass

    if game_dct!={} and game_dct not in events:
        events.append(game_dct)
        
    print("\n\n\n**************\n\n\n\n\*************\n\nResult******\n\n\n")
    return events
events = pdf_processing('events-FREVNOUT-11162021-A7A5ACECC8AB1DB56E14BD0232ED186F.PDF')
pp.pprint(events)
end = time.time()
print(f"\n\n\nTotal taken time: {end-start}")