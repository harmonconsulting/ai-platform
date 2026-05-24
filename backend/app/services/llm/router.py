import requests

from app.core.config import settings


class LLMRouter:

    @staticmethod
    def chat(provider: str, model: str, message: str, context: str = ""):

        if context:
            prompt = f"""You are answering using the user's uploaded knowledge base.

Rules:
- Use the context below when relevant.
- If the context does not contain the answer, say you do not know from the uploaded documents.
- Cite the source filename when possible.
- Be clear and concise.

CONTEXT:
{context}

USER QUESTION:
{message}
"""
        else:
            prompt = message

        if provider == "ollama":
            return LLMRouter._ollama_chat(model, prompt)

        if provider == "openai":
            return LLMRouter._openai_chat(model, prompt)

        raise ValueError("Invalid provider")

    @staticmethod
    def _ollama_chat(model: str, prompt: str):
        response = requests.post(
            f"{settings.OLLAMA_BASE_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=300
        )

        response.raise_for_status()
        data = response.json()
        return data.get("response", "")

    @staticmethod
    def _openai_chat(model: str, prompt: str):
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}"
            },
            json={
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            },
            timeout=300
        )

        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
