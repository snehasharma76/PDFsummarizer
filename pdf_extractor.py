import PyPDF2
import os

def extract_text_from_pdf(pdf_path, progress_callback=None):
    """
    Extract text from a PDF file and return it as a string.
    
    Args:
        pdf_path (str): Path to the PDF file
        progress_callback (callable, optional): Function to report progress updates
        
    Returns:
        str: Extracted text from the PDF
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"The file {pdf_path} does not exist.")
    
    text = ""
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Get the number of pages
            num_pages = len(pdf_reader.pages)

            # Report the number of pages if progress callback provided
            if progress_callback:
                progress_callback(0.15, desc=f"PDF loaded: {num_pages} pages detected")
            
            # Extract text from each page
            for page_num in range(num_pages):
                # Update progress if callback provided
                if progress_callback and num_pages > 1:
                    # Scale progress from 0.15 to 0.5 based on page progress
                    page_progress = 0.15 + (0.35 * (page_num / num_pages))
                    progress_callback(page_progress, desc=f"Extracting page {page_num+1}/{num_pages}")
                
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
                
        # Final progress update for extraction
        if progress_callback:
            progress_callback(0.5, desc="Text extraction complete")
            
        return text
    
    except Exception as e:
        if progress_callback:
            progress_callback(0.5, desc="Error during text extraction")
        raise Exception(f"An error occurred while extracting text from {pdf_path}: {str(e)}")


def chunk_text(text, max_chunk_size=4000):
    """
    Split the text into chunks of approximately equal size.
    
    Args:
        text (str): The text to split into chunks
        max_chunk_size (int): Maximum size of each chunk in characters
        
    Returns:
        list: List of text chunks
    """
    # Split the text by paragraphs (newline characters)
    paragraphs = text.split('\n')
    
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        # If adding this paragraph would exceed the max chunk size, 
        # add the current chunk to the list and start a new one
        if len(current_chunk) + len(paragraph) > max_chunk_size and current_chunk:
            chunks.append(current_chunk)
            current_chunk = paragraph
        else:
            if current_chunk:
                current_chunk += "\n" + paragraph
            else:
                current_chunk = paragraph
    
    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(current_chunk)
   
    return chunks
