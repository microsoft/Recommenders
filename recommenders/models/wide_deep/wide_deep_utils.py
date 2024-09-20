# Copyright (c) Recommenders contributors.
# Licensed under the MIT License.
from typing import Tuple
from dataclasses import dataclass

import torch
from torch.utils.data import DataLoader
from torch import nn

from recommenders.utils.constants import DEFAULT_USER_COL, DEFAULT_ITEM_COL

@dataclass(kw_only=True, frozen=True)
class WideAndDeepHyperParams:
    user_dim: int = 32
    item_dim: int = 32
    dnn_hidden_units: Tuple[int, ...] = (128, 128)
    dnn_dropout: float = 0.0

class WideAndDeepModel(nn.Module):
    def __init__(
        self, 
        num_users: int, 
        num_items: int, 
        hparams: WideAndDeepHyperParams = WideAndDeepHyperParams(),
    ):
        super().__init__()

        self.hparams = hparams
        self.n_users = num_users
        self.n_items = num_items
        
        self.embeddings = nn.ModuleDict({
            'users_emb': nn.Embedding(num_users, hparams.user_dim),
            'items_emb': nn.Embedding(num_items, hparams.item_dim),
            # TODO: Put other embeddings for other categorical features
        })

        # Randomly initialize embeddings
        total_emb_dim = 0
        for _, emb in self.embeddings.items():
            total_emb_dim += emb.embedding_dim
            nn.init.uniform_(emb.weight, -1, 1)

        layers = []
        # TODO: Add support for continuous features
        cont_features = 0
        prev_output = cont_features + total_emb_dim
        for hu in hparams.dnn_hidden_units:
            layers.append(nn.Linear(prev_output, hu))
            layers.append(nn.Dropout(hparams.dnn_dropout))
            layers.append(nn.ReLU())
            prev_output = hu

        self.deep = nn.Sequential(*layers)

        # P(Y=1|X) = W*wide + W'*a^(lf) + bias
        # which is eq. to W"*cat(wide, a^(lf))+bias
        wide_input = num_items # TODO: cross product
        wide_output = num_items

        print('wide_input:', wide_input, 'wide_output:', wide_output, 'total:', wide_input*wide_output)
        print('wide_input:', wide_input, 'prev_output:', prev_output, 'total:', wide_input+prev_output)
        self.head = nn.Sequential(
            nn.Linear(wide_input+prev_output, wide_output),
            nn.Sigmoid(),
        )

    def forward(self, interactions: torch.Tensor) -> torch.Tensor:
        users, items = interactions.T
        all_embed = torch.cat([
            self.embeddings['users_emb'](users), # Receives the indices
            self.embeddings['items_emb'](items),
        ], dim=1)

        # The cross-feature is really only the items because there is no
        # impression data
        # https://datascience.stackexchange.com/a/58915/169220
        cross_product = torch.zeros([items.numel(), self.n_items])
        cross_product[torch.arange(items.numel()), items] = 1

        # TODO: Add support for continuous features (concat inputs)
        deep_output = self.deep(all_embed)

        return self.head(torch.cat([
            cross_product, # wide input
            deep_output, # deep output
        ], dim=1))


class WideAndDeep(object):
    def __init__(
        self, 
        data,
        hparams: WideAndDeepHyperParams = WideAndDeepHyperParams(),
        seed=None,
    ):
        self.model = WideAndDeepModel(
            num_users=...,
            num_items=...,
            hparams=hparams,
        )
        self.dataloader = DataLoader(...)
        self.loss_fn = nn.CrossEntropyLoss()
        
    def fit(self):
        self.train_loop()
        self.test_loop()

    def train_loop(self):
        self.model.train()
        
        for batch, (X,y) in enumerate(self.dataloader):
            pred = self.model(X)
            loss = self.loss_fn(pred, y)

            # Propagate error
            loss.backward()
            self.optimizer.step()
            self.optimizer.zero_grad()

    def test_loop(self):
        # TODO: Copypasted example from pytorch's tutorial. Might need complete rewritting.
        self.model.eval()
        
        size = len(self.dataloader.dataset)
        num_batches = len(self.dataloader)
        test_loss, correct = 0, 0

        with torch.no_grad():
            for X, y in self.dataloader:
                pred = self.model(X)
                test_loss += self.loss_fn(pred, y).item()
                correct += (pred.argmax(1) == y).type(torch.float).sum().item()

        test_loss /= num_batches
        correct /= size
