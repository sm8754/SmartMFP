
import torch
import clip
from PIL import Image

def one_test_cervical_cancer_cells(img):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-B/32", device=device)
    weights_dict = torch.load("\\ft-ViT-B-32.pth", map_location='cuda')
    model.load_state_dict(weights_dict, strict=True)
    model.eval()
    image = preprocess(Image.open(img)).unsqueeze(0).to(device)
    text = clip.tokenize(["A patch of NILM", "A patch of HSIL", "A patch of LSIL"]).to(device)
    res = ["A patch of NILM", "A patch of HSIL", "A patch of LSIL", "A patch of ASC-US"]
    with torch.no_grad():

        logits_per_image, logits_per_text = model(image, text)
        probs = logits_per_image.softmax(dim=-1).cpu().numpy()

    print("Label probs:", probs)  # prints: []
    return res[probs.argmax().item()]