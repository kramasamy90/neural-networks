import os
import sys

from tqdm import tqdm

import torch.nn as nn
from torch.utils.data import DataLoader

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from optimizer_factory import OptimizerFactory

# from typing import 

# Import training parameters.

class Trainer:
    loss_fns = {
        'mse_loss'   : nn.MSELoss,
        'bce_loss'   : nn.BCELoss,
        'ce_loss'    : nn.CrossEntropyLoss
    }


    def __init__(self, model, train_dataset, config):
        self.config = config
        self.model = model
        self.train_dataset = train_dataset

    
    def train(self, inner_progress_bar = False, outer_progress_bar = True, 
              print_loss = False):
        self.model.to(self.config['device'])

        # Get optimizer.
        optimizer_factory = OptimizerFactory(self.config['optimizer'])
        optimizer = optimizer_factory.get_optimizer(self.model.parameters())
        # Loss function.

        criterion = self.loss_fns[self.config['loss_fn']]().to(self.config['device'])

        train_loader = DataLoader(self.train_dataset,
                                    batch_size=self.config['batch_size'], shuffle=True)
        if inner_progress_bar:
            train_loader = tqdm(train_loader)
        if outer_progress_bar:
            epochs_iterator = tqdm(range(self.config['epochs']))
        else:
            epochs_iterator = range(self.config['epochs'])

        self.model.train()
        loss_history = []
        for epoch in epochs_iterator:
            running_loss = 0.0
            for images, labels in train_loader:
                images = images.to(self.config['device'])
                labels = labels.to(self.config['device'])
                optimizer.zero_grad()
                outputs = self.model(images)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()

                running_loss += loss.item()
            if print_loss:
                print(f"Epoch {epoch+1}/{self.config['epochs']},\
                    Loss: {running_loss/len(train_loader)}")

            loss_history.append(running_loss / len(train_loader))
        return {"model": self.model, "loss_history" : loss_history}

