# The basic semantic segmentation as outlined in the pytorch flash documentation [here](https://lightning-flash.readthedocs.io/en/latest/reference/semantic_segmentation.html)

from base64 import decode
import torch
import numpy as np

import flash
# from flash.core.data.utils import download_data
from flash.image import SemanticSegmentation, SemanticSegmentationData

from PIL import Image
import matplotlib.pyplot as plt

colour_code = np.array([(220, 220, 220), (128, 0, 0), (0, 128, 0),  # class
                        (192, 0, 0), (64, 128, 0), (192, 128, 0)])  # background

def decode_colormap(labels, num_classes=2):
        """
            Function to decode the colormap. Receives a numpy array of the correct label
        """
        r = np.zeros_like(labels).astype(np.uint8)
        g = np.zeros_like(labels).astype(np.uint8)
        b = np.zeros_like(labels).astype(np.uint8)
        for class_idx in range(0, num_classes):
            idx = labels == class_idx
            r[idx] = colour_code[class_idx, 0]
            g[idx] = colour_code[class_idx, 1]
            b[idx] = colour_code[class_idx, 2]
        colour_map = np.stack([r, g, b], axis=2)
        # colour_map = colour_map.transpose(2,0,1)
        # colour_map = torch.tensor(colour_map)
        # image = image.to("cpu").numpy().transpose(1, 2, 0)
        return colour_map

gpus = "cuda:0"
map_location = {'cpu':'cuda:0'}
model_f = "results/tmp/segmentation_model_overfit.pt"
model = SemanticSegmentation.load_from_checkpoint(model_f,map_location=map_location)
# pretrained_model.eval()
# pretrained_model.freeze()
# y_hat = pretrained_model(x)

# SemanticSegmentation.available_outputs()

# 3. Create the trainer and finetune the model
trainer = flash.Trainer(max_epochs=3, gpus=torch.cuda.device_count())

# 4. Segment a few images!
predict_files = [
        "data/bitou_test/DJI_20220404135614_0001.JPG",
        "data/bitou_test/DJI_20220404140510_0015.JPG",
        "data/bitou_test/DJI_20220404140802_0022.JPG"
    ]
datamodule = SemanticSegmentationData.from_files(
    predict_files=predict_files,
    batch_size=1
)
predictions = trainer.predict(model, datamodule=datamodule, output='preds') # using 'labels' does not work - unknown why. class names? output='preds'
print(predictions)
for i, pred in enumerate(predictions):
    pr = pred[0]
    print(pr.shape)
    label = torch.argmax(pr.squeeze(), dim=0).detach().numpy()
    l = (pr > 0.0).float()
    lab = torch.argmax(pr, dim=0).detach().numpy()
    print(label.shape)
    dec_label = decode_colormap(label, num_classes=2)
    dec_l = decode_colormap(l)
    dec_lab = decode_colormap(lab)

    # 6. Show the images
    imf = predict_files[i] 
    im = Image.open(imf)
    im_arr = np.asarray(im)

    # show the predictions
    fig, axs = plt.subplots(2,2)    
    axs[0,0].imshow(im_arr)
    axs[0,0].set_title("Original")
    axs[0,0].axis('off')

    axs[0,1].imshow(dec_label)
    axs[0,1].set_title("Squeeze")
    axs[0,1].axis('off')

    # axs[1,0].imshow(dec_l)
    # axs[1,0].set_title("larger than 0")
    # axs[1,0].axis('off')

    axs[1,1].imshow(dec_lab)
    axs[1,1].set_title("No squeeze")
    axs[1,1].axis('off')
    plt.show()


