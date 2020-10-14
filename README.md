# Deeplabv3+ BDD100k/drivable_area implementation

[![Results](./images/result.png)](https://www.youtube.com/watch?v=-dzS8VlVmk4&list=PLn3JZxvQvVuAbhz5ep4X-dysT9jLMMQpv)
(Click image to see demo video)

## Introduction

This repository is merged with https://github.com/jfzhang95/pytorch-deeplab-xception and is success of https://github.com/sunggukcha/deeplabv3plus-bdd100k-drivablearea. Please follow installation policies of the repositories above.

For BDD100k/drivable_area semantic segmentation, I added

1. bdd100k drivable area dataloader, and training/val/test scripts.
2. prediction visualization for both color (visual result) and id (greyscale png file for submission).
3. added Group Noramlization.
4. deeplabv3 which is without deeplabv3+ decoder, but with aspp only.
5. WRN as backbone is added (original code from mapillary@github)
6. additional visualization that marks corrects, missed and wrong pixels.
7. IBN-Net by github.com/XingangPan/IBN-Net/
8. EfficientNet added which is implemented by https://github.com/lukemelas/EfficientNet-PyTorch.
9. Feature Pyramid Networks(FPNs) for semantic segmentation added (version: Panoptic Feature Pyramid Networks).

For more detail, please visit the repositories above.

## Experiment & result
  
<span style="color:red">**Single 12GB GPU**</span>

| Backbone  | Normalization | mIoU in test |                                Parameters                                |
| :-------- | :-----------: | :----------: | :----------------------------------------------------------------------: |
| ResNet50  |   Group-16    |    85.00%    | [link](https://www.dropbox.com/s/5kdi0u8pf3ur9jd/resnet50.pth.tar?dl=0)  |
| ResNet101 |   IGN-a-16    |    85.12%    |  [link](https://www.dropbox.com/s/dw9hmcumrothvi9/ign101.pth.tar?dl=0)   |
| ResNet101 |   Group-16    |    85.33%    | [link](https://www.dropbox.com/s/hzaxajxd17xep1b/resnet101.pth.tar?dl=0) |
| ResNet152 |   Group-16    |    85.45%    | [link](https://www.dropbox.com/s/himdmv7kso2usfj/resnet152.pth.tar?dl=0) |

IGN-a-16 denotes instance group normalization with channel-grouping number 16, replacing BN of IBNNet-a with GN16.
Group-16 denotes group normalization with channel-grouping number 16.

| WAD2018 | Score | Difference |
| :------ | :---: | :--------: |
| 1st     | 86.18 |   -0.09    |
| Mine    | 86.09 |    +0.0    |
| 2nd     | 86.04 |   +0.05    |
| 3rd     | 84.01 |   +2.08    |
