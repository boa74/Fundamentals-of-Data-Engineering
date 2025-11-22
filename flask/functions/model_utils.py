"""
Model-related utility functions for Streamlit app
"""

import torch
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))


def get_device():
    """Get the best available device for PyTorch"""
    from device_utils import get_device as _get_device
    return _get_device()


def load_cgan_model(checkpoint_path, z_dim=100, num_classes=3, image_size=128):
    """
    Load Conditional GAN generator model
    
    Args:
        checkpoint_path: Path to the checkpoint file
        z_dim: Latent dimension
        num_classes: Number of disease classes
        image_size: Image resolution
        
    Returns:
        Loaded generator model
    """
    from models.cgan import Generator
    
    device = get_device()
    G = Generator(z_dim=z_dim, num_classes=num_classes, image_size=image_size).to(device)
    
    checkpoint = torch.load(checkpoint_path, map_location=device)
    if 'generator_state_dict' in checkpoint:
        G.load_state_dict(checkpoint['generator_state_dict'])
    else:
        G.load_state_dict(checkpoint)
    
    G.eval()
    return G, device


def load_prebuilt_gan_model(checkpoint_path, z_dim=128, num_classes=3):
    """
    Load Pre-built GAN generator model
    
    Args:
        checkpoint_path: Path to the checkpoint file
        z_dim: Latent dimension
        num_classes: Number of disease classes
        
    Returns:
        Loaded generator model
    """
    from models.prebuilt_gan import ConditionalGenerator
    
    device = get_device()
    G = ConditionalGenerator(num_classes=num_classes, z_dim=z_dim).to(device)
    
    checkpoint = torch.load(checkpoint_path, map_location=device)
    if 'generator_state_dict' in checkpoint:
        G.load_state_dict(checkpoint['generator_state_dict'])
    else:
        G.load_state_dict(checkpoint)
    
    G.eval()
    return G, device


def generate_cgan_images(generator, class_id, num_samples, z_dim, device):
    """
    Generate images using CGAN
    
    Args:
        generator: CGAN generator model
        class_id: Disease class ID
        num_samples: Number of images to generate
        z_dim: Latent dimension
        device: PyTorch device
        
    Returns:
        Generated images as torch tensor
    """
    with torch.no_grad():
        z = torch.randn(num_samples, z_dim, device=device)
        y = torch.full((num_samples,), class_id, dtype=torch.long, device=device)
        fake_images = generator(z, y)
    return fake_images


def generate_prebuilt_gan_images(generator, class_id, num_samples, z_dim, device):
    """
    Generate images using Pre-built GAN
    
    Args:
        generator: Pre-built GAN generator model
        class_id: Disease class ID
        num_samples: Number of images to generate
        z_dim: Latent dimension
        device: PyTorch device
        
    Returns:
        Generated images as torch tensor
    """
    with torch.no_grad():
        z = torch.randn(num_samples, z_dim, device=device)
        labels = torch.full((num_samples,), class_id, dtype=torch.long, device=device)
        fake_images = generator(z, labels)
    return fake_images


def tensor_to_pil(tensor):
    """
    Convert PyTorch tensor to PIL Image
    
    Args:
        tensor: Image tensor in range [-1, 1]
        
    Returns:
        PIL Image
    """
    from PIL import Image
    import numpy as np
    
    # Denormalize from [-1, 1] to [0, 1]
    img = tensor.cpu()
    img = (img + 1) / 2
    img = torch.clamp(img, 0, 1)
    
    # Convert to numpy and PIL
    img = img.permute(1, 2, 0).numpy()
    img = (img * 255).astype('uint8')
    return Image.fromarray(img)


def get_default_checkpoint_path(model_type):
    """
    Get default checkpoint path for a model type
    
    Args:
        model_type: Type of model ('cgan', 'prebuilt_gan')
        
    Returns:
        Path to default checkpoint
    """
    checkpoint_map = {
        'cgan': 'checkpoints/cgan/generator_final.pt',
        'prebuilt_gan': 'checkpoints/prebuilt_gan/generator_final.pt',
    }
    
    return project_root / checkpoint_map.get(model_type, '')


# Disease class configuration
DISEASE_CLASSES = {
    'Nevus': 0,
    'Melanoma': 1,
    'Basal cell carcinoma': 2,
}

DISEASE_INFO = {
    'Nevus': {
        'name': 'Nevus',
        'description': 'Common moles, usually benign',
        'prevalence': 'Very common',
    },
    'Melanoma': {
        'name': 'Melanoma',
        'description': 'Malignant skin cancer, most dangerous type',
        'prevalence': 'Less common but serious',
    },
    'Basal cell carcinoma': {
        'name': 'Basal cell carcinoma',
        'description': 'Most common type of skin cancer, usually treatable',
        'prevalence': 'Common',
    },
}
