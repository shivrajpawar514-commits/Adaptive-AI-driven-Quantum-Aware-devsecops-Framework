import torch
import torch.optim as optim
import torch.nn as nn
import numpy as np
import json
import os
import time

from src.models.autoencoder import Autoencoder

class AutoencoderTrainer:
    def __init__(self, latent_dim=2):
        self.latent_dim = latent_dim
        self.model = None
        self.threshold = 0.0

    def train(self, X_train, X_val, epochs=50, batch_size=16, lr=0.001):
        input_dim = X_train.shape[1]
        self.model = Autoencoder(input_dim, self.latent_dim)
        
        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.model.parameters(), lr=lr)
        
        train_tensor = torch.tensor(X_train, dtype=torch.float32)
        val_tensor = torch.tensor(X_val, dtype=torch.float32)
        
        train_loader = torch.utils.data.DataLoader(
            torch.utils.data.TensorDataset(train_tensor),
            batch_size=batch_size,
            shuffle=True
        )
        
        start_time = time.time()
        history = {'train_loss': [], 'val_loss': []}
        
        for epoch in range(epochs):
            self.model.train()
            train_loss = 0.0
            for batch in train_loader:
                x_batch = batch[0]
                optimizer.zero_grad()
                outputs = self.model(x_batch)
                loss = criterion(outputs, x_batch)
                loss.backward()
                optimizer.step()
                train_loss += loss.item() * x_batch.size(0)
                
            train_loss /= len(train_loader.dataset)
            
            self.model.eval()
            with torch.no_grad():
                val_outputs = self.model(val_tensor)
                val_loss = criterion(val_outputs, val_tensor).item()
                
            history['train_loss'].append(train_loss)
            history['val_loss'].append(val_loss)
            
        training_time = time.time() - start_time
        
        self.model.eval()
        with torch.no_grad():
            reconstructed = self.model(train_tensor)
            errors = torch.mean((train_tensor - reconstructed) ** 2, dim=1).numpy()
            self.threshold = float(np.percentile(errors, 99))
            
        return history, training_time

    def save(self, filepath_dir):
        os.makedirs(filepath_dir, exist_ok=True)
        torch.save(self.model.state_dict(), os.path.join(filepath_dir, 'autoencoder.pt'))
        with open(os.path.join(filepath_dir, 'threshold.json'), 'w') as f:
            json.dump({'threshold': self.threshold, 'input_dim': self.model.encoder[0].in_features}, f)

    def load(self, filepath_dir):
        with open(os.path.join(filepath_dir, 'threshold.json'), 'r') as f:
            meta = json.load(f)
            self.threshold = meta['threshold']
            input_dim = meta['input_dim']
            
        self.model = Autoencoder(input_dim, self.latent_dim)
        self.model.load_state_dict(torch.load(os.path.join(filepath_dir, 'autoencoder.pt')))
        self.model.eval()
