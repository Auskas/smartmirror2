import json

unicodeData= {
    "string1": "ЧАСЫ",
}
print("unicode Data is ", unicodeData)

with open('test.txt', 'w') as file:
    encodedUnicode = json.dump(unicodeData, file, ensure_ascii=False) # use dump() method to write it in file
print("JSON character encoding by setting ensure_ascii=False", encodedUnicode)
print(encodedUnicode)
print("Decoding JSON", json.loads(encodedUnicode))