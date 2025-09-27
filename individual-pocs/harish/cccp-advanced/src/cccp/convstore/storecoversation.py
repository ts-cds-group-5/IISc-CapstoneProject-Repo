import psycopg2
from psycopg2 import sql


def store_conversation(conv_id, user_id, conversation_model, channel, source, status, csr, csr_assigned_to, topic_label, intent_label, sentiment_label, summary, outcome, user_feedback, language, db_config):
    """
    Stores a conversation turn in the PostgreSQL database.

    Args:
        conv_id (str): Unique identifier for the conversation.
        user_id (str): User identifier.
        conversation_model (str): Model used.
        channel (str): Channel name.
        source (str): Source info.
        status (str): Status.
        csr (str): CSR name.
        csr_assigned_to (str): CSR assigned to.
        topic_label (str): Topic label.
        intent_label (str): Intent label.
        sentiment_label (str): Sentiment label.
        summary (str): Summary.
        outcome (str): Outcome.
        user_feedback (str): Feedback.
        language (str): Language.
        db_config (dict): Database configuration.
    """
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()

    cur.execute(
        sql.SQL("""
            CREATE TABLE IF NOT EXISTS conversations (
                conv_id TEXT,
                user_id TEXT,
                conversation_model TEXT,
                channel TEXT,
                source TEXT,
                status TEXT,
                csr TEXT,
                csr_assigned_to TEXT,
                topic_label TEXT,
                intent_label TEXT,
                sentiment_label TEXT,
                summary TEXT,
                outcome TEXT,
                user_feedback TEXT,
                language TEXT
            )
        """)
    )

    cur.execute(
        sql.SQL("""
            INSERT INTO conversations (
                conv_id, user_id, conversation_model, channel, source, status, csr, csr_assigned_to,
                topic_label, intent_label, sentiment_label, summary, outcome, user_feedback, language
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """),
        (
            conv_id, user_id, conversation_model, channel, source, status, csr, csr_assigned_to,
            topic_label, intent_label, sentiment_label, summary, outcome, user_feedback, language
        )
    )
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    sample_data = {
        "conv_id": "conv001",
        "user_id": "user123",
        "conversation_model": "gpt-4",
        "channel": "web",
        "source": "homepage",
        "status": "active",
        "csr": "csr_01",
        "csr_assigned_to": "csr_02",
        "topic_label": "billing",
        "intent_label": "query",
        "sentiment_label": "positive",
        "summary": "User asked about billing details.",
        "outcome": "Resolved",
        "user_feedback": "Very helpful!",
        "language": "en"
    }

    from .db_config import db_config  # Make sure db_config.py is in the same folder

    store_conversation(
        sample_data["conv_id"],
        sample_data["user_id"],
        sample_data["conversation_model"],
        sample_data["channel"],
        sample_data["source"],
        sample_data["status"],
        sample_data["csr"],
        sample_data["csr_assigned_to"],
        sample_data["topic_label"],
        sample_data["intent_label"],
        sample_data["sentiment_label"],
        sample_data["summary"],
        sample_data["outcome"],
        sample_data["user_feedback"],
        sample_data["language"],
        db_config
    )

# Example usage:
# db_config = {
#     'dbname': 'your_db',
#     'user': 'your_user',
#     'password': 'your_password',
#     'host': 'localhost',
#     'port': 5432
# }
# store_conversation('conv123', 'Hello!', 'Hi there!', '2024-06-01T12:00:00', db_config)