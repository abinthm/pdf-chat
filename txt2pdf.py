#!/usr/bin/env python3
"""
Convert all .txt files in a folder to a single PDF document.
Requires: pip install reportlab
"""

import os
import glob
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import re
import unicodedata

def txt_to_pdf(input_folder, output_pdf="combined_texts.pdf", page_size=A4):
    """
    Convert all .txt files in a folder to a single PDF.
    
    Args:
        input_folder (str): Path to folder containing .txt files
        output_pdf (str): Output PDF filename
        page_size: Page size (default: A4)
    """
    
    # Check if input folder exists
    if not os.path.exists(input_folder):
        print(f"Error: Folder '{input_folder}' does not exist.")
        return False
    
    # Get all .txt files in the folder
    txt_files = glob.glob(os.path.join(input_folder, "*.txt"))
    
    if not txt_files:
        print(f"No .txt files found in '{input_folder}'")
        return False
    
    # Sort files alphabetically
    txt_files.sort()
    
    print(f"Found {len(txt_files)} .txt files")
    
    # Create PDF document
    doc = SimpleDocTemplate(output_pdf, pagesize=page_size,
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=18)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Create custom styles with Unicode-friendly font
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        textColor=colors.darkblue,
        alignment=1,  # Center alignment
        fontName='Helvetica'  # Ensure we use a font that supports more characters
    )
    
    content_style = ParagraphStyle(
        'CustomContent',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=12,
        leftIndent=0,
        rightIndent=0,
        fontName='Helvetica'
    )
    
    # Build story (content) for PDF
    story = []
    
    for i, txt_file in enumerate(txt_files):
        try:
            # Read the text file with better encoding handling
            content = None
            encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
            
            for encoding in encodings_to_try:
                try:
                    with open(txt_file, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                # Last resort: read as binary and decode with error handling
                with open(txt_file, 'rb') as f:
                    raw_content = f.read()
                content = raw_content.decode('utf-8', errors='replace')
            
            # Get filename without path and extension for title
            filename = os.path.splitext(os.path.basename(txt_file))[0]
            
            print(f"Processing: {filename}")
            
            # Add filename as title
            story.append(Paragraph(f"File: {filename}", title_style))
            story.append(Spacer(1, 12))
            
            # Split content into paragraphs and add to story
            paragraphs = content.split('\n\n')
            for paragraph in paragraphs:
                if paragraph.strip():  # Skip empty paragraphs
                    # Clean and normalize the text
                    clean_paragraph = paragraph.strip()
                    
                    # Only remove specific problematic characters that actually cause black boxes
                    # NOT diacritical marks which are legitimate
                    
                    # Remove only actual problematic characters (private use area, control chars)
                    problematic_chars = [
                        '\uf020', '\uf021', '\uf022', '\uf023', '\uf024', '\uf025',  # Private use area
                        '\ufffd',  # Replacement character (actual black diamond with ?)
                    ]
                    
                    for char in problematic_chars:
                        clean_paragraph = clean_paragraph.replace(char, '')
                    
                    # Remove only private use area characters, NOT legitimate diacritics
                    clean_paragraph = re.sub(r'[\uf000-\uf8ff]', '', clean_paragraph)  # Private use area only
                    clean_paragraph = re.sub(r'[\u0000-\u001f\u007f-\u009f]', '', clean_paragraph)  # Control characters only
                    
                    # Handle only actual rendering issues, not diacritics
                    # If the original text had actual ■ symbols, replace them carefully
                    if '■' in clean_paragraph:
                        # Only replace if it's clearly a rendering error pattern
                        clean_paragraph = re.sub(r'■+', '', clean_paragraph)
                    
                    # Standard safe replacements (not diacritics)
                    replacements = {
                        '\ufeff': '',   # BOM
                        '\u00a0': ' ',  # Non-breaking space
                        '\u2013': '-',  # En dash
                        '\u2014': '--', # Em dash
                        '\u2018': "'",  # Left single quote
                        '\u2019': "'",  # Right single quote
                        '\u201c': '"',  # Left double quote
                        '\u201d': '"',  # Right double quote
                        '\u2026': '...' # Ellipsis
                    }
                    
                    for old, new in replacements.items():
                        clean_paragraph = clean_paragraph.replace(old, new)
                    
                    # Escape XML/HTML special characters for reportlab
                    clean_paragraph = clean_paragraph.replace('&', '&amp;')
                    clean_paragraph = clean_paragraph.replace('<', '&lt;')
                    clean_paragraph = clean_paragraph.replace('>', '&gt;')
                    
                    # Convert line breaks to HTML breaks
                    clean_paragraph = clean_paragraph.replace('\n', '<br/>')
                    
                    # Much more conservative character filtering
                    # Keep all legitimate Unicode characters including diacritics
                    safe_chars = []
                    for char in clean_paragraph:
                        # Keep most Unicode characters, only filter out truly problematic ones
                        if ord(char) < 32 and char not in ['\t']:
                            continue  # Skip control characters except tab
                        elif char in ['<', '>', '&', ';', '/', ' ', 'b', 'r']:  # HTML entities and markup
                            safe_chars.append(char)
                        elif ord(char) >= 32:  # Keep most printable characters including Unicode
                            # Check if it's a legitimate character (not a control or private use)
                            category = unicodedata.category(char)
                            if not category.startswith('C'):  # Not a control character
                                safe_chars.append(char)
                    
                    clean_paragraph = ''.join(safe_chars)
                    
                    # Remove extra whitespace
                    clean_paragraph = re.sub(r'\s+', ' ', clean_paragraph).strip()
                    
                    if clean_paragraph:  # Only add non-empty paragraphs
                        story.append(Paragraph(clean_paragraph, content_style))
            
            # Add page break between files (except for the last file)
            if i < len(txt_files) - 1:
                story.append(PageBreak())
                
        except Exception as e:
            print(f"Error processing {txt_file}: {str(e)}")
            continue
    
    # Build PDF
    try:
        doc.build(story)
        print(f"\nPDF created successfully: {output_pdf}")
        print(f"Total pages: {doc.page}")
        return True
        
    except Exception as e:
        print(f"Error creating PDF: {str(e)}")
        return False

def main():
    """Main function with user interaction."""
    
    # Get input folder from user
    input_folder = input("Enter the path to the folder containing .txt files: ").strip()
    
    # Remove quotes if present
    input_folder = input_folder.strip('"\'')
    
    # Get output filename (optional)
    output_name = input("Enter output PDF name (press Enter for 'combined_texts.pdf'): ").strip()
    if not output_name:
        output_name = "combined_texts.pdf"
    
    # Ensure .pdf extension
    if not output_name.lower().endswith('.pdf'):
        output_name += '.pdf'
    
    # Convert files
    success = txt_to_pdf(input_folder, output_name)
    
    if success:
        print(f"\n✓ Conversion completed successfully!")
        print(f"Output file: {os.path.abspath(output_name)}")
    else:
        print("\n✗ Conversion failed!")

if __name__ == "__main__":
    # Example usage (uncomment to use directly):
    # txt_to_pdf("./text_files", "my_combined_document.pdf")
    
    # Interactive mode
    main()