from google_images_search import GoogleImagesSearch
from moviepy import *
from moviepy.video.tools.subtitles import SubtitlesClip
from PIL import Image, ImageFilter, ImageOps, ImageEnhance
from random import randint
from time import sleep
import uuid
import openai
from pydub import AudioSegment
from pydub.silence import split_on_silence
import os
import re
from pprint import pprint
import random
import requests
import shutil
import sys
from time import time, sleep
import google_auth_oauthlib.flow
import googleapiclient.discovery
from google.auth.transport.requests import Request
import googleapiclient.errors
import os
import pickle
import subprocess
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
import numpy as np
import threading
from my_pushover import Pushover
from datetime import datetime
from time import time
import pytesseract
from PIL import Image
import traceback

def send_notification(notification, title, message):
    msg = notification.msg(message)
    msg.set("title", title)
    try:
        notification.send(msg)
    except Exception as e:
        print(str(e))
        pass

def authenticate_channel(client_secrets_file, scopes, channel_name, full_path):
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_local_server(port=0)
    save_credentials(channel_name, credentials, full_path)
    return googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

def load_or_authenticate_channel(channel_name, client_secrets_file, full_path):
    credentials = load_credentials(channel_name, full_path)

    if credentials and credentials.valid:
        return googleapiclient.discovery.build("youtube", "v3", credentials=credentials)
    else:
        return authenticate_channel(client_secrets_file, ["https://www.googleapis.com/auth/youtube.upload"], channel_name, full_path)

def save_credentials(channel_name, credentials, full_path):
    credentials_path = full_path+'\\credentials'+channel_name+'.pkl'
    with open(credentials_path, 'wb') as credentials_file:
        pickle.dump(credentials, credentials_file)

def load_credentials(channel_name, full_path):
    credentials_path = os.path.join(full_path, 'credentials' + channel_name + '.pkl')
    if os.path.exists(credentials_path):
        with open(credentials_path, 'rb') as credentials_file:
            credentials = pickle.load(credentials_file)
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                save_credentials(channel_name, credentials, full_path)  # Save the refreshed credentials
                return credentials
            elif credentials and credentials.valid:
                return credentials
    return None

def run_script(directory):
    """Run the AutomatedYoutube.py script with the given directory."""
    print(f"Running script for {directory}\n")
    subprocess.run(["python", "AutomatedYoutube.py", directory, "-l"], text=True)

def send_notification(notification, title, message):
    msg = notification.msg(message)
    msg.set("title", title)
    try:
        notification.send(msg)
    except Exception:
        pass

def zoom_and_crop_to_aspect_ratio(filepath, target_aspect_ratio=1.7778):
    # Open the image
    img = Image.open(filepath)
    
    # Calculate the current aspect ratio
    width, height = img.size
    current_aspect_ratio = width / height
    
    # Determine if we need to crop the width or the height to achieve the target aspect ratio
    if current_aspect_ratio > target_aspect_ratio:
        # Current image is too wide, need to crop the width
        new_width = int(height * target_aspect_ratio)
        left = (width - new_width) / 2
        top = 0
        right = (width + new_width) / 2
        bottom = height
    else:
        # Current image is too tall, need to crop the height
        new_height = int(width / target_aspect_ratio)
        top = (height - new_height) / 2
        left = 0
        bottom = (height + new_height) / 2
        right = width
    
    # Crop the image to the target aspect ratio
    img = img.crop((left, top, right, bottom))
    
    # Optionally, resize the cropped image back to the original dimensions or any specific dimensions
    # This step might not be necessary if maintaining the original image size isn't required
    # img = img.resize((original_width, original_height), Image.ANTIALIAS)

    # Convert the image to RGB mode if not already to avoid saving issues with JPEG
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Save the edited image back to the original filepath
    img.save(filepath, 'JPEG')

    return filepath

