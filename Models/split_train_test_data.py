import random

with open('\\train\\images_list.txt', 'r') as f:
    lines = f.readlines()

records = {}
for line in lines:
    record_number = line.split('_')[0]
    if record_number not in records:
        records[record_number] = []
    records[record_number].append(line.strip())

train_records = []
test_records = []

for key, items in records.items():
    random.shuffle(items)  #
    split_point = int(len(items) * 0.7)  #
    train_records.extend(items[:split_point])
    test_records.extend(items[split_point:])


with open('\\train\\train.txt', 'w') as f:
    for item in train_records:
        f.write(item + '\n')

with open('\\train\\test.txt', 'w') as f:
    for item in test_records:
        f.write(item + '\n')
