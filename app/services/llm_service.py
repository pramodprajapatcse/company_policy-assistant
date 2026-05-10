from openai import OpenAI
import logging
from app.config import config

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.client = OpenAI(
            api_key=config.NVIDIA_API_KEY,
            base_url=config.NVIDIA_API_BASE_URL,
        )
        self.model = config.NVIDIA_LLM_MODEL

    def generate_response(self, question, context_chunks):
        try:
            context = self._format_context(context_chunks)

            prompt = f"""
You are an AI assistant for company policies.

Context:
{context}

Question:
{question}

Instructions:
- Answer ONLY from context
- If not found, say: "Information not available in policy documents"
- Be concise and professional
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a policy assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"NVIDIA LLM Error: {e}")
            return f"Error: {str(e)}"

    def _format_context(self, context):
        return "\n\n".join([
            f"[{i}] {c['metadata'].get('document_name')} - {c['metadata'].get('section')}\n{c['content']}"
            for i, c in enumerate(context, 1)
        ])