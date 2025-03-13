import os
import gradio as gr
from pdf_extractor import extract_text_from_pdf
from summarizer import TextSummarizer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def process_pdf(pdf_path, api_key=None):
    """
    Process a PDF file: extract text and generate a summary.
    
    Args:
        pdf_path (str): Path to the PDF file
        api_key (str, optional): OpenAI API key
        
    Returns:
        tuple: (extracted_text, summary)
    """
    try:
        # Extract text from PDF
        extracted_text = extract_text_from_pdf(pdf_path)
        
        # Initialize summarizer
        summarizer = TextSummarizer(api_key)
        
        # Generate summary
        summary = summarizer.summarize_long_text(extracted_text)
        
        return extracted_text, summary
    
    except Exception as e:
        return str(e), "An error occurred during summarization."

def create_interface():
    """
    Create and launch the Gradio interface.
    """
    # Default API key from environment variable
    default_api_key = os.getenv("OPENAI_API_KEY", "")
    
    # Create Gradio interface
    with gr.Blocks(title="PDF Summarizer") as interface:
        gr.Markdown("# PDF Document Summarizer")
        gr.Markdown("Upload a PDF document and get a concise summary.")
        
        with gr.Row():
            with gr.Column(scale=1):
                api_key_input = gr.Textbox(
                    label="OpenAI API Key (leave empty to use environment variable)",
                    placeholder="sk-...",
                    value=default_api_key,
                    type="password"
                )
                pdf_input = gr.File(label="Upload PDF")
                submit_button = gr.Button("Process PDF")
            
            with gr.Column(scale=2):
                text_output = gr.Textbox(label="Extracted Text", lines=10)
                summary_output = gr.Textbox(label="Summary", lines=10)
        
        submit_button.click(
            fn=process_pdf,
            inputs=[pdf_input, api_key_input],
            outputs=[text_output, summary_output]
        )
    
    return interface

if __name__ == "__main__":
    # Create and launch the interface
    interface = create_interface()
    interface.launch(share=True)