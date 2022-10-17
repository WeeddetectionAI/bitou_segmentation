# The basic semantic segmentation as outlined in the pytorch flash documentation [here](https://lightning-flash.readthedocs.io/en/latest/reference/semantic_segmentation.html)

import torch

from pytorch_lightning import seed_everything

import flash
# from flash.core.data.utils import download_data
from flash.image import SemanticSegmentation, SemanticSegmentationData

from PIL import Image

# 1. Create the DataModule
# The data was generated with the  CARLA self-driving simulator as part of the Kaggle Lyft Udacity Challenge.
# More info here: https://www.kaggle.com/kumaresanmanickavelu/lyft-udacity-challenge
# download_data(
#     "https://github.com/ongchinkiat/LyftPerceptionChallenge/releases/download/v0.1/carla-capture-20180513A.zip",
#     "./data",
# )

# fixing the seed for reproducibility
seed_everything(42)

datamodule = SemanticSegmentationData.from_folders(
    train_folder="data/bitou_test",
    train_target_folder="data/bitou_test_masks",
    val_split=0.2,
    transform_kwargs=dict(image_size=(512, 512)),
    num_classes=3,
    batch_size=4,   # MEMORY
    num_workers=4,
    pin_memory=True
)

# 2. Build the task
model = SemanticSegmentation(
    backbone="mobilenetv3_large_100",       #   mobilenetv3_large_100
    head="deeplabv3",
    num_classes=datamodule.num_classes,
)

# 3. Create the trainer and finetune the model
trainer = flash.Trainer(max_epochs=30, gpus=torch.cuda.device_count())
trainer.finetune(model, datamodule=datamodule, strategy="freeze")  # strategy="no-freeze"

# 4. Segment a few images!
predict_files = [
        "data/bitou_test/DJI_20220404135834_0005.JPG",
        "data/bitou_test/DJI_20220404140510_0016.JPG",
        "data/bitou_test/DJI_20220404141042_0026.JPG"
    ]
datamodule = SemanticSegmentationData.from_files(
    predict_files=predict_files,
    batch_size=3,
)
predictions = trainer.predict(model, datamodule=datamodule)
print(predictions)

# 5. Save the model!
trainer.save_checkpoint("results/tmp/bitou_3class_512_deeplabv3_mnetv3large_overfit_freeze.pt")