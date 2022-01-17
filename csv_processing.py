import pprint
pp = pprint.PrettyPrinter(indent=4)
import csv
import json

def csv_to_json(csvFile):
    jsonArr = []
    with open(csvFile, encoding='utf-8-sig') as csvf:
        csvReader = csv.DictReader(csvf)
        for row in csvReader:
            jsonArr.append(row)
        
    # with open(jsonFile, 'w', encoding='utf-8') as jsonf:
    #     jsonf.write(json.dumps(jsonArr, indent=4))
    return jsonArr
	
# csvFile = r'revenue-FRBETREVCS-01042022-81A55EB3B9514093BFDA8576D4E2B532.CSV'
# jsonFile = r'new_file.json'
# csv_to_json(csvFile, jsonFile)