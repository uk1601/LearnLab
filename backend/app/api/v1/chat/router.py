import json
import os
from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from openai import OpenAI
from openai.types.chat import ChatCompletionChunk, ChatCompletionMessageParam
from langchain.embeddings import OpenAIEmbeddings
from pinecone import Pinecone
from langchain.schema import HumanMessage, AIMessage
from app.core.deps import get_current_user
from app.models.user import User
from sqlalchemy.orm import Session
from app.schemas.chat.models import ChatRequest, Message
from app.core.config import settings
from app.core.logger import setup_logger, log_error
from agents.utils.rag_application import rag
from ....models.file import File as FileModel
from app.core.deps import (
    get_db,
    get_current_user    
)

router = APIRouter()
logger = setup_logger(__name__)


class RAGTools:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index = self.pc.Index("researchagent")
        self.namespace = "investment_research"

    def create_embedding(self, text: str) -> List[float]:
        """Create embedding for the input text"""
        try:
            embedding = self.openai_client.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            ).data[0].embedding
            return embedding
        except Exception as e:
            logger.error(f"Error creating embedding: {e}")
            raise


# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# Initialize Pinecone
pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(settings.PINECONE_INDEX_NAME)

# Initialize vector store
embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
vectorstore = Pinecone(index)


def convert_to_chat_messages(messages: List[Message]) -> List[ChatCompletionMessageParam]:
    return [{"role": msg.role, "content": msg.content} for msg in messages]


def convert_to_langchain_messages(messages: List[Message]):
    message_map = {
        "user": HumanMessage,
        "assistant": AIMessage
    }
    return [message_map[msg.role](content=msg.content) for msg in messages]


async def stream_langchain_response(chain, question: str, chat_history: List):
    """Stream responses from LangChain"""
    try:
        response = await chain.ainvoke({
            "question": question,
            "chat_history": chat_history
        })

        # Stream the response in chunks
        chunks = response['answer'].split()
        for chunk in chunks:
            yield f'0:{json.dumps(chunk + " ")}\n'

        # Send completion signal
        usage = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }
        yield f'e:{{"finishReason":"stop","usage":{json.dumps(usage)},"isContinued":false}}\n'

    except Exception as e:
        log_error(logger, e, {'operation': 'stream_langchain_response'})
        raise


async def stream_chat_completion(messages: List[ChatCompletionMessageParam]):
    """Fallback streaming using direct OpenAI completion"""
    try:
        stream = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages,
            stream=True,
            temperature=0.7,
        )

        for chunk in stream:
            if chunk.choices:
                choice = chunk.choices[0]
                if choice.finish_reason is not None:
                    if choice.finish_reason == "stop":
                        usage = {
                            "prompt_tokens": 0,
                            "completion_tokens": 0,
                            "total_tokens": 0
                        }
                        yield f'e:{{"finishReason":"stop","usage":{json.dumps(usage)},"isContinued":false}}\n'
                    continue

                if choice.delta.content:
                    yield f'0:{json.dumps(choice.delta.content)}\n'

    except Exception as e:
        log_error(logger, e, {'operation': 'stream_chat_completion'})
        yield f'0:{json.dumps("An error occurred during chat completion")}\n'
        yield 'e:{"finishReason":"error"}\n'


@router.post("")
async def chat(request: ChatRequest,db: Session = Depends(get_db)):
    """Chat endpoint with LangChain RAG and fallback to direct OpenAI"""
    try:        
        messages = convert_to_chat_messages(request.messages)        
        print("-------------------------")
        print(request.file_id)
        file = db.query(FileModel).filter(
            FileModel.id == request.file_id,            
            FileModel.is_deleted == False
        ).first()

        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        filename_without_extension = file.filename.rsplit('.', 1)[0]
        print(filename_without_extension)
        
        results = rag.query_document(request.messages[-1].content, filename_without_extension)
        messages = convert_to_chat_messages(request.messages)
        messages[-1]["content"] = results["question"] + results["answer"]
        response = StreamingResponse(
            stream_chat_completion(messages),
            media_type='text/plain',
        )
        response.headers['x-vercel-ai-data-stream'] = 'v1'

        return response

    except Exception as e:
        log_error(logger, e, {
            'operation': 'chat_langchain_failed',
            'fallback': 'using_direct_openai'
        })

        # Fallback to original OpenAI streaming
        messages = convert_to_chat_messages(request.messages)
        response = StreamingResponse(
            stream_chat_completion(messages),
            media_type='text/plain',
        )
        response.headers['x-vercel-ai-data-stream'] = 'v1'

        return response
