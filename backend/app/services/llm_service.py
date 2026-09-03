from google import genai


class LLMService:

    def __init__(
        self,
        api_key: str,
        model_name: str,
    ):

        self.client = genai.Client(
            api_key=api_key
        )

        self.model_name = (
            model_name
        )

    # =====================================================
    # GENERATE ANSWER
    # =====================================================

    def generate_answer(
        self,
        question: str,
        context: str,
        history=None,
    ):

        history_text = ""

        if history:

            history_parts = []

            for message in history:

                role = message.role

                content = (
                    message.content
                )

                history_parts.append(

                    f"{role}: {content}"
                )

            history_text = (
                "\n".join(
                    history_parts
                )
            )

        prompt = f"""
You are a document question-answering assistant.

Your job is to answer the user's question
using ONLY the provided document context.

IMPORTANT RULES:

1. Use only information present in the context.
2. Do not invent facts.
3. Do not use outside knowledge.
4. If the answer cannot be found in the context,
   clearly say that the information is not available
   in the provided document.
5. Keep the answer directly related to the question.
6. When useful, mention the relevant page number.
7. Do not claim something is present in the document
   unless the context supports it.

CONVERSATION HISTORY:

{history_text}

DOCUMENT CONTEXT:

{context}

USER QUESTION:

{question}

ANSWER:
"""

        response = (
            self.client
            .models
            .generate_content(

                model=
                    self.model_name,

                contents=prompt,
            )
        )

        return response.text