import os

directory_path = 'Cell_\\HSIL'
bingli_list = []
for j in os.listdir(directory_path):
    bingli_list.append(j)


for bl in bingli_list:
    file_names = []
    for filename in os.listdir(os.path.join(directory_path, bl)):
        if filename.endswith('.png'):
            file_names.append(os.path.splitext(filename)[0])
    output_file = os.path.join(directory_path, bl) + '\\filelist.txt'
    with open(output_file, 'w') as file:
        for name in file_names:
            file.write(name + '\n')

    print(f'Files have processed to {output_file}')
