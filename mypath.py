class Path(object):
    @staticmethod
    def db_root_dir(dataset):
        if dataset == "pascal":
            return "/path/to/datasets/VOCdevkit/VOC2012/"  # folder that contains VOCdevkit/.
        elif dataset == "sbd":
            return (
                "/path/to/datasets/benchmark_RELEASE/"  # folder that contains dataset/.
            )
        elif dataset == "cityscapes":
            return "/path/to/datasets/cityscapes/"  # foler that contains leftImg8bit/
        elif dataset == "coco":
            return "/path/to/datasets/coco/"
        elif dataset == "bdd":
            # return './bdd100k'
            # return "C:/datasets/bdd100k/bdd100k"
            return "/nasa/datasets/public_datasets/bdd100k/bdd100k"
        elif dataset == "nice":
            return "./bdd_nice"
        else:
            print("Dataset {} not available.".format(dataset))
            raise NotImplementedError
