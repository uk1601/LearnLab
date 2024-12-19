
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from retreiving import PDFProcessor  # Import from your existing file
from typing import List, Dict, Any

load_dotenv()

class RAGApplication:
    def __init__(self):
        """Initialize RAG application with necessary components."""
        openai_api_key = os.getenv("OPENAI_API_KEY")
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        
        if not openai_api_key or not pinecone_api_key:
            raise ValueError("Missing API keys. Check your .env file.")
            
        self.llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key=openai_api_key
        )
        # Initialize PDFProcessor with both required API keys
        self.pdf_processor = PDFProcessor(
            openai_api_key=openai_api_key,
            pinecone_api_key=pinecone_api_key
        )
        self.document_chunks = None
        self.metadata = None
        
        # Create Pinecone index
        self.pdf_processor.create_index("pdf-embeddings")

    def process_document(self, pdf_path: str) -> bool:
        """Process and store document chunks."""
        try:
            # Read and process the document
            doc_info = self.pdf_processor.read_pdf(pdf_path)
            if not doc_info:
                return False
                
            # Index the document
            num_chunks = self.pdf_processor.index_document(doc_info)
            print(f"\nIndexed document into {num_chunks} chunks")
            return True
            
        except Exception as e:
            print(f"Error processing document: {str(e)}")
            return False

    def query_document(self, question: str, top_k: int = 3) -> Dict[str, Any]:
        """Query the document using the existing Pinecone index."""
        try:
            # Get relevant chunks using Pinecone
            relevant_chunks = self.pdf_processor.query(question, top_k)
            
            # Remove duplicate chunks and preserve order
            seen = set()
            unique_chunks = []
            for chunk in relevant_chunks:
                # Create a hash of the content (excluding the title) to check for duplicates
                content = chunk.split('\n', 2)[2] if '\n' in chunk else chunk
                if content not in seen:
                    seen.add(content)
                    unique_chunks.append(chunk)
            
            # Generate answer using LangChain
            answer = self.generate_answer(question, unique_chunks)
            
            return {
                "question": question,
                "answer": answer,
                "relevant_chunks": unique_chunks
            }
            
        except Exception as e:
            return {
                "error": f"Error processing query: {str(e)}",
                "question": question
            }

    def generate_answer(self, query: str, context_chunks: List[str]) -> str:
        """Generate answer using LangChain with retrieved context."""
        # Format context chunks with clear separation
        formatted_chunks = []
        for i, chunk in enumerate(context_chunks, 1):
            # Extract title and content
            parts = chunk.split('\n', 2)
            title = parts[0] if len(parts) > 0 else "Unknown"
            content = parts[2] if len(parts) > 2 else chunk
            
            formatted_chunk = f"[Document {i}] {title}\n{content}"
            formatted_chunks.append(formatted_chunk)
            
        context = "\n\n---\n\n".join(formatted_chunks)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful assistant that answers questions based on the provided context.
Your answers should be comprehensive and accurate, drawing specifically from the provided context.
If you find relevant information, explain it clearly and cite which document the information comes from."""),
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

def main():
    try:
        # Initialize RAG application
        print("Initializing RAG application...")
        rag_app = RAGApplication()
        
        # Process document
        print("\nProcessing document...")
        if not rag_app.process_document("textbook.pdf"):
            print("Error processing document")
            return

        # Interactive query loop
        print("\nRAG Application Ready! Type 'exit' to quit.")
        print("-" * 50)
        
        while True:
            question = input("\nEnter your question: ")
            if question.lower() == 'exit':
                break
                
            # Process query
            result = rag_app.query_document(question)
            
            if "error" in result:
                print(f"\nError: {result['error']}")
                continue
                
            # Print results
            print("\nAnswer:")
            print("-" * 50)
            print(result["answer"])
            print("\nRelevant Chunks Used:")
            print("-" * 50)
            for i, chunk in enumerate(result["relevant_chunks"], 1):
                print(f"\nChunk {i}:")
                print(chunk)
                print("-" * 50)
                
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()