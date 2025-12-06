import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os

# --- Configuration ---
CHART_WIDTH = 1200
CHART_HEIGHT = 600
TEMPLATE_WIDTH = 1600
TEMPLATE_HEIGHT = 1000
OUTPUT_FILENAME = "seo_infographic_output.png"
CHART_TEMP_FILENAME = "temp_chart.png"

# --- PART 1: Data Processing and Chart Generation (The Python Core) ---

def create_chart_image(data):
    """
    Generates a clean bar chart from data and saves it with a transparent background.
    This is where the 'graphic design' clean-up starts, by removing ugly defaults.
    """
    labels = list(data.keys())
    values = list(data.values())
    
    # Create the figure and axes
    fig, ax = plt.subplots(figsize=(CHART_WIDTH / 100, CHART_HEIGHT / 100), dpi=100)
    
    # 1. Plot the data (using a clean color palette)
    colors = ['#4CAF50' if v > 10000 else '#FFC107' for v in values] # Conditional coloring
    ax.bar(labels, values, color=colors)
    
    # 2. Design Cleanup (Crucial for a premium look)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    # Remove y-axis labels and ticks for a cleaner, infographic style
    ax.yaxis.set_visible(False)
    ax.tick_params(axis='x', length=0)
    
    # Add data labels directly on top of bars
    for i, v in enumerate(values):
        ax.text(i, v + 200, f'${v:,.0f}', ha='center', color='black', fontsize=16)

    plt.xticks(fontsize=14)
    plt.title("Revenue by Channel Q3 2025", fontsize=20, pad=20)
    
    # Save the chart as a transparent PNG
    plt.savefig(CHART_TEMP_FILENAME, transparent=True, bbox_inches='tight', pad_inches=0.1)
    plt.close(fig)

    print(f"Chart saved temporarily to {CHART_TEMP_FILENAME}")

# --- PART 2: Image Composition (The Graphic Design Automation) ---

def create_infographic_composition():
    """
    Combines the generated chart with a designed template background and text.
    """
    try:
        # 1. Create the Template Canvas (This is the design input)
        # We simulate a sleek, white background with a colored banner header
        infographic = Image.new('RGB', (TEMPLATE_WIDTH, TEMPLATE_HEIGHT), color='#FFFFFF')
        draw = ImageDraw.Draw(infographic)
        
        # Draw the top banner (Design Element)
        draw.rectangle([0, 0, TEMPLATE_WIDTH, 150], fill="#3F51B5") # Blue header
        
        # Add the main infographic title (Design Element)
        try:
            # Use a default font if a custom one isn't found
            font_title = ImageFont.truetype("arial.ttf", 60)
            font_text = ImageFont.truetype("arial.ttf", 30)
        except IOError:
            print("Using default PIL fonts, consider installing a system font like 'arial.ttf'")
            font_title = ImageFont.load_default()
            font_text = ImageFont.load_default()
            
        draw.text((80, 40), "Q3 2025 Revenue Deep Dive", fill="#FFFFFF", font=font_title)
        
        # 2. Paste the Generated Chart
        chart_img = Image.open(CHART_TEMP_FILENAME)
        
        # Calculate paste position (centered)
        x_pos = (TEMPLATE_WIDTH - chart_img.width) // 2
        y_pos = 250 # Below the banner
        
        infographic.paste(chart_img, (x_pos, y_pos), chart_img)
        
        # 3. Add SEO/Branding Footer
        draw.text((80, 920), "Source: [Your Brand Name]. Data used to justify next quarter planning.", fill="#9E9E9E", font=font_text)

        # 4. Save Final Product
        infographic.save(OUTPUT_FILENAME)
        print(f"\n✅ Infographic successfully created and saved as {OUTPUT_FILENAME}")
        
    except FileNotFoundError:
        print(f"Error: Temporary chart file {CHART_TEMP_FILENAME} not found. Check if Matplotlib save was successful.")
    finally:
        # Clean up the temporary chart file
        if os.path.exists(CHART_TEMP_FILENAME):
            os.remove(CHART_TEMP_FILENAME)

# --- Main Execution ---

if __name__ == "__main__":
    # Sample data that the tool accepts (e.g., loaded from a CSV/API)
    sample_data = {
        'SEO': 12500,
        'Social Media': 9800,
        'Email': 15000,
        'Paid Ads': 8900
    }
    
    create_chart_image(sample_data)
    create_infographic_composition()
    
    # You could run this in a loop to generate hundreds of infographics
    # from a large database of data points, making the process passive!
