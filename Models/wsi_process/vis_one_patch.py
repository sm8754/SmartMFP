import cv2
import matplotlib.pyplot as plt
import json

# visualize specific class image to check if the data generation is right
fig = plt.figure(figsize=(16,16))

p = '\\LSIL\\01S182\\01S182_12.json'
pp = '\\IMG_300000_550000.tif'

with open(p, 'r') as f:
    train_dicts = json.load(f)
img = cv2.imread(pp)
img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

for l in train_dicts:
    x = int(l['x'])
    y = int(l['y'])
    w = int(l['w'])
    h = int(l['h'])


    img = cv2.rectangle(img,(x,y),(x+w-1,y+h-1),(0,255,0),2)
# print(l['class'])

plt.imshow(img)
plt.show()