import torch
import clip
from PIL import Image
import numpy as np


class CCAPredictor10:
    def __init__(self, model_name="ViT-B/32"):

        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_name = model_name
        self.device = device
        self.text = ["A patch of NILM.",
                     "A patch of Positive.", "A patch of Background."
                     ]
        self.classes = ['NILM', 'Positive', 'BKG']
        self.text_inputs = torch.cat([clip.tokenize(f"A patch of {c}") for c in self.classes]).to(device)
        self.text_features = self.model.encode_text(self.text_inputs)
        self.text_features /= self.text_features.norm(dim=-1, keepdim=True)
        self.model, self.preprocess = clip.load(self.model_name, device=self.device)
        weights_dict = torch.load(
            "./weights/ft-cca-screening_10.pth",
            map_location='cuda')
        self.model.load_state_dict(weights_dict, strict=True)

    def split_image(img, block_size=(512, 512), overlap=128):

        blocks = []
        step = block_size[0] - overlap  # Step size derived from block size and overlap
        for y in range(0, img.shape[0] - block_size[0] + 1, step):
            for x in range(0, img.shape[1] - block_size[1] + 1, step):
                block = img[y:y + block_size[0], x:x + block_size[1]]
                blocks.append(block)
        return blocks

    def predict(self, image_path):
        image_path = Image.open(image_path)
        blocks = self.split_image(image_path)
        positive_probs = []
        for block in blocks:
            image = self.preprocess(Image.open(block)).unsqueeze(0).to(self.device)

            with torch.no_grad():
                image_features = self.model.encode_image(image)
            image_features /= image_features.norm(dim=-1, keepdim=True)

            similarity = (100.0 * image_features @ self.text_features.T).softmax(dim=-1)
            predicted_class = self.classes[similarity[0].argmax().item()]
            max_index = similarity[0].argmax().item()
            print(self.text[max_index])

            if predicted_class == 'positive':
                positive_probs.append(similarity[0].argmax())


        if positive_probs:
            return 'positive', np.mean(positive_probs)
        else:
            return 'negative', 0


class CCAPredictor20:
    def __init__(self, model_name="ViT-B/32"):

        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_name = model_name
        self.device = device
        self.text = ["A patch of NILM.",
                     "A patch of LSIL.",
                     "A patch of HSIL.",
                     "A patch of ASCUS.",
                     "A patch of Background."
                     ]
        self.classes = ['NILM', 'LSIL', 'HSIL', 'ASCUS', 'BKG']
        self.text_inputs = torch.cat([clip.tokenize(f"A patch of {c}") for c in self.classes]).to(device)\

        self.model, self.preprocess = clip.load(self.model_name, device=self.device)
        weights_dict = torch.load(
            "./weights/ft-cca-class.pth",
            map_location='cuda')
        self.model.load_state_dict(weights_dict, strict=True)

    def predict(self, image_path, lens):

        self.text_features = self.model.encode_text(self.text_inputs)
        self.text_features /= self.text_features.norm(dim=-1, keepdim=True)

        image = self.preprocess(Image.open(image_path)).unsqueeze(0).to(self.device)

        with torch.no_grad():
            image_features = self.model.encode_image(image)
        image_features /= image_features.norm(dim=-1, keepdim=True)

        similarity = (100.0 * image_features @ self.text_features.T).softmax(dim=-1)
        predicted_class = self.classes[similarity[0].argmax().item()]
        max_index = similarity[0].argmax().item()
        print(self.text[max_index])
        return predicted_class, similarity[0].argmax()

if __name__ == '__main__':
    clip_predictor = CCAPredictor10()
    text_result = clip_predictor.predict("\\01S144_88.jpg")
    print(text_result)
