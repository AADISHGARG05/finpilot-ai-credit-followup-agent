import json

from langchain_groq import ChatGroq

from langchain_core.messages import (
    SystemMessage,
    HumanMessage
)

from app.core.config import (
    GROQ_API_KEY,
    MODEL_NAME
)

from app.models.schemas import (
    EmailResponse
)

from app.agents.prompt_templates import (
    SYSTEM_PROMPT,
    USER_PROMPT_TEMPLATE
)

from app.core.logger import logger


class LLMEmailGenerator:

    def __init__(self):

        if not GROQ_API_KEY:

            raise ValueError(
                "GROQ_API_KEY not found"
            )

        self.llm = ChatGroq(
            model_name=MODEL_NAME,
            groq_api_key=GROQ_API_KEY,
            temperature=0.4
        )

    def generate_email(
        self,
        invoice_data
    ):

        try:

            user_prompt = (
                USER_PROMPT_TEMPLATE.format(

                    client_name=invoice_data[
                        "client_name"
                    ],

                    invoice_no=invoice_data[
                        "invoice_no"
                    ],

                    amount=invoice_data[
                        "amount"
                    ],

                    due_date=invoice_data[
                        "due_date"
                    ],

                    days_overdue=invoice_data[
                        "days_overdue"
                    ],

                    tone=invoice_data[
                        "tone"
                    ],

                    stage=invoice_data[
                        "stage"
                    ],

                    payment_link=invoice_data[
                        "payment_link"
                    ]
                )
            )

            messages = [

                SystemMessage(
                    content=SYSTEM_PROMPT
                ),

                HumanMessage(
                    content=user_prompt
                )
            ]

            response = self.llm.invoke(
                messages
            )

            cleaned_response = (
                response.content
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

            start_index = (
                cleaned_response.find("{")
            )

            end_index = (
                cleaned_response.rfind("}") + 1
            )

            cleaned_response = (
                cleaned_response[
                    start_index:end_index
                ]
            )

            try:

                parsed_json = json.loads(
                    cleaned_response
                )

            except json.JSONDecodeError:

                logger.error(
                    f"Invalid JSON returned: "
                    f"{cleaned_response}"
                )

                print(
                    "\nINVALID JSON RESPONSE:\n"
                )

                print(cleaned_response)

                return None

            validated_response = (
                EmailResponse(
                    **parsed_json
                )
            )

            logger.info(
                f"Email generated for "
                f"{invoice_data['invoice_no']}"
            )

            return validated_response

        except Exception as e:

            logger.error(
                f"LLM generation error: {e}"
            )

            print(
                f"\nERROR GENERATING EMAIL:\n{e}\n"
            )

            return None