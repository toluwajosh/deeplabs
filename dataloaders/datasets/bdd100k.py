import os
from copy import deepcopy
import numpy as np
import scipy.misc as m
from PIL import Image
from torch.utils import data
from mypath import Path
from torchvision import transforms
from dataloaders import custom_transforms as tr


class BDD100kSegmentation(data.Dataset):
    """
    BDD100k Drivable Area segmentation
    """

    NUM_CLASSES = 3

    def __init__(self, args, root=Path.db_root_dir("bdd"), split="train", division=10):

        self.root = root
        self.split = split
        self.args = args
        self.files = {}
        self.lane_files = {}

        self.images_base = os.path.join(self.root, "images", "100k", self.split)
        self.annotations_base = os.path.join(
            self.root, "drivable_maps", "labels", self.split
        )
        self.lanes_base = os.path.join(self.root, "lanes", "100k", self.split)

        self.lane_files[split] = self.recursive_glob(
            rootdir=self.lanes_base, suffix=".png"
        )

        # to make sure all files in lanes are in images
        # self.files[split] = self.recursive_glob(rootdir=self.images_base, suffix=".jpg")
        self.files[split] = deepcopy(self.lane_files[split])
        self.files[split] = [
            x.replace("lanes/100k", "images/100k") for x in self.files[split]
        ]
        self.files[split] = [x.replace(".png", ".jpg") for x in self.files[split]]

        # REDUCING DATASET
        if split != "test":
            self.files[split] = self.files[split][: len(self.files[split]) // division]
            self.lane_files[split] = self.lane_files[split][
                : len(self.lane_files[split]) // division
            ]
        else:
            self.files[split] = self.recursive_glob(
                rootdir=self.images_base, suffix=".jpg"
            )

        self.void_classes = (
            []
        )  # [0, 1, 2, 3, 4, 5, 6, 9, 10, 14, 15, 16, 18, 29, 30, -1]
        self.valid_classes = [
            0,
            1,
            2,
        ]  # [7, 8, 11, 12, 13, 17, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 31, 32, 33]
        self.class_names = [
            "Not drivable",
            "Drivable area",
            "Alternative drivable area",
        ]

        self.ignore_index = 255
        self.class_map = dict(zip(self.valid_classes, range(self.NUM_CLASSES)))

        if not self.files[split]:
            raise Exception(
                "No files for split=[%s] found in %s" % (split, self.images_base)
            )
        print("Found %d %s images" % (len(self.files[split]), split))
        # print("Found %d %s images" % (len(self.lane_files[split]), split))
        # exit(0)

    def __len__(self):
        return len(self.files[self.split])

    def __getitem__(self, index):

        img_path = self.files[self.split][index].rstrip()
        lanes_path = self.lane_files[self.split][index].rstrip()
        lbl_path = os.path.join(
            self.annotations_base, os.path.basename(img_path)[:17] + "_drivable_id.png"
        )

        _img = Image.open(img_path).convert("RGB")
        _name = os.path.basename(img_path)[:17] + ".png"
        _lane = Image.open(lanes_path).convert("L").point(lambda i: i > 0 and 1)

        if self.split == "test":
            sample = {"image": _img, "name": _name}
        else:
            _tmp = np.array(Image.open(lbl_path), dtype=np.uint8)
            _tmp = self.encode_segmap(_tmp)
            _target = Image.fromarray(_tmp)
            sample = {"image": _img, "label": _target, "name": _name, "lanes": _lane}

        if self.split == "train":
            return self.transform_tr(sample)
        elif self.split == "val":
            return self.transform_val(sample)
        elif self.split == "test":
            return self.transform_ts(sample)

    def encode_segmap(self, mask):
        # Put all void classes to zero
        for _voidc in self.void_classes:
            mask[mask == _voidc] = self.ignore_index
        for _validc in self.valid_classes:
            mask[mask == _validc] = self.class_map[_validc]
        return mask

    def recursive_glob(self, rootdir=".", suffix=""):
        """Performs recursive glob with given suffix and rootdir
        :param rootdir is the root directory
        :param suffix is the suffix to be searched
        """
        return [
            os.path.join(looproot, filename)
            for looproot, _, filenames in os.walk(rootdir)
            for filename in filenames
            if filename.endswith(suffix)
        ]

    def transform_tr(self, sample):
        composed_transforms = transforms.Compose(
            [
                #            tr.RandomHorizontalFlip(),
                #            tr.RandomScaleCrop(base_size=self.args.base_size, crop_size=self.args.crop_size, fill=255),
                #            tr.RandomCrop2(crop_size=self.args.crop_size),
                tr.Rescale(ratio=self.args.ratio),
                tr.RandomGaussianBlur(),
                tr.Normalize(mean=(0.279, 0.293, 0.290), std=(0.197, 0.198, 0.201)),
                tr.ToTensor(),
            ]
        )

        return composed_transforms(sample)

    def transform_val(self, sample):

        composed_transforms = transforms.Compose(
            [
                #            tr.FixScaleCrop(crop_size=self.args.crop_size),
                tr.Normalize(mean=(0.279, 0.293, 0.290), std=(0.197, 0.198, 0.201)),
                tr.ToTensor(),
            ]
        )

        return composed_transforms(sample)

    def transform_ts(self, sample):

        composed_transforms = transforms.Compose(
            [
                #            tr.FixedResize(size=self.args.crop_size),
                tr.Normalize(mean=(0.279, 0.293, 0.290), std=(0.197, 0.198, 0.201)),
                tr.ToTensor(),
            ]
        )

        return composed_transforms(sample)


if __name__ == "__main__":
    from dataloaders.utils import decode_segmap
    from torch.utils.data import DataLoader
    import matplotlib.pyplot as plt
    import argparse

    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    args.base_size = 513
    args.crop_size = 513

    cityscapes_train = CityscapesSegmentation(args, split="train")

    dataloader = DataLoader(cityscapes_train, batch_size=2, shuffle=True, num_workers=2)

    for ii, sample in enumerate(dataloader):
        for jj in range(sample["image"].size()[0]):
            img = sample["image"].numpy()
            gt = sample["label"].numpy()
            tmp = np.array(gt[jj]).astype(np.uint8)
            segmap = decode_segmap(tmp, dataset="cityscapes")
            img_tmp = np.transpose(img[jj], axes=[1, 2, 0])
            img_tmp *= (0.229, 0.224, 0.225)
            img_tmp += (0.485, 0.456, 0.406)
            img_tmp *= 255.0
            img_tmp = img_tmp.astype(np.uint8)
            plt.figure()
            plt.title("display")
            plt.subplot(211)
            plt.imshow(img_tmp)
            plt.subplot(212)
            plt.imshow(segmap)

        if ii == 1:
            break

    plt.show(block=True)
