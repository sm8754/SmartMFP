import os
import json
import openslide


def process_svs_files(folder_a, folder_b):
    if not os.path.exists(folder_b):
        os.makedirs(folder_b)

    for file in os.listdir(folder_a):
        if file.endswith('.svs'):
            svs_file_path = os.path.join(folder_a, file)
            svs_file_name = os.path.splitext(file)[0]
            json_file_path = svs_file_path.replace('.svs', '.json')

            if os.path.exists(json_file_path):
                with open(json_file_path, 'r') as json_file:
                    annotations = json.load(json_file)

                slide = openslide.OpenSlide(svs_file_path)
                slide_width, slide_height = slide.dimensions

                svs_folder_path = os.path.join(folder_b, svs_file_name)
                if not os.path.exists(svs_folder_path):
                    os.makedirs(svs_folder_path)

                for annotation in annotations:
                    x, y, w, h, class_name = int(annotation['x']), int(annotation['y']), int(annotation['w']), int(
                        annotation['h']), annotation['class']

                    if w <= 0 or h <= 0:
                        continue

                    x = max(0, min(x, slide_width - w))
                    y = max(0, min(y, slide_height - h))

                    region = slide.read_region((x, y), 0, (w, h))

                    image_name = f"cell_{x}_{y}_{w}_{h}_{class_name}.png"
                    image_path = os.path.join(svs_folder_path, image_name)
                    region.save(image_path)

    print(f"Processing complete. Images saved in {folder_b}")


folder_a = "G:\\TCT_ZJU\\dierpi\\lsil"
folder_b = "E:\\CCA\\dataset\\ZJU_dataset\\Remarked\\single_cell\\LSIL"

process_svs_files(folder_a, folder_b)
