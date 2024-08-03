# Next-Generation Smart Microscopy

## Abstract
Microscopes are essential partners for pathologists in routine clinical diagnoses. However, current AI-assisted solutions primarily rely on Whole Slide Images (WSIs), which overlook the development of generic microscopes in intelligent pathology. WSI-based AI solutions are labor-intensive, time-consuming, and require substantial storage capacity and costs. Here, we developed a Visual-Language Task-driven (VLT) framework that seamlessly integrates visual and language foundation models with widely used forms of microscopy. VLT enables automatic image acquisition, customized analysis, and other intuitive human-microscope interactions. VLT features self-adaptive stage movement, lens switching, and key parameter adjustments in response to language commands and visual cues. Proof-of-concept evaluations, including cancer diagnosis and quantitative assessments, demonstrate the efficacy of VLT. The VLT-powered microscope offers an efficient and economical solution for AI-assisted intelligent pathology, eliminating the need for slide-level pixel scanning, extensive data storage, and specialized model development.


## Requirements

### Hardware Requirements (Microscope)

Please ensure that the system has enough main memory space (minimum: 8 GB) to allow for the connection of microscopes.

Use the free Micro Manager (MM) software to configure a local electric microscope and connect controllable components to the computer through a serial port.
The MM package and detailed tutorials can be obtained from https://micro-manager.org/. Or use a more convenient SDK managed by the microscope supplier.

#### others
- GPU: Nvidia 1080Ti or better (at least 10G memory)

- CPU: Intel i5 or better

### Software Stacks

- CUDA, CUDNN (Essential for PyTorch to enable GPU-accelerated deep neural network training and inferring. See https://docs.nvidia.com/cuda/cuda-installation-guide-linux/ .
)

- System: Win 7 or better

- Nvidia GPU corresponding driver

- Python,
openai,
Tensorboard,
torch,
Numpy,
Opencv-python,
Scikit-learn
```
pip install xxx (Dependency packages for requirements)
```
- OpenSlide

OpenSlide is a library to read slides. See the installation guide in https://github.com/openslide/openslide .

## Usage

### Fine-tune a machine assisted diagnostic model

#### Dataset
Download the corresponding dataset from the website. The cervical and liver datasets related to this paper can be obtained from the following sources:
- Mendeley Liquid Based Cytology dataset : https://data.mendeley.com/datasets/zddtpgzv63/4.
- Herlev Pap Smear dataset: https://mde-lab.aegean.gr/index.php/downloads/.
- SIPaKMeD Pap Smear dataset: https://www.cs.uoi.gr/~marina/sipakmed.html.
- Opened HCC dataset: https://portal.gdc.cancer.gov/.

The data used in this article is currently not publicly available due to privacy reasons.
More samples for evaluation can be obtained on reasonable requests by contacting the corresponding author.

#### Prepare data for fine-tuning

Convert WSI `.kfb` from the Department of Pathology to a pyramid graph `.svs` and obtain annotated image blocks at `level=0`.

Executing the following code can prepare fine-tuning for the dataset, such as obtaining the semantics of images and creating labels for them.

```
python kfb_to_svs.py

python celldata_generation.py

python Generate_text_for_images.py

python split_train_test_data.py
```

#### Fine-tune and evaluate the models

Start fine-tuning the VFM model. We provide an example of fine-tuning liver cancer. Before doing this, please set the data and model parameters.

```
python VFM_ft_HCC_train.py

python VFM_ft_HCC_test.py

python test_oneshot.py
```
#### Configure substrate library

Refer to the instructions of MM and the local microscope hardware, and configure the library in folder `Microscopr/Logical_library` that including `stage`, `camera`, etc.

### Run the VLT
We use the developed interactive interface to execute VLT. For LFM conversation permissions, 
a password needs to be manually added to the code, which can be obtained on https://platform.openai.com/docs/api-reference/introduction.
Before run, you can test the dialogue permissions of the language model by run `test_lfm.py`.
```
python test_lfm.py

python VLT-UI.py
```
Note: Please modify the corresponding path according to your local environment.
