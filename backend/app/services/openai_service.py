"""
OpenAI service for bias detection and embeddings
"""
from openai import AsyncOpenAI
from app.core.config import settings
from app.models.schemas import BiasInstance, BiasType
from typing import List
import json


class OpenAIService:
    """Service for interacting with OpenAI API"""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.embedding_model = settings.OPENAI_EMBEDDING_MODEL

    async def analyze_bias(self, text: str, bias_types: List[BiasType] = None) -> dict:
        """
        Analyze text for various types of bias using GPT-4

        Args:
            text: The text to analyze
            bias_types: Specific bias types to check for (if None, check all)

        Returns:
            Dictionary with analysis results
        """
        bias_types_str = ", ".join([bt.value for bt in bias_types]) if bias_types else "all types"

        system_prompt = """You are an expert bias detection AI. Your task is to analyze text
        for various types of bias including gender bias, political bias, cultural bias,
        confirmation bias, selection bias, anchoring bias, and others.

        For each bias instance found, provide:
        1. The type of bias
        2. The exact biased text passage
        3. A clear explanation of why it's biased
        4. A severity score from 0 to 1
        5. The start and end character positions
        6. Suggestions for improvement

        Respond in JSON format with the following structure:
        {
            "overall_score": <float 0-1>,
            "summary": "<brief summary>",
            "bias_instances": [
                {
                    "type": "<bias_type>",
                    "text": "<biased passage>",
                    "explanation": "<explanation>",
                    "severity": <float 0-1>,
                    "start_position": <int>,
                    "end_position": <int>,
                    "suggestions": "<improvement suggestions>"
                }
            ]
        }
        """

        user_prompt = f"""Analyze the following text for {bias_types_str} of bias:

{text}

Provide a comprehensive analysis in JSON format."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            raise Exception(f"Error analyzing bias with OpenAI: {str(e)}")

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text using OpenAI embeddings

        Args:
            text: The text to embed

        Returns:
            List of floats representing the embedding vector
        """
        try:
            response = await self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding

        except Exception as e:
            raise Exception(f"Error generating embedding: {str(e)}")

    async def generate_summary(self, text: str, max_length: int = 200) -> str:
        """
        Generate a summary of the text

        Args:
            text: The text to summarize
            max_length: Maximum length of summary

        Returns:
            Summary string
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates concise summaries."},
                    {"role": "user", "content": f"Summarize the following text in {max_length} characters or less:\n\n{text}"}
                ],
                temperature=0.5,
                max_tokens=100
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            raise Exception(f"Error generating summary: {str(e)}")


# Singleton instance
openai_service = OpenAIService()
