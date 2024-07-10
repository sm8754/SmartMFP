import os

root_folder = 'train\\NILM'

for subfolder in os.listdir(root_folder):
    subfolder_path = os.path.join(root_folder, subfolder)

    if os.path.isdir(subfolder_path):
        for image_file in os.listdir(subfolder_path):
            if image_file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
                image_name = os.path.splitext(image_file)[0]
                label_content = ""

                label_file_path = os.path.join(subfolder_path, f"{image_name}.txt")

                with open(label_file_path, 'w') as label_file:
                    label_file.write(label_content)

                print(f"Created label file for {image_name}: {label_file_path}")
