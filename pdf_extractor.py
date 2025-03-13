import PyPDF2
import os

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file and return it as a string.
    
    Args:
        pdf_path (str): Path to the PDF file
        
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
            
            # Extract text from each page
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
                
        return text
    
    except Exception as e:
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
    import PyPDF2
import os

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file and return it as a string.
    
    Args:
        pdf_path (str): Path to the PDF file
        
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
            
            # Extract text from each page
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
                
        return text
    
    except Exception as e:
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
