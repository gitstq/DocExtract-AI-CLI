"""
AI Provider Module
Supports multiple AI providers for structured data extraction.
"""

import json
import re
import urllib.request
import urllib.error
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key
        self.base_url = base_url

    @abstractmethod
    def extract(self, document_text: str, schema_prompt: str, model: str = "default") -> Dict[str, Any]:
        """Extract structured data from document text using AI."""
        pass

    @abstractmethod
    def list_models(self) -> List[str]:
        """List available models from this provider."""
        pass

    @abstractmethod
    def test_connection(self) -> tuple[bool, str]:
        """Test connection to the provider."""
        pass

    def _clean_json_response(self, text: str) -> str:
        """Clean AI response to extract valid JSON."""
        # Remove markdown code blocks
        text = re.sub(r"```json\s*", "", text)
        text = re.sub(r"```\s*", "", text)
        text = text.strip()

        # Find JSON object
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return match.group(0)
        return text

    def _make_request(self, url: str, data: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Make HTTP POST request with JSON data."""
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))


class OpenAIProvider(AIProvider):
    """OpenAI-compatible provider (OpenAI, Azure, Groq, etc.)."""

    DEFAULT_BASE_URL = "https://api.openai.com/v1"

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        super().__init__(api_key, base_url or self.DEFAULT_BASE_URL)

    def extract(self, document_text: str, schema_prompt: str, model: str = "gpt-4o-mini") -> Dict[str, Any]:
        """Extract structured data using OpenAI API."""
        system_prompt = (
            "You are a precise document data extraction assistant. "
            "Extract information exactly as requested and return ONLY valid JSON. "
            "Do not include any explanations, markdown, or extra text."
        )

        user_prompt = f"{schema_prompt}\n\nDocument content:\n{document_text[:15000]}"

        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.1,
            "max_tokens": 4000,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        try:
            response = self._make_request(f"{self.base_url}/chat/completions", data, headers)
            content = response["choices"][0]["message"]["content"]
            cleaned = self._clean_json_response(content)
            return json.loads(cleaned)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"OpenAI API error: {e.code} - {error_body}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse AI response as JSON: {str(e)}")

    def list_models(self) -> List[str]:
        """List available models."""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        req = urllib.request.Request(
            f"{self.base_url}/models",
            headers=headers,
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))
                return [m["id"] for m in data.get("data", [])]
        except Exception:
            return ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]

    def test_connection(self) -> tuple[bool, str]:
        """Test connection to OpenAI API."""
        try:
            models = self.list_models()
            return True, f"Connected successfully. {len(models)} models available."
        except Exception as e:
            return False, str(e)


class OllamaProvider(AIProvider):
    """Ollama local AI provider."""

    DEFAULT_BASE_URL = "http://localhost:11434"

    def __init__(self, base_url: Optional[str] = None):
        super().__init__(None, base_url or self.DEFAULT_BASE_URL)

    def extract(self, document_text: str, schema_prompt: str, model: str = "llama3.2") -> Dict[str, Any]:
        """Extract structured data using Ollama API."""
        system_prompt = (
            "You are a precise document data extraction assistant. "
            "Extract information exactly as requested and return ONLY valid JSON. "
            "Do not include any explanations, markdown, or extra text."
        )

        user_prompt = f"{schema_prompt}\n\nDocument content:\n{document_text[:15000]}"

        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 4000,
            },
        }

        headers = {"Content-Type": "application/json"}

        try:
            response = self._make_request(f"{self.base_url}/api/chat", data, headers)
            content = response["message"]["content"]
            cleaned = self._clean_json_response(content)
            return json.loads(cleaned)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"Ollama API error: {e.code} - {error_body}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse AI response as JSON: {str(e)}")

    def list_models(self) -> List[str]:
        """List available Ollama models."""
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
                return [m["name"] for m in data.get("models", [])]
        except Exception:
            return ["llama3.2", "mistral", "phi4"]

    def test_connection(self) -> tuple[bool, str]:
        """Test connection to Ollama."""
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
                models = [m["name"] for m in data.get("models", [])]
                return True, f"Connected. {len(models)} models available: {', '.join(models[:5])}"
        except Exception as e:
            return False, f"Cannot connect to Ollama at {self.base_url}: {str(e)}"


class GeminiProvider(AIProvider):
    """Google Gemini provider."""

    DEFAULT_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

    def __init__(self, api_key: str):
        super().__init__(api_key, self.DEFAULT_BASE_URL)

    def extract(self, document_text: str, schema_prompt: str, model: str = "gemini-1.5-flash") -> Dict[str, Any]:
        """Extract structured data using Gemini API."""
        prompt = (
            f"{schema_prompt}\n\n"
            f"Document content:\n{document_text[:15000]}\n\n"
            f"Return ONLY valid JSON. No explanations, no markdown."
        )

        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 4000,
            },
        }

        url = f"{self.base_url}/models/{model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}

        try:
            response = self._make_request(url, data, headers)
            content = response["candidates"][0]["content"]["parts"][0]["text"]
            cleaned = self._clean_json_response(content)
            return json.loads(cleaned)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"Gemini API error: {e.code} - {error_body}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse AI response as JSON: {str(e)}")

    def list_models(self) -> List[str]:
        """List available Gemini models."""
        return [
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-1.5-flash-8b",
        ]

    def test_connection(self) -> tuple[bool, str]:
        """Test connection to Gemini API."""
        try:
            url = f"{self.base_url}/models?key={self.api_key}"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))
                models = [m["name"].split("/")[-1] for m in data.get("models", []) if "gemini" in m["name"]]
                return True, f"Connected. {len(models)} Gemini models available."
        except Exception as e:
            return False, str(e)


class ProviderRegistry:
    """Registry of available AI providers."""

    PROVIDERS = {
        "openai": OpenAIProvider,
        "ollama": OllamaProvider,
        "gemini": GeminiProvider,
    }

    @classmethod
    def create(cls, provider_name: str, **kwargs) -> AIProvider:
        """Create a provider instance by name."""
        provider_class = cls.PROVIDERS.get(provider_name.lower())
        if not provider_class:
            raise ValueError(f"Unknown provider: {provider_name}. Available: {', '.join(cls.PROVIDERS.keys())}")
        return provider_class(**kwargs)

    @classmethod
    def list_providers(cls) -> List[str]:
        """List available provider names."""
        return list(cls.PROVIDERS.keys())
