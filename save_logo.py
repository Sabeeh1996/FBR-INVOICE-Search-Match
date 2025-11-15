"""
Codium Edge Logo Creator
Creates a stylized logo inspired by the colorful 'C' design
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_codium_edge_logo():
    """Create a colorful Codium Edge logo with stylized C letter"""
    
    # Logo dimensions
    width, height = 250, 60
    
    # Create image with white background
    img = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Colors inspired by the attached logo
    yellow = (255, 193, 7)      # Yellow/Gold
    purple = (106, 90, 205)     # Purple
    red = (244, 67, 54)         # Red
    
    # Draw stylized 'C' letter (simplified version)
    c_x, c_y = 30, 30
    c_radius = 22
    
    # Yellow outer arc (left side of C)
    draw.arc([c_x - c_radius, c_y - c_radius, c_x + c_radius, c_y + c_radius],
             start=90, end=270, fill=yellow, width=8)
    
    # Purple inner part
    draw.arc([c_x - c_radius + 6, c_y - c_radius + 6, c_x + c_radius - 6, c_y + c_radius - 6],
             start=45, end=315, fill=purple, width=6)
    
    # Red horizontal line in middle
    draw.rectangle([c_x, c_y - 2, c_x + 20, c_y + 2], fill=red)
    
    # Add "Codium Edge" text
    try:
        # Try to use a nice font
        font_large = ImageFont.truetype("arial.ttf", 24)
        font_small = ImageFont.truetype("arial.ttf", 12)
    except:
        # Fallback to default font
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Draw "Codium Edge" text
    text_x = c_x + c_radius + 15
    draw.text((text_x, 15), "Codium", font=font_large, fill=purple)
    draw.text((text_x + 85, 15), "Edge", font=font_large, fill=(70, 70, 70))
    
    # Add tagline
    draw.text((text_x, 42), "Automation Solutions", font=font_small, fill=(120, 120, 120))
    
    # Save the logo
    assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
    os.makedirs(assets_dir, exist_ok=True)
    logo_path = os.path.join(assets_dir, 'codium_edge_logo.png')
    img.save(logo_path, 'PNG')
    print(f"✅ Codium Edge logo saved to: {logo_path}")
    return logo_path

if __name__ == "__main__":
    create_codium_edge_logo()
