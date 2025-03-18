import os
import time
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.schema import Document
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DocumentQA:
    def __init__(self, api_key=None):
        """Initialize the QA processor with OpenAI API key."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.vector_store = None
        self.qa_chain = None
        self.is_initialized = False
        
        if not self.api_key:
            raise ValueError("No OpenAI API key provided. Please provide an API key or set the OPENAI_API_KEY environment variable.")

    def initialize_with_text(self, text, progress_callback=None):
        """
        Initialize the QA system with document text.
        
        Args:
            text (str): The extracted text from the PDF
            progress_callback (callable): Function to report progress
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            if progress_callback:
                progress_callback(0.82)
            
            # Skip if text is too short
            if not text or len(text.strip()) < 100:
                if progress_callback:
                    progress_callback(0.85)
                return False
            
            # Split text into chunks for better processing
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=100,
                separators=["\n\n", "\n", ". ", " ", ""]
            )
            chunks = text_splitter.split_text(text)
            
            if len(chunks) == 0:
                if progress_callback:
                    progress_callback(0.85)
                return False
            
            if progress_callback:
                progress_callback(0.85)
            
            # Create embeddings and store in vector database
            embeddings = OpenAIEmbeddings(openai_api_key=self.api_key)
            
            # Convert chunks to Document objects
            docs = [Document(page_content=chunk) for chunk in chunks]
            
            # Create the vector store
            self.vector_store = FAISS.from_documents(docs, embeddings)
            
            if progress_callback:
                progress_callback(0.9)
            
            # Initialize the QA chain
            retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
            llm = ChatOpenAI(
                model_name="gpt-3.5-turbo",
                temperature=0,
                openai_api_key=self.api_key,
                request_timeout=60
            )
            
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=True
            )
            
            self.is_initialized = True
            if progress_callback:
                progress_callback(0.95)
            
            return True
            
        except Exception as e:
            if progress_callback:
                progress_callback(0.9)
            print(f"Error initializing QA system: {str(e)}")
            return False

    def ask_question(self, question):
        """
        Ask a question about the document.
        
        Args:
            question (str): The question to ask about the document
            
        Returns:
            dict: Contains 'answer' and 'sources' keys
        """
        if not self.is_initialized:
            return {
                "answer": "Error: QA system not initialized. Please process a document first.",
                "sources": []
            }
            
        try:
            # Get answer from the QA chain
            start_time = time.time()
            result = self.qa_chain({"query": question})
            end_time = time.time()
            
            # Format the response
            response = {
                "answer": result["result"],
                "sources": [doc.page_content for doc in result["source_documents"]],
                "processing_time": round(end_time - start_time, 2)
            }
            
            return response
            
        except Exception as e:
            print(f"Error in ask_question: {str(e)}")
            return {
                "answer": f"Error processing question: {str(e)}",
                "sources": [],
                "processing_time": 0
            }