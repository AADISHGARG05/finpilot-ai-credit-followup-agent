import pandas as pd

from datetime import datetime

from app.core.logger import logger

from app.core.security import sanitize_text


class InvoiceProcessor:

    def __init__(self):

        self.df = None

    def calculate_days_overdue(
        self,
        due_date
    ):

        today = datetime.today()

        due_date = datetime.strptime(
            due_date,
            "%Y-%m-%d"
        )

        delta = today - due_date

        return delta.days

    def determine_stage_and_tone(
        self,
        days_overdue
    ):

        if 1 <= days_overdue <= 7:

            return (
                "Stage 1",
                "Warm & Friendly"
            )

        elif 8 <= days_overdue <= 14:

            return (
                "Stage 2",
                "Polite but Firm"
            )

        elif 15 <= days_overdue <= 21:

            return (
                "Stage 3",
                "Formal & Serious"
            )

        elif 22 <= days_overdue <= 30:

            return (
                "Stage 4",
                "Stern & Urgent"
            )

        elif days_overdue > 30:

            return (
                "Escalation",
                "Legal Review"
            )

        else:

            return (
                "Not Due",
                "No Action"
            )

    def process_invoices(self):

        processed_records = []

        for _, row in self.df.iterrows():

            days_overdue = (
                self.calculate_days_overdue(
                    row["due_date"]
                )
            )

            stage, tone = (
                self.determine_stage_and_tone(
                    days_overdue
                )
            )

            processed_record = {

                "invoice_no":
                    sanitize_text(
                        row["invoice_no"]
                    ),

                "client_name":
                    sanitize_text(
                        row["client_name"]
                    ),

                "email":
                    sanitize_text(
                        row["email"]
                    ),

                "amount":
                    row["amount"],

                "due_date":
                    row["due_date"],

                "payment_link":
                    row["payment_link"],

                "followup_count":
                    row["followup_count"],

                "days_overdue":
                    days_overdue,

                "stage":
                    stage,

                "tone":
                    tone
            }

            processed_records.append(
                processed_record
            )

        logger.info(
            "Invoices processed successfully"
        )

        return processed_records