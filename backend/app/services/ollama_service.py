"""
Ollama service for local AI inference - No API keys required!
Uses local models for bias detection and embeddings
"""
import httpx
import json
from typing import List, Optional
from app.core.config import settings


class OllamaService:
    """
    Service for interacting with Ollama local AI models.

    Recommended models:
    - llama3.2 or mistral for analysis (fast and good quality)
    - nomic-embed-text for embeddings (384 dimensions)
    """

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self.embedding_model = settings.OLLAMA_EMBEDDING_MODEL
        self.timeout = 120.0  # Longer timeout for local inference

    async def _check_ollama_running(self) -> bool:
        """Check if Ollama is running"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/tags", timeout=5.0)
                return response.status_code == 200
        except:
            return False

    async def _ensure_model_exists(self, model_name: str) -> bool:
        """Check if model is available, provide instructions if not"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/tags", timeout=10.0)
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    model_names = [m.get("name", "").split(":")[0] for m in models]
                    return model_name.split(":")[0] in model_names
        except:
            pass
        return False

    async def generate(self, prompt: str, system: str = None) -> str:
        """
        Generate text using Ollama

        Args:
            prompt: The user prompt
            system: Optional system prompt

        Returns:
            Generated text response
        """
        try:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": False,
                        "options": {
                            "temperature": 0.3,
                            "num_predict": 4096
                        }
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    return result.get("message", {}).get("content", "")
                else:
                    raise Exception(f"Ollama error: {response.status_code}")

        except httpx.ConnectError:
            raise Exception(
                "Ollama is not running! Please start it with: ollama serve\n"
                f"Then pull the model: ollama pull {self.model}"
            )
        except Exception as e:
            raise Exception(f"Error generating with Ollama: {str(e)}")

    async def analyze_bias(self, text: str, bias_types: List[str] = None) -> dict:
        """
        Analyze text for bias using local Ollama model

        Args:
            text: The text to analyze
            bias_types: Specific bias types to check for

        Returns:
            Dictionary with analysis results
        """
        bias_types_str = ", ".join(bias_types) if bias_types else "all types"

        system_prompt = """You are an expert bias detection AI. Analyze text for biases including:
- gender: Gender-based stereotypes or discrimination
- political: Political leaning or partisan bias
- cultural: Cultural assumptions or ethnocentrism
- confirmation: Seeking confirming information only
- selection: Cherry-picking data or examples
- anchoring: Over-reliance on initial information
- other: Any other type of bias

You MUST respond ONLY with valid JSON in this exact format:
{
    "overall_score": 0.0 to 1.0,
    "summary": "brief summary",
    "bias_instances": [
        {
            "type": "gender|political|cultural|confirmation|selection|anchoring|other",
            "text": "the biased passage",
            "explanation": "why it's biased",
            "severity": 0.0 to 1.0,
            "start_position": 0,
            "end_position": 0,
            "suggestions": "how to fix it"
        }
    ]
}

If no bias found, return overall_score: 0 and empty bias_instances array."""

        user_prompt = f"""Analyze this text for {bias_types_str} of bias. Return ONLY valid JSON:

TEXT TO ANALYZE:
{text[:6000]}

JSON RESPONSE:"""

        try:
            response = await self.generate(user_prompt, system_prompt)

            # Try to extract JSON from response
            response = response.strip()

            # Find JSON in response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1

            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                result = json.loads(json_str)

                # Validate and set defaults
                result.setdefault("overall_score", 0.0)
                result.setdefault("summary", "Analysis complete")
                result.setdefault("bias_instances", [])

                return result
            else:
                return {
                    "overall_score": 0.0,
                    "summary": "Could not parse analysis results",
                    "bias_instances": []
                }

        except json.JSONDecodeError:
            return {
                "overall_score": 0.0,
                "summary": "Analysis completed but response format was invalid",
                "bias_instances": []
            }
        except Exception as e:
            raise Exception(f"Error analyzing bias: {str(e)}")

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector using Ollama

        Args:
            text: The text to embed

        Returns:
            List of floats representing the embedding vector
        """
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/embeddings",
                    json={
                        "model": self.embedding_model,
                        "prompt": text[:8000]  # Limit text length
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    return result.get("embedding", [])
                else:
                    raise Exception(f"Embedding error: {response.status_code}")

        except httpx.ConnectError:
            raise Exception(
                "Ollama is not running! Please start it with: ollama serve\n"
                f"Then pull the embedding model: ollama pull {self.embedding_model}"
            )
        except Exception as e:
            raise Exception(f"Error generating embedding: {str(e)}")

    async def generate_summary(self, text: str, max_length: int = 200) -> str:
        """Generate a summary of the text"""
        prompt = f"Summarize this text in {max_length} characters or less:\n\n{text[:3000]}"
        return await self.generate(prompt)

    async def get_status(self) -> dict:
        """Get Ollama service status"""
        is_running = await self._check_ollama_running()

        if not is_running:
            return {
                "status": "offline",
                "message": "Ollama is not running. Start with: ollama serve",
                "models_available": []
            }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/tags", timeout=10.0)
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]

                return {
                    "status": "online",
                    "message": "Ollama is running",
                    "models_available": model_names,
                    "analysis_model": self.model,
                    "embedding_model": self.embedding_model,
                    "analysis_model_ready": any(self.model.split(":")[0] in m for m in model_names),
                    "embedding_model_ready": any(self.embedding_model.split(":")[0] in m for m in model_names)
                }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "models_available": []
            }


# Singleton instance
ollama_service = OllamaService()
