from typing import Optional, Type, Any, List
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser
import os
import json
from dotenv import load_dotenv 

load_dotenv()

gemini_api_key= os.getenv("GEMINI_API_KEY")

class Flashcard(BaseModel):
    front: str
    back: str
    explanation: Optional[str] = None

class FlashcardSet(BaseModel):
    title: str
    flashcards: List[Flashcard]

class LLMConfig(BaseModel):
    model: str = "learnlm-1.5-pro-experimental"
    base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    temperature: float = 0.7
    api_key: Optional[str] = gemini_api_key

class ContentEngine:
    def __init__(self, llm_config: Optional[LLMConfig] = None):
        print("-----------------------------------\nFlashcard Agent Initialisation......")
        print("Initializing ContentEngine...")
        self.llm_config = llm_config or LLMConfig()
        self.llm = self._initialize_llm()
        print("ContentEngine initialized successfully")

    def _initialize_llm(self) -> ChatOpenAI:
        print(f"Setting up LLM with model: {self.llm_config.model}")
        if not (self.llm_config.api_key or os.getenv("OPENAI_API_KEY")):
            raise ValueError("No API key provided. Please set OPENAI_API_KEY environment variable or provide it in LLMConfig")
        
        return ChatOpenAI(
            model=self.llm_config.model,
            base_url=self.llm_config.base_url,
            api_key=self.llm_config.api_key,
            temperature=self.llm_config.temperature,
        )
    
    def display_flashcards(self, flashcard_set: FlashcardSet):
        """Print flashcards in a readable format"""
        print("\n" + "="*50)
        print(f"Flashcard Set: {flashcard_set.title}")
        print("="*50)
        
        for i, card in enumerate(flashcard_set.flashcards, 1):
            print(f"\nCard {i}:")
            print(f"Front: {card.front}")
            print(f"Back: {card.back}")
            if card.explanation:
                print(f"Explanation: {card.explanation}")
            print("-"*30)
            
    def generate_flashcards(
        self,
        topic: str,
        num: int = 5,
        prompt_template: Optional[str] = None,
        custom_instructions: Optional[str] = None,
        response_model: Optional[Type[Any]] = None,
        llm: Optional[ChatOpenAI] = None,
        **kwargs
    ) -> FlashcardSet:
        """
        Generate a set of flashcards for a given topic.
        """
        print(f"\nGenerating {num} flashcards for topic: {topic}")
        
        response_model = response_model or FlashcardSet
        parser = PydanticOutputParser(pydantic_object=response_model)
        format_instructions = parser.get_format_instructions()

        if prompt_template is None:
            prompt_template = """
            Generate a set of {num} flashcards on the topic: {topic}.
            
            Use the following research context to ensure accuracy:
            {context}

            For each flashcard:
            1. Create a clear, focused question or concept for the front
            2. Provide a concise, accurate answer on the back
            3. Include a brief explanation that adds context or examples
            
            The flashcards should:
            - Cover key concepts from the research context
            - Be factually accurate based on the provided information
            - Progress from fundamental to more advanced concepts
            - Use clear, precise language

            Structure the output as:
            - A title for the flashcard set
            - A list of flashcards, each with:
            - front: Question or concept
            - back: Answer or definition
            - explanation: Additional context
            """

        if custom_instructions:
            prompt_template += f"\n\nAdditional Instructions:\n{custom_instructions}"

        prompt_template += "\n\nRespond in this JSON format:\n{format_instructions}"

        print("Creating prompt template...")
        flashcard_prompt = PromptTemplate(
            input_variables=["num", "topic", "context"],
            template=prompt_template,
            partial_variables={"format_instructions": format_instructions}
        )

        llm_to_use = llm or self.llm
        print("Setting up LLM chain...")
        flashcard_chain = flashcard_prompt | llm_to_use
        
        try:
            print("Generating flashcards...")
            context = kwargs.get('custom_instructions', 'No specific context provided.')
            results = flashcard_chain.invoke(
                {"num": num, "topic": topic, "context": context}
            )
            print("Parsing results...")
            flashcard_set = parser.parse(results.content)
            print("Flashcards generated successfully!")
            
            self.display_flashcards(flashcard_set)
            
            return flashcard_set
        except Exception as e:
            print(f"\nError generating or parsing flashcards: {e}")
            if 'results' in locals():
                print("\nRaw output:", results.content)
            else:
                print("No results generated")
            return FlashcardSet(title=topic, flashcards=[])

# Example usage
if __name__ == "__main__":
    # Make sure you have set your OPENAI_API_KEY environment variable
    engine = ContentEngine()
    
    # Generate flashcards
    topic = "Python Programming Basics"
    try:
        flashcards = engine.generate_flashcards(topic, num=3)
    except Exception as e:
        print(f"Error in main execution: {e}")

