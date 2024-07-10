# VLT-OM

## Abstract
Microscopes are indispensable tools for pathologists in routine clinical diagnoses. The advancement
of digital pathology and artificial intelligence (AI) has led to the emergence of a new discipline, 
diagnostic pathological AIs, primarily utilized in clinical settings. However, current AI-assisted 
pathological diagnoses rely on Whole Slide Images (WSIs), limiting the application of models to 
specific tasks and diseases in practice. This approach is labor-intensive, time-consuming, and requires 
substantial storage capacity and costs. To address these challenges, we developed a framework 
featuring a visual-language model-powered, task-adaptive microscope, seamlessly integrated with 
cutting-edge AI technologies. Our system incorporates a large language model to enable automatic 
image acquisition, customized analysis, and user-friendly human-microscope interaction. This AIintegrated microscope is equipped with self-adapted stage movement, lens switching, and key 
parameter adjustments in response to specific language and visual commands. We conducted proofof-concept demonstrations for both tissue and cellular pathology analyses, showcasing the 
microscope’s capabilities in qualitative and quantitative clinical task. The visual-language task-driven 
processing allows the microscope to automatically respond to complex pathological interpretations, 
producing more accurate and enriched diagnostic contents. Our innovation presents a significant 
advancement in the nascent field of smart microscopy for digital pathology. It has the potential to 
facilitate the workflow of AI-assisted pathological diagnosis in routine clinical practice, eliminating 
the need for slide-level pixel scanning, big data storage, and specialized model development.


## Requirements

### Hardware Requirements (Microscope)

Ensure that the system contains sufficient main memory space (minimum: 8 GB) to allow for the connection of microscopes.

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
clip,
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

The data used in this article is currently not publicly available due to privacy reasons. However, you can still download examples from: www. 
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

Start fine-tuning the visual language model. We provide an example of fine-tuning liver cancer. Before doing this, please set the data and model parameters.

```
python VLM_ft_HCC_train.py

python VLM_ft_HCC_test.py

python test_oneshot.py
```
#### Configure substrate library

Refer to the instructions of MM and the local microscope hardware, and configure the library in folder `Microscopr/Logical_library` that including `stage`, `camera`, etc.

### Run the VLT-OM
We use the developed interactive interface to execute VLT-OM. For ChatGPT conversation permissions, 
a password needs to be manually added to the code, which can be obtained on https://platform.openai.com/docs/api-reference/introduction.
Before run, you can test the dialogue permissions of the language model by run `test_llm.py`.
```
python test_gpt.py

python VLT-UI.py
```
Note: Please modify the corresponding path according to your local environment.
