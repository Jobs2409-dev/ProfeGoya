# import json

# with open('data/tasks_provider_a.json', 'r', encoding='utf-8') as f:
#    datos = json.load(f)

# print(datos)



# import csv

# with open('data/tasks_provider_b.csv', 'r') as csvfile:
#    reader = csv.DictReader(csvfile)
#    for row in reader:
#        print(row)


import xml.etree.ElementTree as ET
tree = ET.parse('data/tasks_provider_c.xml')
root = tree.getroot()
for task in root.findall('task'):
    print({
        "title": task.find('title').text,
        "priority": task.find('priority').text,
        "status": task.find('status').text
    })