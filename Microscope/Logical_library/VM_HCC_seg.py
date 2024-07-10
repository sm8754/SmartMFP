import time
import torch
import clip
from PIL import Image, ImageDraw, ImageFont, ImageOps
import os
class hccPredictor10:
    def __init__(self, model_name="ViT-B/32"):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model, self.preprocess = clip.load(model_name, device=device)

        weights_dict = torch.load(
            "./weights/ft-hcc-seg10.pth",
            map_location='cuda')
        self.model.load_state_dict(weights_dict, strict=True)
        self.device = device
        self.text = ["A patch of Tumor",
                     "A patch of Normal",
                     "A patch of Background"]
        self.classes = ['Tumor', 'Normal', 'Background']

        self.text_inputs = torch.cat([clip.tokenize(f"A patch of {c}") for c in self.classes]).to(device)

        self.text_features = self.model.encode_text(self.text_inputs)
        self.text_features /= self.text_features.norm(dim=-1, keepdim=True)
        self.font = ImageFont.truetype("arial.ttf", 50)


    def predict(self, image_path, save_flag = True):

        original_image = Image.open(image_path)
        width, height = original_image.size

        rows, cols = height // 256, width // 256

        predictions = []
        tumor_count = 0
        nor_count = 0
        bkg_count = 0

        for i in range(rows):
            for j in range(cols):
                left, upper, right, lower = j * 256, i * 256, (j + 1) * 256, (i + 1) * 256
                image_block = original_image.crop((left, upper, right, lower))
                image = self.preprocess(image_block).unsqueeze(0).to(self.device)

                with torch.no_grad():
                    image_features = self.model.encode_image(image)
                    image_features /= image_features.norm(dim=-1, keepdim=True)
                    similarity = (100.0 * image_features @ self.text_features.T).softmax(dim=-1)
                    max_index = similarity[0].argmax().item()

                predicted_class = self.classes[max_index]
                predictions.append(predicted_class)

                if predicted_class == 'Tumor':
                    tumor_count += 1
                    overlay = Image.new("RGBA", (256, 256), (255, 0, 0, 76))
                    original_image.paste(overlay, (left, upper), overlay)
                if predicted_class == 'Normal':
                    nor_count += 1
                else:
                    bkg_count += 1

        if save_flag:
            original_image.save(image_path)  # Specify your output path
        if tumor_count:
            ret = 1
        else:
            ret = 0

        return ret, tumor_count, nor_count, bkg_count

class hccPredictor20:
    def __init__(self, model_name="ViT-B/32"):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model, self.preprocess = clip.load(model_name, device=device)

        weights_dict = torch.load(
            "./weights/ft-hcc-seg20.pth",
            map_location='cuda')
        self.model.load_state_dict(weights_dict, strict=True)
        self.device = device
        self.text = ["A patch of Tumor",
                     "A patch of Normal",
                     "A patch of Background"]
        self.classes = ['Tumor', 'Normal', 'Background']

        self.text_inputs = torch.cat([clip.tokenize(f"A patch of {c}") for c in self.classes]).to(device)

        self.text_features = self.model.encode_text(self.text_inputs)
        self.text_features /= self.text_features.norm(dim=-1, keepdim=True)
        self.font = ImageFont.truetype("arial.ttf", 50)


    def predict(self, image_path, save_flag = True):

        original_image = Image.open(image_path)
        width, height = original_image.size

        rows, cols = height // 256, width // 256

        predictions = []
        tumor_count = 0
        nor_count = 0
        bkg_count = 0

        for i in range(rows):
            for j in range(cols):
                left, upper, right, lower = j * 256, i * 256, (j + 1) * 256, (i + 1) * 256
                image_block = original_image.crop((left, upper, right, lower))
                image = self.preprocess(image_block).unsqueeze(0).to(self.device)

                with torch.no_grad():
                    image_features = self.model.encode_image(image)
                    image_features /= image_features.norm(dim=-1, keepdim=True)
                    similarity = (100.0 * image_features @ self.text_features.T).softmax(dim=-1)
                    max_index = similarity[0].argmax().item()

                predicted_class = self.classes[max_index]
                predictions.append(predicted_class)

                if predicted_class == 'Tumor':
                    tumor_count += 1
                    overlay = Image.new("RGBA", (256, 256), (255, 0, 0, 76))
                    original_image.paste(overlay, (left, upper), overlay)
                if predicted_class == 'Normal':
                    nor_count += 1
                else:
                    bkg_count += 1

        if save_flag:
            original_image.save(image_path)  # Specify your output path
        if tumor_count:
            ret = 1
        else:
            ret = 0

        return ret, tumor_count, nor_count, bkg_count

hcc_predictor = hccPredictor10()
path = '\\val\\tumor\\2020041365_3\\'
imgs = os.listdir(path)
for img in imgs:
    hcc_predictor.predict(os.path.join(path, img))