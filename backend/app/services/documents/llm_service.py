from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.core.config import get_settings
import logging

logger = logging.getLogger(__name__)


class LLMService:
    """
    Service to interact with the LLM model.

    It uses the langchain library to interact with the LLM model.
    The service provides a single method to generate a response based on a given query and context.
    """
    def __init__(self):
        settings = get_settings()
        self.llm = ChatOllama(
            model="llama3.2:1b",
            base_url=settings.ollama_url,
            temperature=0.7,
            system="You are a helpful AI assistant. Answer questions based on the provided context."
        )
        
        self.prompt_template = ChatPromptTemplate.from_template(
            """Use the following context to answer the question succinctly in markdown format. Follow these rules:

                1. Base your answer solely on the provided context.
                2. If the context does not provide enough information, respond with "I don't know" without any additional commentary.
                3. Keep your answer short and to the point.
                4. Do not include any extra text, explanations, or filler content beyond the answer.
                5. If the question contains multiple parts and the context allows, you may use bullet points or numbered lists for clarity.

                Context: {context}

                Question: {question}

                Answer:"""
        )

    async def generate_response(
        self,
        query: str,
        context: str,
        custom_prompt: str = None
    ) -> str:
        """
        Generate a response using Llama model

        Args:
            query (str): The question to answer.
            context (str): The context to use when generating the response.
            custom_prompt (str, optional): The custom prompt to use when generating the response. Defaults to None.

        Returns:
            str: The generated response.
        """
        try:
            prompt = self.prompt_template
            if custom_prompt:
                prompt = ChatPromptTemplate.from_template(custom_prompt)
                
            chain = prompt | self.llm | StrOutputParser()
            
            return await chain.ainvoke({
                "context": context,
                "question": query
            })
            
        except Exception as e:
            logger.error(f"Exception : {e}")
            return "Sorry, I encountered an error processing your request."