def enhance_image_with_vignette(filepath, vignette_strength=3.0, sharpness_factor=4.0, contrast_factor=1.5):
    # Open the original image
    img = Image.open(filepath)
    width, height = img.size

    # # Create a mask for the vignette
    # mask = Image.new('L', (width, height), 0)
    # gradient = ImageDraw.Draw(mask)

    # # Generate a radial gradient (black at edges to transparent at center)
    # for x in range(width):
    #     for y in range(height):
    #         # Calculate distance to the center
    #         distance = ((x - width / 2) ** 2 + (y - height / 2) ** 2) ** 0.5
    #         # Normalize distance to maximum radius
    #         max_distance = ((width / 2) ** 2 + (height / 2) ** 2) ** 0.5
    #         opacity = 255 - int(min(255, max(0, 255 * (distance / max_distance) ** vignette_strength)))
    #         gradient.point((x, y), fill=opacity)

    # # Blur the vignette mask to make the effect smoother
    # mask = mask.filter(ImageFilter.GaussianBlur(radius=min(width, height) / 30))

    # # Apply the vignette by combining it with the original image
    # img.putalpha(mask)
    # img = Image.alpha_composite(Image.new("RGBA", img.size, "black"), img)
    # img = img.convert("RGB")  # Convert back to RGB to remove alpha for saving

    # Increase sharpness
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(sharpness_factor)

    # Increase contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(contrast_factor)

    # Correctly handle file format based on the file extension
    file_extension = filepath.split('.')[-1].upper()  # Extract file extension and convert to uppercase
    format = 'JPEG' if file_extension in ['JPG', 'JPEG'] else file_extension
    if format not in ['JPEG', 'PNG', 'TIFF', 'BMP', 'GIF']:
        format = 'PNG'  # Default to PNG if unknown or unsupported extension
    img.save(filepath, format=format)

    return filepath

def google_image_search(query, api_key, cx):
    """
    Perform a Google image search using the Custom Search JSON API.

    Args:
        query (str): Search query.
        api_key (str): Your API key.
        cx (str): Your Programmable Search Engine ID.

    Returns:
        list: A list of image items (each is a dict) from the search result.
    """
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'q': query,
        'cx': cx,
        'key': api_key,
        'searchType': 'image'
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()  # Raise an exception if the request failed
    data = response.json()
    
    # Return the list of image results or an empty list if none found
    return data.get('items', [])

def download_image(image_url, download_dir):
    """
    Download an image from the given URL and save it with a unique filename.

    Args:
        image_url (str): URL of the image to download.
        download_dir (str): Path to the directory where images will be saved.
    """
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # Generate a unique filename (default extension set as .jpg)
        unique_filename = str(uuid.uuid4()) + ".jpg"
        file_path = os.path.join(download_dir, unique_filename)
        
        with open(file_path, 'wb') as file:
            file.write(response.content)
        
        print(f"Downloaded: {image_url} -> {file_path}")
    except Exception as e:
        print(f"Error downloading {image_url}: {e}")

def search_and_download(query, api_key, cx, download_dir):
    """
    Search for images and download them to a specific directory with unique names.

    Args:
        query (str): Search query.
        api_key (str): Your API key.
        cx (str): Your Programmable Search Engine ID.
        download_dir (str): Directory to download images to.
    """
    # Ensure the download directory exists
    os.makedirs(download_dir, exist_ok=True)
    
    # Search for images
    images = google_image_search(query, api_key, cx)
    
    if not images:
        print("No images found for this query.")
        return
    
    # Download each image from the search results
    for item in images:
        image_link = item.get('link')
        if image_link:
            download_image(image_link, download_dir)

def randomSleep():
    sleep(randint(2,4)*(randint(500,1000)/1000))

def hashes_are_similar(hash1, hash2, tolerance=5):
    # Count the number of differing bits
    if len(hash1) != len(hash2):
        return False
    return sum(c1 != c2 for c1, c2 in zip(hash1, hash2)) <= tolerance

def dhash(image, hash_size=6):  # Reduced hash_size
    # Resize and grayscale the image
    resized_image = image.convert('L').resize((hash_size + 1, hash_size))
    
    # Calculate the difference hash
    pixels = list(resized_image.getdata())
    diff = []
    for row in range(hash_size):
        for col in range(hash_size):
            diff.append(pixels[col + row * (hash_size + 1)] > pixels[col + row * (hash_size + 1) + 1])
    
    # Build the hash
    return ''.join(str(int(b)) for b in diff)

def process_images_in_directory(directory):
    for filename in os.listdir(directory):
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue  # Skip non-image files

        filepath = os.path.join(directory, filename)
        img = Image.open(filepath)

        # Resize image to have a height of 1000 if not already
        if img.height != 1000:
            scale_factor = 1000 / img.height
            img = img.resize((int(img.width * scale_factor), 1000), Image.LANCZOS)

        # If image is wider than 1920px, crop it
        if img.width > 1920:
            left = (img.width - 1920) / 2
            img = img.crop((left, 0, left + 1920, img.height))
        elif img.width < 1920:
            # Create a blurred background
            background = img.copy().resize((1920, 1000)).filter(ImageFilter.GaussianBlur(15))
            enhancer = ImageEnhance.Brightness(background)
            background = enhancer.enhance(0.7)

            # Calculate position to paste the resized image onto the background
            x_offset = (1920 - img.width) // 2
            background.paste(img, (x_offset, 0))
            img = background

        # Add black bar for subtitles
        black_bar = Image.new('RGB', (1920, 1080), (0, 0, 0))
        black_bar.paste(img, (0, 0))
        img = black_bar

        img_format = 'PNG' if filename.lower().endswith('.png') else 'JPEG'
        img.save(filepath, format=img_format)  # Specify the format explicitly based on the file e

