
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from agents.utils.pdf_processor import PDFProcessor
from typing import List, Dict, Any, Optional  

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

class RAGApplication:
    def __init__(self):
        """Initialize RAG application with necessary components."""
        print(f"\nInitializing RAG Application..................")
        openai_api_key = os.getenv("OPENAI_API_KEY")
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        pinecone_index_name = os.getenv("PINECONE_INDEX_NAME","pdf-semantic-chunking")
        
        if not openai_api_key or not pinecone_api_key or not pinecone_index_name:
            raise ValueError("Missing API keys. Check your .env file.")

        self.llm = ChatOpenAI(model="learnlm-1.5-pro-experimental",base_url="https://generativelanguage.googleapis.com/v1beta/openai/", temperature=0.7, api_key=gemini_api_key)
        self.pdf_processor = PDFProcessor(
            openai_api_key=openai_api_key,
            pinecone_api_key=pinecone_api_key,
            pinecone_index_name=pinecone_index_name
        )
        
        # Track current PDF context
        self.current_pdf = None

    def process_document(self, pdf_path: str) -> bool:
        """Process and store document chunks."""
        try:
            # Read and process the document
            doc_info = self.pdf_processor.read_pdf(pdf_path)
            if not doc_info:
                return False
                
            # Index the document
            num_chunks, was_overwritten = self.pdf_processor.index_document(doc_info)
            print(f"\nIndexed document into {num_chunks} chunks")
            return True
            
        except Exception as e:
            print(f"Error processing document: {str(e)}")
            return False

    def set_current_pdf(self, pdf_title: str) -> bool:
        """Set the current PDF context for queries."""
        available_pdfs = self.pdf_processor.get_available_pdfs()
        if pdf_title in available_pdfs:
            self.current_pdf = pdf_title
            return True
        return False

    def list_available_pdfs(self) -> List[str]:
        """Get list of available PDF titles."""
        return self.pdf_processor.get_available_pdfs()

    def generate_answer(self, query: str, context_chunks: List[str]) -> str:
        """Generate answer using LangChain with retrieved context."""
        context = "\n\n".join(context_chunks)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant that answers questions based on the provided context."),
            ("user", """Answer the question based on the following context. 
If the answer cannot be found in the context, say "I cannot answer this based on the provided context."

Context:
{context}

Question: {question}

Answer:""")
        ])
        
        chain = prompt | self.llm
        
        response = chain.invoke({
            "context": context,
            "question": query
        })
        
        return response.content

    def query_document(self, question: str, pdf_title: Optional[str] = None, top_k: int = 3) -> Dict[str, Any]:
        """Query the document using the existing Pinecone index."""
        try:
            print(f"Querying document '{pdf_title}' with question: {question}..................")
            # Determine which PDF to query
            target_pdf = pdf_title or self.current_pdf
            
            # Get relevant chunks using Pinecone
            relevant_chunks = self.pdf_processor.query(question, target_pdf, top_k)
            
            # Debug logging
            print(f"Retrieved {len(relevant_chunks)} relevant chunks..................")

            # Generate answer using LangChain
            answer = self.generate_answer(question, relevant_chunks)
            
            return {
                "question": question,
                "answer": answer,
                "relevant_chunks": relevant_chunks,
                "pdf_title": target_pdf
            }
            
        except Exception as e:
            return {
                "error": f"Error processing query: {str(e)}",
                "question": question
            }

def main():
    try:
        # Initialize RAG application
        print("Initializing RAG application...")
        rag_app = RAGApplication()
        
        # Process document(s)
        print("\nProcessing documents...")
        # Add your PDF files here - update these paths to your actual PDF locations
        pdf_files = [
            "/Users/akashvarun/Data-Science/ai-podcast/textbook.pdf",
            "/Users/akashvarun/Northeastern/ebooks/Databricks_Book-of-MLOps-2nd-Edition.pdf"
        ]
        
        for pdf_file in pdf_files:
            if not rag_app.process_document(pdf_file):
                print(f"Error processing document: {pdf_file}")
                continue
            print(f"Successfully processed: {pdf_file}")

        # Interactive query loop
        print("\nRAG Application Ready! Commands:")
        print("- 'list': Show available PDFs")
        print("- 'use <pdf_title>': Select a PDF to query")
        print("- 'exit': Quit the application")
        print("-" * 50)
        
        while True:
            command = input("\nEnter command or question: ").strip()
            
            if command.lower() == 'exit':
                break
            elif command.lower() == 'list':
                pdfs = rag_app.list_available_pdfs()
                print("\nAvailable PDFs:")
                for pdf in pdfs:
                    print(f"- {pdf}")
                continue
            elif command.lower().startswith('use '):
                pdf_title = command[4:].strip()
                if rag_app.set_current_pdf(pdf_title):
                    print(f"\nNow querying PDF: {pdf_title}")
                else:
                    print(f"\nError: PDF '{pdf_title}' not found")
                continue
                
            # Process query
            if not rag_app.current_pdf:
                print("\nPlease select a PDF first using 'use <pdf_title>'")
                continue
                
            result = rag_app.query_document(command)
            
            if "error" in result:
                print(f"\nError: {result['error']}")
                continue
                
            # Print results
            print(f"\nAnswering from PDF: {result['pdf_title']}")
            print("\nAnswer:")
            print("-" * 50)
            print(result["answer"])
            print("\nRelevant Chunks Used:")
            print("-" * 50)
            for i, chunk in enumerate(result["relevant_chunks"], 1):
                print(f"\nChunk {i}:")
                print(chunk[:200] + "..." if len(chunk) > 200 else chunk)
                print("-" * 50)
                
    except Exception as e:
        print(f"An error occurred: {str(e)}")
rag = RAGApplication()
if __name__ == "__main__":
    main()