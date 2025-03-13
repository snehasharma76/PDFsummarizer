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
        
        # Initialize the language model
        self.llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0,
            openai_api_key=self.api_key
        )
    
    def summarize_text(self, text, max_length=1000):
        """
        Summarize the given text using OpenAI API.
        
        Args:
            text (str): The text to summarize
            max_length (int): Maximum length of the summary in characters
            
        Returns:
            str: Summarized text
        """
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
    
    def summarize_long_text(self, text, max_chunk_size=4000):
        """
        Summarize a long text by breaking it into chunks and summarizing each chunk.
        Then summarize all the summaries to get a final summary.
        
        Args:
            text (str): The long text to summarize
            max_chunk_size (int): Maximum size of each chunk in characters
            
        Returns:
            str: Final summarized text
        """
        # Split the text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=max_chunk_size,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        chunks = text_splitter.split_text(text)
        
        # Summarize each chunk
        chunk_summaries = []
        for chunk in chunks:
            summary = self.summarize_text(chunk)
            chunk_summaries.append(summary)
        
        # If we have multiple summaries, combine them
        if len(chunk_summaries) > 1:
            combined_summaries = "\n\n".join(chunk_summaries)
            final_summary = self.summarize_text(combined_summaries)
            return final_summary
        elif len(chunk_summaries) == 1:
            return chunk_summaries[0]
        else:
            return "No text to summarize."