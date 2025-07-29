import os
import json
from google.cloud import vision
from pathlib import Path
import argparse
import shutil
import time
import requests

class ImageTextExtractor:
    def __init__(self, credentials_path=None):
        """
        Initialize the Vision API client
        
        Args:
            credentials_path (str, optional): Path to the JSON credentials file.
                                           If None, will use default service account (for cloud deployment)
        """
        if credentials_path:
            # Use provided credentials file (for local development)
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
            print(f"Using credentials file: {credentials_path}")
        else:
            # Use default service account (for cloud deployment)
            print("Using default service account (cloud deployment)")
            # Clear any existing credentials to use default service account
            if 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
                del os.environ['GOOGLE_APPLICATION_CREDENTIALS']
        
        # Initialize the Vision API client
        self.client = vision.ImageAnnotatorClient()
        
        # Supported image formats
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
    
    def extract_text_from_image(self, image_path):
        """
        Extract text from a single image
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            str: Extracted text from the image
        """
        try:
            # Read the image file
            with open(image_path, 'rb') as image_file:
                content = image_file.read()
            
            # Create image object
            image = vision.Image(content=content)
            
            # Perform text detection
            response = self.client.text_detection(image=image)
            
            # Extract text
            texts = response.text_annotations
            
            if texts:
                # The first annotation contains all detected text
                extracted_text = texts[0].description
                return extracted_text
            else:
                return "No text found in image"
                
        except Exception as e:
            return f"Error processing image: {str(e)}"
    
    def process_folder(self, folder_path, output_format='txt'):
        """
        Process all images in a folder and extract text
        
        Args:
            folder_path (str): Path to the folder containing images
            output_format (str): Output format - 'txt', 'json', or 'console'
        """
        folder_path = Path(folder_path)
        
        if not folder_path.exists():
            print(f"Error: Folder '{folder_path}' does not exist")
            return
        
        # Get all image files in the folder
        image_files = []
        for file_path in folder_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                image_files.append(file_path)
        
        if not image_files:
            print(f"No supported image files found in '{folder_path}'")
            print(f"Supported formats: {', '.join(self.supported_formats)}")
            return
        
        print(f"Found {len(image_files)} image files to process...")
        
        results = {}
        
        # Process each image
        for i, image_path in enumerate(image_files, 1):
            print(f"Processing ({i}/{len(image_files)}): {image_path.name}")
            
            extracted_text = self.extract_text_from_image(str(image_path))
            results[image_path.name] = extracted_text
            
            if output_format == 'console':
                print(f"\n--- Text from {image_path.name} ---")
                print(extracted_text)
                print("-" * 50)
        
        # Save results based on output format
        if output_format == 'txt':
            self.save_as_txt(results, folder_path)
        elif output_format == 'json':
            self.save_as_json(results, folder_path)
        
        print(f"\nProcessing complete! Processed {len(image_files)} images.")
    
    def save_as_txt(self, results, folder_path):
        """Save results as individual text files"""
        output_folder = folder_path / "extracted_text"
        output_folder.mkdir(exist_ok=True)
        
        for image_name, text in results.items():
            # Create output filename
            output_filename = f"{Path(image_name).stem}_text.txt"
            output_path = output_folder / output_filename
            
            # Write text to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"Text extracted from: {image_name}\n")
                f.write("=" * 50 + "\n\n")
                f.write(text)
            
            print(f"Saved: {output_path}")
    
    def save_as_json(self, results, folder_path):
        """Save results as a single JSON file"""
        output_path = folder_path / "extracted_text_results.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"Saved: {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Extract text from images using Google Vision API')
    parser.add_argument('folder_path', help='Path to folder containing images')
    parser.add_argument('credentials_path', help='Path to Google Cloud credentials JSON file')
    parser.add_argument('--output', choices=['txt', 'json', 'console'], default='txt',
                       help='Output format (default: txt)')
    
    args = parser.parse_args()
    
    # Validate credentials file
    if not os.path.exists(args.credentials_path):
        print(f"Error: Credentials file '{args.credentials_path}' not found")
        return
    
    # Create extractor and process folder
    extractor = ImageTextExtractor(args.credentials_path)
    extractor.process_folder(args.folder_path, args.output)

if __name__ == "__main__":
    # Example usage if running directly
    if len(os.sys.argv) == 1:
        print("Example usage:")
        print("python image_text_extractor.py /path/to/images /path/to/credentials.json --output txt")
        print("\nOr use it programmatically:")
        print()
        print("extractor = ImageTextExtractor('/path/to/credentials.json')")
        print("extractor.process_folder('/path/to/images', 'txt')")
    else:
        main()