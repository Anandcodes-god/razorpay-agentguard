import json
import logging
from typing import Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from backend.config import get_settings

logger = logging.getLogger(__name__)

class LLMClient:
    """Client for interacting with LLM APIs (OpenAI or Gemini) for intent parsing and risk analysis."""
    
    def __init__(self):
        settings = get_settings()
        self.provider = settings.llm_provider
        self.model = settings.llm_model
        
        self.llm = self._initialize_llm(settings)
    
    def _initialize_llm(self, settings) -> Any:
        try:
            if self.provider == "gemini":
                from langchain_google_genai import ChatGoogleGenerativeAI
                return ChatGoogleGenerativeAI(
                    model=self.model,
                    google_api_key=settings.google_api_key,
                    temperature=0.1
                )
            else:
                from langchain_openai import ChatOpenAI
                return ChatOpenAI(
                    model_name=self.model,
                    openai_api_key=settings.openai_api_key,
                    temperature=0.1
                )
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            return None
    
    async def analyze_risk(self, context: Dict[str, Any], system_prompt: str) -> str:
        """Send context to LLM for risk analysis."""
        if not self.llm:
            return "LLM analysis unavailable. Relying on policy engine only."
            
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("user", "Analyze the following context for risks:\n{context}")
            ])
            
            chain = prompt | self.llm | StrOutputParser()
            
            result = await chain.ainvoke({
                "context": json.dumps(context, indent=2)
            })
            
            return result
        except Exception as e:
            logger.error(f"LLM risk analysis failed: {e}")
            return "LLM analysis unavailable. Relying on policy engine only."
    
    async def parse_intent(self, raw_instruction: str) -> Dict[str, Any]:
        """Parse a human instruction into structured intent contract fields."""
        fallback = {
            "purpose": "unknown",
            "categories": [],
            "max_amount": None,
            "merchant_constraints": [],
            "requires_confirmation_above": None
        }
        
        if not self.llm:
            return fallback
            
        try:
            system_prompt = """
            You are an AI that extracts structured payment intent from human instructions.
            Return a JSON object with the following fields:
            - purpose: string (brief description of the payment purpose)
            - categories: list of strings (e.g., 'food', 'travel', 'software')
            - max_amount: integer (maximum amount in paise, null if not specified)
            - merchant_constraints: list of strings (specific merchants allowed, empty if none)
            - requires_confirmation_above: integer (amount in paise above which confirmation is needed, null if not specified)
            """
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("user", "{instruction}")
            ])
            
            # Use JSON parser
            llm_with_json = self.llm.bind(response_format={"type": "json_object"})
            chain = prompt | llm_with_json | JsonOutputParser()
                
            result = await chain.ainvoke({"instruction": raw_instruction})
            return result
        except Exception as e:
            logger.error(f"LLM intent parsing failed: {e}")
            return fallback

def get_llm_client() -> LLMClient:
    """Factory function for LLMClient."""
    return LLMClient()
