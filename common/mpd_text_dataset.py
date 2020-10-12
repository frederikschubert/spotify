import logging
import os

import torch
from torch.utils.data import IterableDataset, get_worker_info
from transformers import PreTrainedTokenizer

logger = logging.getLogger(__name__)


class CustomIterableDataset(IterableDataset):
    def __init__(
        self, file_path, tokenizer: PreTrainedTokenizer, block_size: int, length: int
    ):
        self.file_path = file_path
        self.tokenizer = tokenizer
        self.block_size = block_size
        self.length = length

    def preprocess(self, text):
        batch_encoding = self.tokenizer(
            text.strip("\n"),
            add_special_tokens=True,
            truncation=True,
            max_length=self.block_size,
        )

        return torch.tensor(batch_encoding["input_ids"])

    def line_mapper(self, line):
        return self.preprocess(line)

    def __iter__(self):
        file_itr = open(self.file_path, encoding="utf-8")
        mapped_itr = map(self.line_mapper, file_itr)

        return mapped_itr

    def __len__(self):
        return self.length
