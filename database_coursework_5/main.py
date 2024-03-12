import json

from config import PATH_TO_JSON_EMPLOYERS_ID


with open(PATH_TO_JSON_EMPLOYERS_ID, "r") as file:
    data = json.load(file)

print(data)
for value in data.values():
    print(value)
