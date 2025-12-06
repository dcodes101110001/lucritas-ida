#pip install Pillow numpy

import numpy as np
from PIL import Image, ImageDraw
import random
import os

def random_color():
    """Generates a random RGB tuple."""
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def interpolate(start_color, end_color, factor: float):
    """Finds the color between two colors based on a factor (0 to 1)."""
    return tuple(int(start_color[i] + (end_color[i] - start_color[i]) * factor) for i in range(3))

def create_gradient(width, height, start_col, end_col):
    """Creates a smooth linear gradient image."""
    base = Image.new('RGB', (width, height), start_col)
    top = Image.new('RGB', (width, height), end_col)
    mask = Image.new('L', (width, height))
    mask_data = []
    
    # Create a vertical gradient mask
    for y in range(height):
        mask_data.extend([int(255 * (y / height))] * width)
        
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return base

def add_noise(image, factor=0.15):
    """Adds grain/noise to the image using NumPy for speed."""
    width, height = image.size
    # Convert image to numpy array
    img_array = np.array(image)
    
    # Generate random noise (-255 to 255), scaled by factor
    noise = np.random.normal(0, 50, (height, width, 3)) # Standard deviation of 50
    noise = noise * factor
    
    # Add noise to image
    noisy_img = img_array + noise
    
    # Clip values to 0-255 range and convert back to uint8
    noisy_img = np.clip(noisy_img, 0, 255).astype(np.uint8)
    
    return Image.fromarray(noisy_img)

def generate_pack(count=5):
    if not os.path.exists('output'):
        os.makedirs('output')
        
    print(f"🎨 Generating {count} assets...")
    
    for i in range(count):
        # 1. Define Dimensions (4K Resolution)
        W, H = 3840, 2160
        
        # 2. Pick Colors (You can hardcode your designer palettes here later)
        col1 = random_color()
        col2 = random_color()
        
        # 3. Generate Base Gradient
        img = create_gradient(W, H, col1, col2)
        
        # 4. Add Texture (The "Grain")
        # Adjust 'factor' to make it more or less grainy (0.1 to 0.3 is usually sweet spot)
        final_img = add_noise(img, factor=0.2)
        
        # 5. Save
        filename = f"output/gradient_{i+1}.png"
        final_img.save(filename)
        print(f"Saved: {filename}")

if __name__ == "__main__":
    generate_pack()
