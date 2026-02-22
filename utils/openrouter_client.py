import os
import openai
from dotenv import load_dotenv
from typing import Optional, Dict, Any

load_dotenv()

class OpenRouterClient:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = "anthropic/claude-3-haiku"
        self.dry_run = os.getenv("DRY_RUN", "true").lower() == "true"

        if not self.dry_run and self.api_key:
            # Configure OpenAI client to use OpenRouter
            openai.api_key = self.api_key
            openai.base_url = self.base_url
        elif not self.api_key:
            print("Warning: OPENROUTER_API_KEY not found in environment")

    def is_connected(self) -> bool:
        """Check if the client is properly configured with API key"""
        if self.dry_run:
            return False  # In dry run mode, we're not actually connected
        return bool(self.api_key)

    def get_client_info(self) -> str:
        """Get client connection info for dashboard"""
        if self.dry_run:
            return "None"
        elif self.api_key:
            return "Claude (OpenRouter)"
        else:
            return "None"

    def chat_completion(self, messages: list, **kwargs) -> Optional[str]:
        """Make a chat completion request to OpenRouter"""
        if self.dry_run:
            # In dry run mode, return a mock response
            return f"[DRY RUN] Would send request to {self.model} with messages: {messages}"

        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not set in environment")

        try:
            # Set default parameters
            params = {
                "model": self.model,
                "messages": messages,
                **kwargs
            }

            response = openai.chat.completions.create(**params)
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error making OpenRouter request: {e}")
            raise

    def test_connection(self) -> bool:
        """Test if we can establish a connection to OpenRouter"""
        if self.dry_run or not self.api_key:
            return False

        try:
            response = self.chat_completion(
                messages=[{"role": "user", "content": "Test connection"}],
                max_tokens=10
            )
            return response is not None
        except Exception:
            return False