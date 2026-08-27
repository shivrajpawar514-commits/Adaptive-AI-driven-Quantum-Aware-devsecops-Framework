import numpy as np
from src.training.trainer import AutoencoderTrainer

def test_autoencoder_trainer():
    X_train = np.random.rand(10, 4)
    X_val = np.random.rand(5, 4)
    
    trainer = AutoencoderTrainer(latent_dim=2)
    history, train_time = trainer.train(X_train, X_val, epochs=5, batch_size=2)
    
    assert 'train_loss' in history
    assert len(history['train_loss']) == 5
    assert trainer.threshold > 0.0
