# PDF Document Summarizer

An automated tool that extracts text from PDF documents and generates concise summaries using the OpenAI API and LangChain.

## Features

- PDF text extraction: Extract text content from PDF documents.
- AI-powered summarization: Generate concise summaries of long documents.
- User-friendly interface: Simple web interface for uploading PDFs and viewing summaries.
- Handles long documents: Efficiently processes and summarizes lengthy documents.

## Project Structure

```
pdf-summarizer/
│
├── app.py                  # Main application file with Gradio interface
├── pdf_extractor.py        # Module for extracting text from PDFs
├── summarizer.py           # Module for summarizing text using OpenAI API
├── .env                    # Environment variables file (create from .env.template)
├── .env.template           # Template for environment variables
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

## Prerequisites

- Python 3.8 or higher
- OpenAI API key

## Installation

1. Clone this repository or download the source code.

2. Create and activate a virtual environment:
```bash
python -m venv pdf_summarizer_env
source pdf_summarizer_env/bin/activate  # On Windows: pdf_summarizer_env\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Set up your environment variables:
```bash
cp .env.template .env
```
Then edit the `.env` file and add your OpenAI API key.

## Usage

1. Start the application:
```bash
python app.py
```

2. Open the provided URL in your web browser.

3. Upload a PDF document, and click "Process PDF".

4. View the extracted text and the generated summary.

## Customization

- To change the OpenAI model, modify the `model_name` parameter in the `TextSummarizer` class.
- Adjust summary length and style by modifying the prompt template in the `summarize_text` method.
- For better handling of specialized documents, you can extend the extraction and chunking functions.

## Limitations

- The tool may not correctly process PDFs with complex layouts or heavily image-based content.
- Summarization quality depends on the OpenAI model used and the clarity of the original text.
- Processing very large documents (100+ pages) may take significant time and API tokens.

## License

This project is licensed under the MIT License.