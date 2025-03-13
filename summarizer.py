import os
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TextSummarizer:
    def __init__(self, api_key=None):
        """
        Initialize the TextSummarizer with an OpenAI API key.
        
        Args:
            api_key (str, optional): OpenAI API key. If not provided, it will look for OPENAI_API_KEY in environment variables.
        """
        # Use provided API key or get from environment variables
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("No OpenAI API key provided. Please provide an API key or set the OPENAI_API_KEY environment variable.")
        
        try:
            # Initialize the language model
            self.llm = ChatOpenAI(
                model_name="gpt-3.5-turbo",
                temperature=0,
                openai_api_key=self.api_key,
                request_timeout=60  # Increase timeout to 60 seconds
            )
        except Exception as e:
            print(f"Error initializing ChatOpenAI: {str(e)}")
            raise ValueError(f"Failed to initialize OpenAI client: {str(e)}")
    
    def summarize_text(self, text, max_length=1000):
        """
        Summarize the given text using OpenAI API.
        
        Args:
            text (str): The text to summarize
            max_length (int): Maximum length of the summary in characters
            
        Returns:
            str: Summarized text
        """
        try:
            # Check if text is empty or too short
            if not text or len(text.strip()) < 50:
                return "Text is too short to summarize."
            
            # Create documents
            docs = [Document(page_content=text)]
            
            # Define the summarization prompt
            prompt_template = """
            Write a concise summary of the following text. Highlight the main points and key information:
            
            TEXT: {text}
            
            SUMMARY:
            """
            
            prompt = ChatPromptTemplate.from_template(prompt_template)
            
            # Define a chain for summarization
            chain = load_summarize_chain(
                self.llm,
                chain_type="stuff",
                prompt=prompt,
            )
            
            # Generate summary
            summary = chain.run(docs)
            
            return summary
        
        except Exception as e:
            # Log the error for debugging
            print(f"Error in summarize_text: {str(e)}")
            return f"Error during summarization: {str(e)}"
    
    def summarize_long_text(self, text, max_chunk_size=4000, progress_callback=None):
        """
        Summarize a long text by breaking it into chunks and summarizing each chunk.
        Then summarize all the summaries to get a final summary.
        
        Args:
            text (str): The long text to summarize
            max_chunk_size (int): Maximum size of each chunk in characters
            progress_callback (callable, optional): Function to report progress updates
            
        Returns:
            str: Final summarized text
        """
        try:
            # Check if text is empty
            if not text or len(text.strip()) < 100:
                if progress_callback:
                    progress_callback(0.95, desc="Text too short to summarize")
                return "The extracted text is too short or empty to generate a meaningful summary."
                
            # Update progress if callback provided
            if progress_callback:
                progress_callback(0.6, desc="Splitting text into chunks...")
                
            # Split the text into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=max_chunk_size,
                chunk_overlap=200,
                separators=["\n\n", "\n", ". ", " ", ""]
            )
            
            chunks = text_splitter.split_text(text)
            total_chunks = len(chunks)
            
            if total_chunks == 0:
                if progress_callback:
                    progress_callback(0.95, desc="No valid content found")
                return "No valid content found to summarize."
            
            # Update progress
            if progress_callback:
                progress_callback(0.65, desc=f"Processing {total_chunks} text chunks...")
            
            # Summarize each chunk with progress updates
            chunk_summaries = []
            for i, chunk in enumerate(chunks):
                # Skip empty chunks
                if not chunk or len(chunk.strip()) < 50:
                    continue
                    
                # Update progress for each chunk
                if progress_callback and total_chunks > 1:
                    chunk_progress = 0.65 + (0.25 * (i / total_chunks))
                    progress_callback(chunk_progress, desc=f"Summarizing chunk {i+1}/{total_chunks}...")
                
                try:
                    summary = self.summarize_text(chunk)
                    if summary and not summary.startswith("Error during summarization"):
                        chunk_summaries.append(summary)
                except Exception as chunk_error:
                    print(f"Error summarizing chunk {i+1}: {str(chunk_error)}")
                    # Continue with other chunks even if one fails
                    continue
            
            # Check if we have any valid summaries
            if not chunk_summaries:
                if progress_callback:
                    progress_callback(0.95, desc="Failed to generate summaries")
                return "Unable to generate summary. Please check your API key and try again."
                
            # If we have multiple summaries, combine them
            if len(chunk_summaries) > 1:
                if progress_callback:
                    progress_callback(0.9, desc="Creating final summary from chunks...")
                    
                combined_summaries = "\n\n".join(chunk_summaries)
                try:
                    final_summary = self.summarize_text(combined_summaries)
                    
                    if progress_callback:
                        progress_callback(0.95, desc="Final summary complete")
                        
                    return final_summary
                except Exception as final_error:
                    print(f"Error creating final summary: {str(final_error)}")
                    # Return the combined summaries if final summarization fails
                    return "COMBINED CHUNK SUMMARIES:\n\n" + combined_summaries
                    
            elif len(chunk_summaries) == 1:
                if progress_callback:
                    progress_callback(0.95, desc="Summary complete")
                return chunk_summaries[0]
            else:
                if progress_callback:
                    progress_callback(0.95, desc="No content to summarize")
                return "No text to summarize."
                
        except Exception as e:
            print(f"Error in summarize_long_text: {str(e)}")
            if progress_callback:
                progress_callback(0.95, desc="Error during summarization process")
            return f"An error occurred during summarization: {str(e)}"