def clean_directory(source_directory, target_directory):
    for filename in os.listdir(source_directory):
        filepath = os.path.join(source_directory, filename)
        
        # Delete files that are not JPG, JPEG, or PNG
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            os.remove(filepath)
            continue
        
        # Copy certain images to another directory
        img = Image.open(filepath)
        aspect_ratio = img.width / img.height
        if img.width > 800 and img.height > 400 and aspect_ratio > 1.5:
            shutil.copy(filepath, os.path.join(target_directory, filename))
            
def process_topics_and_paragraphs(list_of_things, max_length_for_topic):
    new_final_script = []
    current_paragraph = ""

    for index, item in enumerate(list_of_things):
        if len(item) < max_length_for_topic:
            # If there's a paragraph being built, append it before adding a new topic
            if current_paragraph:
                new_final_script.append(current_paragraph)
                current_paragraph = ""  # Reset current paragraph
            new_final_script.append(item)  # Append topic directly
        else:
            # For paragraphs, merge with the current_paragraph string
            if current_paragraph:
                current_paragraph += " " + item  # Merge with existing paragraph
            else:
                current_paragraph = item  # Start a new paragraph
    if current_paragraph:
        new_final_script.append(current_paragraph)

    return new_final_script

def extract_initial_number(s):
    match = re.match(r'\d+', s)
    if match:
        return int(match.group())
    else:
        return float('inf')

def reduce_image_size(thumbnail_file, directory, max_size_mb=2, step=10, quality=85):
    # Check initial file size
    file_size = os.path.getsize(thumbnail_file) / (1024 * 1024)  # Convert to MB
    if file_size <= max_size_mb:
        return thumbnail_file

    with Image.open(thumbnail_file) as img:
        width, height = img.size
        while file_size > max_size_mb:
            # Reduce dimensions
            img = img.resize((width, height), Image.LANCZOS)

            # Save the image with reduced quality
            img.save(os.path.join(directory, "temp_img.jpg"), quality=quality, optimize=True)

            # Check the size
            file_size = os.path.getsize(os.path.join(directory, "temp_img.jpg")) / (1024 * 1024)  # Convert to MB
            if file_size > max_size_mb:
                # Reduce dimensions and quality for next iteration
                width, height = int(width * 0.9), int(height * 0.9)
                quality -= step
                quality = max(quality, 10)  # Maintain a minimum quality

        return os.path.join(directory, "temp_img.jpg")

def convert_image_to_1920x1080(input_image_path, output_image_path):
    desired_aspect_ratio = 1920 / 1080  # Aspect ratio of 16:9
    with Image.open(input_image_path) as img:
        original_width, original_height = img.size
        original_aspect_ratio = original_width / original_height
        
        # Calculate the cropping box dimensions
        if original_aspect_ratio > desired_aspect_ratio:
            # The image is wider than needed, crop width
            new_height = original_height
            new_width = int(desired_aspect_ratio * new_height)
            left = (original_width - new_width) / 2
            top = 0
            right = (original_width + new_width) / 2
            bottom = original_height
        else:
            # The image is taller than needed, crop height
            new_width = original_width
            new_height = int(new_width / desired_aspect_ratio)
            left = 0
            top = (original_height - new_height) / 2
            right = original_width
            bottom = (original_height + new_height) / 2
        
        # Crop the image to the calculated box
        img_cropped = img.crop((left, top, right, bottom))
        
        # Resize the image to 1920x1080 if it is not already the desired size
        if img_cropped.size != (1920, 1080):
            img_cropped = img_cropped.resize((1920, 1080), Image.LANCZOS)
        
        # Save the cropped and resized image
        img_cropped.save(output_image_path)

def generate_thumbnail(thumbnail_prompt, directory):

    client = openai.Client(api_key=(open(os.getcwd()+'\\openai_key.txt').read()).strip())

    try:
        generated_image = client.images.generate(
            model="dall-e-3",
            prompt="Make a thumbnail for the following topic: "+thumbnail_prompt+". The thumbnail needs to stand out as irresistibly clickable among a sea of others, compelling viewers to choose it over the rest. Make sure to use strong, bright and contrasting colours. Make sure to use a close-up view. IMPORTANT: Do not put any words on the thumbnail.",
            n=1,
            size="1792x1024"
        )

        response = requests.get(generated_image.data[0].url)
        thumbnail_path = os.path.join(directory, 'thumbnail.png')

        with open(thumbnail_path, "wb") as file:
            file.write(response.content)
    
        return thumbnail_path

    except Exception as thumbnail_error:
        print(thumbnail_error)
        return False