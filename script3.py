import pdfplumber
import re
from datetime import datetime
import pprint
pp = pprint.PrettyPrinter(indent=4)

game = []
game_dct = {}
out = []
buff = []
is_duplicate_sport_str = None
new_lst = []

with pdfplumber.open('events-FREVNOUT-11162021-A7A5ACECC8AB1DB56E14BD0232ED186F.PDF') as f:
    extracted = ''
    for page_no in range(11):
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

    lst = []
    is_dup = None
    cnt = 0
    for l in out:
        cnt += 1

        print("Line: ", l)
        if l.startswith('SPORT: '):
            if is_dup!=None:
                print("\n\nLine sport:", l)
                print("\n\nDuplicate is_dup:", is_dup)
                if is_dup == l:continue
                else:
                    new_lst.append(lst)
            lst = []
            lst.append(l)
            is_dup = l
        else: 
            if lst != None:
                lst.append(l)
                print("Appended:", l)

    new_lst.append(lst)


    participant_rounds = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', 'Final/OT']

    for lst in new_lst:
        game_dct = {}
        participants = []
        participants_dct = {}
        winning_selections = []
        winning_selections_dct = {}
        for line in lst:
            print("This is line:", line)
            if 'SPORT: ' in line:
                game_dct['name'] = line

            elif re.match(r'([a-zA-Z]|\s|/)+[@]([a-zA-Z]|\s|/)+\s\d{2}/\d{2}/\d{4}', line):
                game_dct['date'] = line[-37:-15]
                game_dct['id'] = line[-9:-1]

            elif ("Away" in line) or ("Home" in line):
                participants_dct = {}
                pattern = "(?:\d{1}|----)"
                BI = re.search(r"(\d{4})", line)
                if BI:
                    participants_dct['BI'] = BI[0]
                else:
                    participants_dct['BI'] = ''
                participants_dct['participant'] = re.search("([a-zA-Z]+\s[a-zA-Z]+)", line)[0] 
                participants_dct['HA'] = "Away" if "Away" in line else "Home"
                values = re.findall(pattern, line[4:])
                for indx in range(len(participant_rounds)):
                    participants_dct[participant_rounds[indx]] = values[indx]
                if len(participants_dct) == 13:
                    participants.append(participants_dct)
        
            elif "Match Winner" in line:
                winning_selections_dct = {}
                dates = re.findall("\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2} (?:am|pm)", line)
                winning_selections_dct['bet_end'] = dates[0]
                winning_selections_dct['market_name'] = re.search("Match Winner \(\d+\.\d\)", line)[0]
                winning_selections_dct['set_results'] = dates[1]
                lst = line.split(' ')
                winning_selections_dct['winning_selection'] = lst[-2] + " " + lst[-1]
                winning_selections.append(winning_selections_dct)
                
    
        game_dct['pariticipants'] = participants
        game_dct['winning_selection'] = winning_selections
        game.append(game_dct)
        
pp.pprint(game)