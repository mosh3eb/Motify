from PIL import Image, ImageDraw, ImageFont
import os

def create_placeholder_image(filename, title, size=(800, 600), bg_color=(33, 33, 33), text_color=(255, 255, 255)):
    # Create a new image with the specified background color
    img = Image.new('RGB', size, bg_color)
    draw = ImageDraw.Draw(img)
    
    # Add a title
    try:
        font = ImageFont.truetype("Arial", 40)
    except:
        font = ImageFont.load_default()
    
    # Calculate text position to center it
    text_bbox = draw.textbbox((0, 0), title, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    
    # Draw the text
    draw.text((x, y), title, font=font, fill=text_color)
    
    # Save the image
    img.save(filename)

# Create the images directory if it doesn't exist
os.makedirs('docs/assets/images', exist_ok=True)

# Generate placeholder screenshots
create_placeholder_image('docs/assets/images/main-interface.png', 'Main Interface')
create_placeholder_image('docs/assets/images/playlist-management.png', 'Playlist Management')
create_placeholder_image('docs/assets/images/download-queue.png', 'Download Queue') 