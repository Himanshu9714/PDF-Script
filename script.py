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
import pprint
pp = pprint.PrettyPrinter(indent=4)

game = []
game_dct = {}
out = []
buff = []
is_duplicate_sport_str = None

with pdfplumber.open('events-FREVNOUT-11162021-A7A5ACECC8AB1DB56E14BD0232ED186F.PDF') as f:
    for page_no in range(2):
        fpage = f.pages[page_no]
        # print(fpage.extract_text())
        extracted = fpage.extract_text()
        
        # print(f"\n\n\n\n{type(extracted)}")
        for c in extracted:
            if c == '\n':
                out.append(''.join(buff))
                buff = []
            else:
                buff.append(c)
        else:
            if buff:
                out.append(''.join(buff))
        # print(out, f"\n\n\n{len(out)}")

        participant_rounds = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', 'Final/OT']

        participants = []
        winning_selections = []
        participants_dct = {}
        winning_selections_dct = {}
        game_dct['name'] = ''
        for line in out:
            if 'SPORT: ' in line:
                if is_duplicate_sport_str == line:
                    continue
                game.append(game_dct)
                game_dct = {}
                participants = []
                winning_selections = []
                # print(f"\n\nThis is sport block game dict:{game_dct}\n\n")
                game_dct['name'] = line
                is_duplicate_sport_str = line
                print("Duplicaqte", is_duplicate_sport_str)
                print("The game appended:")
                # pp.pprint(game)
            

            elif re.match(r'[a-zA-Z]+\s[a-zA-Z]+\s[@]+\s[a-zA-Z]+\s[a-zA-Z]+\s\d{2}/\d{2}/\d{4}', line):
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
                game_dct['pariticipants'] = participants
       
            elif "Match Winner" in line:
                winning_selections_dct = {}
                
                dates = re.findall("\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2} (?:am|pm)", line)
                winning_selections_dct['bet_end'] = dates[0]
                winning_selections_dct['market_name'] = re.search("Match Winner \(\d+\.\d\)", line)[0]
                winning_selections_dct['set_results'] = dates[1]
                lst = line.split(' ')
                winning_selections_dct['winning_selection'] = lst[-2] + " " + lst[-1]
                winning_selections.append(winning_selections_dct)
                game_dct['winning_selection'] = winning_selections
            # print("Second Duplicaqte", is_duplicate_sport_str)
            
        game_dct['pariticipants'] = participants
        game.append(game_dct)
        # pp.pprint(game_dct)
# print("\n\n\n\n\n\*********************\n\n\n\n\*************\n\nResult******\n\n\n")
pp.pprint(game)