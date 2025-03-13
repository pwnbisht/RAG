from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.core.config import get_settings

class LLMService:
    def __init__(self):
        settings = get_settings()
        self.llm = ChatOllama(
            model="llama3.2:1b",
            base_url=settings.ollama_url,
            temperature=0.7,
            system="You are a helpful AI assistant. Answer questions based on the provided context."
        )
        
        self.prompt_template = ChatPromptTemplate.from_template(
            """Use the following context to answer the question. 
            If you don't know the answer, say you don't know.
            
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
        """
        try:
            # Use custom prompt if provided
            prompt = self.prompt_template
            if custom_prompt:
                prompt = ChatPromptTemplate.from_template(custom_prompt)
                
            chain = prompt | self.llm | StrOutputParser()
            
            return await chain.ainvoke({
                "context": context,
                "question": query
            })
            
        except Exception as e:
            return "Sorry, I encountered an error processing your request."