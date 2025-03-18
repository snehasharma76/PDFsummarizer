import os
import gradio as gr
from pdf_extractor import extract_text_from_pdf
from summarizer import TextSummarizer
from qa_processor import DocumentQA
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Global variable to store QA system state
qa_system = None
current_text = None

def process_pdf(pdf_path, api_key=None, progress=gr.Progress()):
    """
    Process a PDF file: extract text, generate a summary, and prepare for Q&A.
    
    Args:
        pdf_path (str): Path to the PDF file
        api_key (str, optional): OpenAI API key
        progress (gradio.Progress): Gradio progress tracker
        
    Returns:
        tuple: (extracted_text, summary, qa_status, qa_panel_visibility)
    """
    global qa_system, current_text
    
    try:
        # Create a compatible progress callback function
        def progress_wrapper(value, message=""):
            progress(value)
        
        # Extract text from PDF with progress updates
        progress(0.1)
        extracted_text = extract_text_from_pdf(pdf_path, lambda p: progress(p))
        current_text = extracted_text
        
        # Check if text extraction was successful
        if not extracted_text or len(extracted_text.strip()) < 100:
            return (
                "The PDF contains too little text to process.",
                "The PDF contains too little text to summarize.",
                "Q&A not available: Text too short",
                gr.update(visible=False)
            )
        
        # Initialize summarizer
        progress(0.5)
        summarizer = TextSummarizer(api_key)
        
        # Generate summary
        summary = summarizer.summarize_long_text(extracted_text, progress_callback=lambda p: progress(p))
        
        # Initialize QA system
        progress(0.8)
        qa_system = DocumentQA(api_key=api_key)
        qa_init_success = qa_system.initialize_with_text(extracted_text, lambda p: progress(p))
        
        if qa_init_success:
            qa_status = "Q&A system ready. You can ask questions about the document."
            qa_visible = gr.update(visible=True)
        else:
            qa_status = "Q&A system initialization failed. You can still view the summary."
            qa_visible = gr.update(visible=False)
        
        progress(1.0, desc="Processing complete!")
        return extracted_text, summary, qa_status, qa_visible
    
    except Exception as e:
        error_msg = str(e)
        return error_msg, f"An error occurred during processing: {error_msg}", "Q&A not available due to processing error", gr.update(visible=False)

def ask_question(question):
    """
    Ask a question about the processed document.
    
    Args:
        question (str): Question to ask about the document
        
    Returns:
        str: Answer to the question
    """
    global qa_system
    
    if not qa_system or not qa_system.is_initialized:
        return "Please process a document first before asking questions."
    
    if not question or len(question.strip()) < 3:
        return "Please enter a valid question."
    
    try:
        # Get answer from QA system
        result = qa_system.ask_question(question)
        
        # Format the response
        answer = result["answer"]
        processing_time = result.get("processing_time", 0)
        
        response = f"{answer}\n\n*Question processed in {processing_time} seconds*"
        return response
    
    except Exception as e:
        return f"Error answering question: {str(e)}"

def create_interface():
    """
    Create and launch the Gradio interface.
    """
    # Default API key from environment variable
    default_api_key = os.getenv("OPENAI_API_KEY", "")
    
    # Create Gradio interface
    with gr.Blocks(title="PDF Summarizer with Q&A") as interface:
        gr.Markdown("# PDF Document Summarizer with Q&A")
        gr.Markdown("Upload a PDF document to get a concise summary and ask questions about the content.")
        
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
                
                # Status indicators
                status_indicator = gr.Markdown("Ready to process PDF.")
                qa_status_indicator = gr.Markdown(visible=False)
            
            with gr.Column(scale=2):
                with gr.Tabs() as tabs:
                    with gr.TabItem("Summary"):
                        summary_output = gr.Textbox(label="Summary", lines=12)
                    with gr.TabItem("Extracted Text"):
                        text_output = gr.Textbox(label="Extracted Text", lines=12)
                    with gr.TabItem("Q&A"):
                        with gr.Group(visible=False) as qa_group:
                            gr.Markdown("Ask questions about the document content:")
                            question_input = gr.Textbox(
                                label="Your Question",
                                placeholder="What is the main topic of this document?",
                                lines=2
                            )
                            ask_button = gr.Button("Ask Question", variant="primary")
                            answer_output = gr.Textbox(label="Answer", lines=8)
        
        # Define function to update status after processing
        def update_status_on_completion(text, summary, qa_status):
            # Only mark as complete if we didn't get an error
            if summary and not summary.startswith("An error occurred") and not summary.startswith("Error"):
                return "Processing complete! Summary generated successfully.", qa_status
            elif summary:
                return f"Error: {summary}", ""
            else:
                return "Processing failed. Please check your inputs and try again.", ""
        
        # Event handlers
        submit_button.click(
            fn=lambda: ("Processing PDF... Please wait", ""),
            inputs=None,
            outputs=[status_indicator, qa_status_indicator]
        ).then(
            fn=process_pdf,
            inputs=[pdf_input, api_key_input],
            outputs=[text_output, summary_output, qa_status_indicator, qa_group],
            show_progress="full"
        ).then(
            fn=update_status_on_completion,
            inputs=[text_output, summary_output, qa_status_indicator],
            outputs=[status_indicator, qa_status_indicator]
        )
        
        # Q&A button handler
        ask_button.click(
            fn=ask_question,
            inputs=[question_input],
            outputs=[answer_output]
        )
        
        # Clear button functionality
        def clear_outputs():
            global qa_system, current_text
            qa_system = None
            current_text = None
            return "", "", "Ready to process PDF.", "", gr.update(visible=False)
        
        clear_button.click(
            fn=clear_outputs,
            inputs=None,
            outputs=[text_output, summary_output, status_indicator, qa_status_indicator, qa_group]
        )
    
    return interface


if __name__ == "__main__":
    # Create and launch the interface
    interface = create_interface()
    interface.launch(share=True)