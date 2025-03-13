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
        gr.Markdown("Upload a PDF document and get a concise summary with real-time progress updates.")
        
        with gr.Row():
            with gr.Column(scale=1):
                api_key_input = gr.Textbox(
                    label="OpenAI API Key (leave empty to use environment variable)",
                    placeholder="sk-...",
                    value=default_api_key,
                    type="password"
                )
                pdf_input = gr.File(label="Upload PDF")
                
                with gr.Row():
                    submit_button = gr.Button("Process PDF", variant="primary")
                    clear_button = gr.Button("Clear", variant="secondary")
                
                # Status indicator
                status_indicator = gr.Markdown("Ready to process PDF.")
            
            with gr.Column(scale=2):
                with gr.Tabs():
                    with gr.TabItem("Summary"):
                        summary_output = gr.Textbox(label="Summary", lines=12)
                    with gr.TabItem("Extracted Text"):
                        text_output = gr.Textbox(label="Extracted Text", lines=12)
        
        # Define function to update status after processing
        def update_status_on_completion(text, summary):
            # Only mark as complete if we didn't get an error
            if summary and not summary.startswith("An error occurred") and not summary.startswith("Error"):
                return "Processing complete! Summary generated successfully."
            elif summary:
                return f"Error: {summary}"
            else:
                return "Processing failed. Please check your inputs and try again."
        
        # Event handlers
        submit_button.click(
            fn=lambda: "Processing PDF... Please wait",
            inputs=None,
            outputs=status_indicator
        ).then(
            fn=process_pdf,
            inputs=[pdf_input, api_key_input],
            outputs=[text_output, summary_output],
            show_progress="full"
        ).then(
            fn=update_status_on_completion,
            inputs=[text_output, summary_output],
            outputs=status_indicator
        )
        
        # Clear button functionality
        def clear_outputs():
            return "", "", "Ready to process PDF."
        
        clear_button.click(
            fn=clear_outputs,
            inputs=None,
            outputs=[text_output, summary_output, status_indicator]
        )
    
    return interface


if __name__ == "__main__":
    # Create and launch the interface
    interface = create_interface()
    interface.launch(share=True)