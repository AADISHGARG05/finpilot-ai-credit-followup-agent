import pandas as pd

from tabulate import tabulate

from app.services.invoice_processor import (
    InvoiceProcessor
)

from app.services.llm_service import (
    LLMEmailGenerator
)

from app.database.db import (
    AuditDatabase
)

print("\nFinance Email Agent Started\n")

processor = InvoiceProcessor()

processor.df = pd.read_csv(
    "data/invoices.csv"
)

results = processor.process_invoices()

print("\nProcessed Invoice Records:\n")

print(
    tabulate(
        results,
        headers="keys",
        tablefmt="grid"
    )
)

llm_generator = (
    LLMEmailGenerator()
)

db = AuditDatabase()

print("\nGenerating AI Emails...\n")

for invoice in results:

    if invoice["stage"] == "Not Due":

        continue

    email_response = (
        llm_generator.generate_email(
            invoice
        )
    )

    if email_response:

        if hasattr(
            email_response,
            "dict"
        ):

            email_response = (
                email_response.dict()
            )

        print("\n" + "=" * 80)

        print(
            f"Invoice: "
            f"{invoice['invoice_no']}"
        )

        print(
            f"Stage: "
            f"{invoice['stage']}"
        )

        print(
            f"Tone: "
            f"{invoice['tone']}"
        )

        print("\nSUBJECT:\n")

        print(email_response["subject"])

        print("\nEMAIL BODY:\n")

        print(email_response["body"])

        print("\nCTA:\n")

        print(email_response["cta"])

        print("\n" + "=" * 80)

        audit_record = {

            "invoice_no":
                invoice["invoice_no"],

            "client_name":
                invoice["client_name"],

            "email":
                invoice["email"],

            "amount":
                invoice["amount"],

            "days_overdue":
                invoice["days_overdue"],

            "stage":
                invoice["stage"],

            "tone":
                invoice["tone"],

            "subject":
                email_response[
                    "subject"
                ],

            "email_body":
                email_response[
                    "body"
                ],

            "cta":
                email_response[
                    "cta"
                ],

            "status":
                "GENERATED"
        }

        db.insert_email_log(
            audit_record
        )

print(
    "\nAll generated emails "
    "saved to SQLite audit database.\n"
)