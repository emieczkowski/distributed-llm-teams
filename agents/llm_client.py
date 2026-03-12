"""
LLM Client for multi-provider support.

Supports: Anthropic, OpenAI, Google (Gemini).
"""
import asyncio
import os
from typing import Optional
from anthropic import Anthropic, AsyncAnthropic
from openai import OpenAI, AsyncOpenAI
from google import genai as google_genai
from google.genai.errors import ServerError


class LLMClient:

    def __init__(self, provider, model):
        """
        Initialize LLM client.

        Args:
            provider: "anthropic", "openai"
            model: Model name
        """
        self.provider = provider.lower()
        self.model = model or self._get_default_model()
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self._initialize_clients()

    def _get_default_model(self):
        """Get default model."""
        defaults = {
            "anthropic": "claude-sonnet-4-6",
            "openai": "gpt-4o",
            "google": "gemini-3-flash-preview",
            "mistral": "mistral-large-latest"
        }
        return defaults.get(self.provider, "claude-sonnet-4-6")

    def _initialize_clients(self):
        if self.provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not set in .env file")
            self.client = Anthropic(api_key=api_key)
            self.async_client = AsyncAnthropic(api_key=api_key)

        elif self.provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not set in .env file")
            self.client = OpenAI(api_key=api_key)
            self.async_client = AsyncOpenAI(api_key=api_key)

        elif self.provider == "google":
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not set in .env file")
            self.client = google_genai.Client(api_key=api_key)
            self.async_client = self.client 

        else:
            raise ValueError(f"Unsupported provider: {self.provider}. Supported: anthropic, openai, google.")

    def call(self, system, messages, temperature=0.7, max_tokens=4096):
        """
        Call the LLM with system prompt and messages.
        """
        if self.provider == "anthropic":
            response = self.client.messages.create(
                model=self.model,
                system=system,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            self.total_input_tokens += response.usage.input_tokens
            self.total_output_tokens += response.usage.output_tokens
            return response.content[0].text
        elif self.provider == "openai":
            full_messages = [{"role": "system", "content": system}] + messages
            response = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            self.total_input_tokens += response.usage.prompt_tokens
            self.total_output_tokens += response.usage.completion_tokens
            return response.choices[0].message.content
        elif self.provider == "google":
            response = self.client.models.generate_content(
                model=self.model,
                contents=self._to_google_contents(messages),
                config=google_genai.types.GenerateContentConfig(
                    system_instruction=system,
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                ),
            )
            self.total_input_tokens += response.usage_metadata.prompt_token_count or 0
            self.total_output_tokens += response.usage_metadata.candidates_token_count or 0
            return response.text or ""

    async def call_async(self, system, messages, temperature=0.7, max_tokens=4096):
        if self.provider == "anthropic":
            response = await self.async_client.messages.create(
                model=self.model,
                system=system,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            self.total_input_tokens += response.usage.input_tokens
            self.total_output_tokens += response.usage.output_tokens
            return response.content[0].text
        elif self.provider == "openai":
            full_messages = [{"role": "system", "content": system}] + messages
            response = await self.async_client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            self.total_input_tokens += response.usage.prompt_tokens
            self.total_output_tokens += response.usage.completion_tokens
            return response.choices[0].message.content
        elif self.provider == "google":
            for attempt in range(5):
                try:
                    response = await self.async_client.aio.models.generate_content(
                        model=self.model,
                        contents=self._to_google_contents(messages),
                        config=google_genai.types.GenerateContentConfig(
                            system_instruction=system,
                            temperature=temperature,
                            max_output_tokens=max_tokens,
                        ),
                    )
                    break
                except ServerError as e:
                    if attempt == 4:
                        raise
                    await asyncio.sleep(2 ** attempt)
            self.total_input_tokens += response.usage_metadata.prompt_token_count or 0
            self.total_output_tokens += response.usage_metadata.candidates_token_count or 0
            return response.text or ""

    @staticmethod
    def _to_google_contents(messages):
        """Convert OpenAI-style messages to Google GenAI."""
        contents = []
        for msg in messages:
            role = "model" if msg["role"] == "assistant" else "user"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})
        return contents


def create_llm_client(provider: Optional[str] = None, model: Optional[str] = None) -> LLMClient:
    provider = provider or os.getenv("LLM_PROVIDER", "anthropic")
    model = model or os.getenv("LLM_MODEL")
    return LLMClient(provider=provider, model=model)
