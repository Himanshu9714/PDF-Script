# import PyPDF2

# pdfobj = open('events-FREVNOUT-11162021-A7A5ACECC8AB1DB56E14BD0232ED186F.PDF', 'rb')
# text=''
# pdfread = PyPDF2.PdfFileReader(pdfobj)
# # print(pdfread.isEncrypted)
# # print(pdfread.numPages)
# pageObj = pdfread.getPage(2)
# text = text+pageObj.extractText()
# print(text)


# # with open('file.txt', 'a') as f:
# #     for i in range(10):
# #         pageObj = pdfread.getPage(i)
# #         text = pageObj.extractText()
# #         f.write(text)
    
# # print(pageObj.extractText())


# USING TEXTRACT
# import textract
# text = textract.process('events-FREVNOUT-11162021-A7A5ACECC8AB1DB56E14BD0232ED186F.PDF', method='pdfminer')
# print(str(text))

# with open('pfreaded', 'w') as f:
#     f.write(str(text))

# from tika import parser
# raw = parser.from_file('events-FREVNOUT-11162021-A7A5ACECC8AB1DB56E14BD0232ED186F.PDF')
# print(raw['content'])


import pdfplumber
import re
from datetime import datetime
game = []
game_dct = {}
out = []
buff = []

with pdfplumber.open('events-FREVNOUT-11162021-A7A5ACECC8AB1DB56E14BD0232ED186F.PDF') as f:
    fpage = f.pages[0]
    print(fpage.extract_text())
    extracted = fpage.extract_text()
    print(f"\n\n\n\n{type(extracted)}")
    for c in extracted:
        if c == '\n':
            out.append(''.join(buff))
            buff = []
        else:
            buff.append(c)
    else:
        if buff:
            out.append(''.join(buff))
    print(out, f"\n\n\n{len(out)}")

    participant_rounds = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', 'Final/OT']
    participants = []
    winning_selections = []
    keys = ['name', 'start_date', 'id', 'participants', 'winning_selections']
    
    strptr = 0
    for line in out:
        print("This is line:", line)
        if 'SPORT: ' in line:
            game_dct['name'] = line

        elif re.match(r'[a-zA-Z]+\s[a-zA-Z]+\s[@]+\s[a-zA-Z]+\s[a-zA-Z]+\s\d{2}/\d{2}/\d{4}', line):
            game_dct['date'] = line[-37:-15]
            game_dct['id'] = line[-9:-1]

        elif ("Home" or "Away") in line:
            participants_dct = {}
            pattern = "(?:\d{1}|----)"
            values = re.findall(pattern, line[4:])
            participants_dct['BI'] = re.search(r"(\d{4})", line)[0]
            participants_dct['participant'] = re.search("([a-zA-Z]+\s[a-zA-Z]+)", line)[0] 
            participants_dct['HA'] = "Away" if "Away" in line else "Home"
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
            break
        
    game_dct['pariticipants'] = participants
    game_dct['winning_selections'] = winning_selections
    game.append(game_dct)
    print("\n\n\nResult:", game)