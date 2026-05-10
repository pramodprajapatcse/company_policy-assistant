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
            logger.info(f"Generating response for question with {len(context_chunks)} context chunks")
            
            if not context_chunks:
                logger.warning("No context chunks provided")
                return "I could not find relevant information to answer your question."
            
            context = self._format_context(context_chunks)
            logger.info(f"Context formatted, length: {len(context)}")

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

            logger.info(f"Calling NVIDIA LLM API with model: {self.model}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a policy assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            logger.info(f"LLM Response generated successfully")
            return answer

        except Exception as e:
            error_msg = f"NVIDIA LLM Error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            print(f"[LLM ERROR] {error_msg}")
            raise  # Re-raise so it can be caught by the route handler

    def _format_context(self, context):
        try:
            formatted = []
            for i, c in enumerate(context, 1):
                try:
                    metadata = c.get('metadata', {}) if isinstance(c, dict) else {}
                    content = c.get('content', '') if isinstance(c, dict) else str(c)
                    doc_name = metadata.get('document_name', 'Unknown Document')
                    section = metadata.get('section', 'General')
                    formatted.append(f"[{i}] {doc_name} - {section}\n{content}")
                except Exception as e:
                    logger.warning(f"Error formatting chunk {i}: {e}")
                    formatted.append(f"[{i}] Error formatting this chunk")
            return "\n\n".join(formatted)
        except Exception as e:
            logger.error(f"Error in _format_context: {e}", exc_info=True)
            raise