import sqlite3
import pandas as pd


class AuditDatabase:

    def __init__(self):

        self.db_path = "app/database/audit.db"

        self.connection = sqlite3.connect(
            self.db_path,
            check_same_thread=False
        )

        self.cursor = self.connection.cursor()

        self.create_table()

    def create_table(self):

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS email_audit (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                invoice_no TEXT,

                client_name TEXT,

                email TEXT,

                amount REAL,

                days_overdue INTEGER,

                stage TEXT,

                tone TEXT,

                subject TEXT,

                email_body TEXT,

                cta TEXT,

                status TEXT,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        self.connection.commit()

    def insert_email_log(
        self,
        record
    ):

        self.cursor.execute(
            """
            INSERT INTO email_audit (

                invoice_no,
                client_name,
                email,
                amount,
                days_overdue,
                stage,
                tone,
                subject,
                email_body,
                cta,
                status

            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.get("invoice_no"),
                record.get("client_name"),
                record.get("email"),
                record.get("amount"),
                record.get("days_overdue"),
                record.get("stage"),
                record.get("tone"),
                record.get("subject"),
                record.get("email_body"),
                record.get("cta"),
                record.get("status")
            )
        )

        self.connection.commit()

    def fetch_all_logs(self):

        self.cursor.execute(
            """
            SELECT * FROM email_audit
            ORDER BY created_at DESC
            """
        )

        rows = self.cursor.fetchall()

        columns = [
            "id",
            "invoice_no",
            "client_name",
            "email",
            "amount",
            "days_overdue",
            "stage",
            "tone",
            "subject",
            "email_body",
            "cta",
            "status",
            "created_at"
        ]

        return pd.DataFrame(
            rows,
            columns=columns
        )

    def is_connected(self):

        try:
            self.connection.execute(
                "SELECT 1"
            )
            return True

        except Exception:
            return False

    def close_connection(self):

        if self.connection:
            self.connection.close()