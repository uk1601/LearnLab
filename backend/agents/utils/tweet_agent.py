from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
load_dotenv()

class TweetContent(BaseModel):
    tweet: str

class TweetAgent:
    def __init__(self, api_key: str = os.getenv("GEMINI_API_KEY")):
        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing. Check your environment variables.")
        self.llm = ChatOpenAI(
            model="learnlm-1.5-pro-experimental",
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key=api_key,
            temperature=0.7,
        )

    def generate_tweet(self, query: str, rag_context: dict) -> TweetContent:
        """
        Generate a tweet based on the query and retrieved context.
        
        Args:
            query (str): The topic or query for the tweet.
            rag_context (dict): A dictionary containing "answer" and "evidence".

        Returns:
            TweetContent: A Pydantic model containing the tweet text.
        """
        prompt_template = """
        You are a technical tweet writer. Compose a concise, factually accurate tweet based on the topic and research context provided below. The entire tweet must be under 1000 characters.

        Topic: {query}

        Research Context:
        Answer: {answer}
        Evidence: {evidence}

        Guidelines:
        1. Maintain a clear, technical tone without overloading jargon.
        2. Highlight the core insight or finding in an engaging manner.
        3. Keep the structure tight and the tweet concise.
        4. Ensure accuracy by referencing specific evidence where relevant.
        5. Adhere to the 1000-character limit.
        """

        # Format the evidence as a single string
        formatted_evidence = " ".join(rag_context.get("evidence", []))

        prompt = ChatPromptTemplate.from_template(prompt_template)
        formatted_prompt = prompt.format_messages(
            query=query,
            answer=rag_context.get("answer", "No answer provided."),
            evidence=formatted_evidence
        )

        response = self.llm.invoke(formatted_prompt)
        if not response or not response.content:
            raise ValueError("Tweet generation failed.")

        # Ensure the tweet is within the character limit
        tweet_text = response.content.strip()

        return TweetContent(tweet=tweet_text)
