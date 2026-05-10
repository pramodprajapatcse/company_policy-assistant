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
You are a helpful AI assistant for company policies. Answer questions in a natural, conversational way as if you're explaining the information to a colleague.

Context:
{context}

Question:
{question}

Instructions:
- Answer ONLY from the provided context
- Write in a natural, conversational tone like you're speaking to someone
- Use complete sentences and flow naturally from one point to the next
- Do NOT use bullet points, numbered lists, or asterisks (*)
- Do NOT include section headers or references
- Vary your wording and phrasing each time the same question is asked - explain the same information using different words and sentence structures
- If information is not found in context, say: "I don't have that information in the policy documents"
- Keep your response helpful and easy to understand
"""

            logger.info(f"Calling NVIDIA LLM API with model: {self.model}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a policy assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Slightly higher for more variety
                max_tokens=500,
                stream=True  # Enable streaming
            )
            
            # Collect streaming response
            full_response = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
            
            logger.info(f"LLM Response generated successfully")
            return full_response

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