# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

from typing import Callable, Optional

from overrides import overrides
from torch.utils.data import Dataset
from torchvision.datasets import ImageNet
from torchvision.transforms import ToTensor

from archai.api.dataset_provider import DatasetProvider
from archai.common.logging_utils import get_logger

logger = get_logger(__name__)


class ImageNetDatasetProvider(DatasetProvider):
    """ImageNet dataset provider."""

    def __init__(
        self,
        root: Optional[str] = "dataroot",
    ) -> None:
        """Initialize ImageNet dataset provider.

        Args:
            root: Root directory of dataset where is saved.

        """

        super().__init__()

        self.root = root

    @overrides
    def get_train_dataset(
        self,
        transform: Optional[Callable] = None,
        target_transform: Optional[Callable] = None,
        loader: Optional[Callable] = None,
    ) -> Dataset:
        return ImageNet(
            self.root,
            split="train",
            transform=transform or ToTensor(),
            target_transform=target_transform,
            loader=loader,
        )

    @overrides
    def get_val_dataset(
        self,
        transform: Optional[Callable] = None,
        target_transform: Optional[Callable] = None,
        loader: Optional[Callable] = None,
    ) -> Dataset:
        return ImageNet(
            self.root,
            split="val",
            transform=transform or ToTensor(),
            target_transform=target_transform,
            loader=loader,
        )

    @overrides
    def get_test_dataset(
        self,
        transform: Optional[Callable] = None,
        target_transform: Optional[Callable] = None,
        loader: Optional[Callable] = None,
    ) -> Dataset:
        logger.warn("Testing set not available. Returning validation set ...")
        return self.get_val_dataset(transform=transform, target_transform=target_transform, loader=loader)
