from google import genai


class LLMService:

    def __init__(
        self,
        api_key: str,
        model: str
    ):

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = model

    def generate_answer(
        self,
        question: str,
        results,
        history=None
    ):

        # --------------------------------
        # Retrieved context
        # --------------------------------

        context_parts = []

        for result in results:

            payload = result.payload

            context_parts.append(
                f"""
Source: {payload['filename']}
Page: {payload['page']}

{payload['text']}
"""
            )

        context = "\n\n".join(
            context_parts
        )

        # --------------------------------
        # Conversation history
        # --------------------------------

        history_text = ""

        if history:

            history_parts = []

            for message in history:

                history_parts.append(
                    f"{message.role.upper()}: "
                    f"{message.content}"
                )

            history_text = "\n".join(
                history_parts
            )

        # --------------------------------
        # Prompt
        # --------------------------------

        prompt = f"""
You are an AI document assistant.

Use the retrieved document context to answer
the user's question.

You may use the conversation history to
understand references such as:
"it", "that", "the second one", etc.

Rules:

1. Use the document context as the factual
   source.
2. Do not invent information.
3. Do not use outside knowledge.
4. If the answer cannot be found in the
   document context, say that you could not
   find it in the uploaded document.
5. Keep the answer clear and concise.

Conversation History:
----------------
{history_text}
----------------

Document Context:
----------------
{context}
----------------

Current Question:
{question}

Answer:
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )

        return response.text