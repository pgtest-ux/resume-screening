# llm_client.py
import os
import json
from groq import Groq  # pip install groq


GROQ_DEFAULT_MODEL = "llama-3.3-70b-versatile"  # adjust if needed


class GroqLLMClient:
    """Wrapper around Groq chat completion API."""

    def __init__(self, model: str | None = None):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set.")
        self.client = Groq(api_key=api_key)
        self.model = model or GROQ_DEFAULT_MODEL

    def chat(self, system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
        """Send a chat completion request and return the text content."""
        extra_args = {}
        if json_mode:
            extra_args["response_format"] = {"type": "json_object"}

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
            **extra_args,
        )
        return response.choices[0].message.content

    def chat_json(self, system_prompt: str, user_prompt: str) -> dict:
        """Helper: run chat() expecting JSON and parse it."""
        text = self.chat(system_prompt, user_prompt, json_mode=True)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            raise ValueError(f"Failed to parse JSON from LLM response: {text}")


def create_llm_client(provider: str = "groq"):
    """Initialize LLM client."""
    if provider == "groq":
        return GroqLLMClient()

    raise ValueError(f"Unknown LLM provider: {provider}")
