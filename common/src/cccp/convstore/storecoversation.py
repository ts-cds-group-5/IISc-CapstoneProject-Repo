db_config = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': 5432
}
import uuid
from datetime import datetime
def store_conversation(conversation_json, db_config):
    import psycopg2
    import json
    from psycopg2 import sql

    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    cur.execute(
        sql.SQL("""
            INSERT INTO conversation_table (
                conv_id, user_id, conversation_blob, conversation_model, channel, source,
                created_at, updated_at, last_message_at, status, csr_handoff_needed, csr_assigned_to,
                topic_label, intent_label, sentiment_label, summary, outcome, user_feedback, language
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """),
        (
            conversation_json["conv_id"],
            conversation_json["user_id"],
            json.dumps(conversation_json["conversation_blob"]),  # Store as JSON string
            conversation_json["conversation_model"],
            conversation_json["channel"],
            conversation_json["source"],
            conversation_json["created_at"],
            conversation_json["updated_at"],
            conversation_json["last_message_at"],
            conversation_json["status"],
            conversation_json["csr_handoff_needed"],
            conversation_json["csr_assigned_to"],
            conversation_json["topic_label"],
            conversation_json["intent_label"],
            conversation_json["sentiment_label"],
            conversation_json["summary"],
            conversation_json["outcome"],
            conversation_json["user_feedback"],
            conversation_json["language"]
        )
    )
    conn.commit()
    cur.close() 
    conn.close()

sample_json = {
    "conv_id": str(uuid.uuid4()),
    "user_id": "prashanth",
    "conversation_blob": [
        {"sender": "user", "message": "Hello!", "timestamp": "2024-09-28T10:00:00"},
        {"sender": "bot", "message": "Hi there!", "timestamp": "2024-09-28T10:00:01"}
    ],
    "conversation_model": "ollama",
    "channel": "web",
    "source": "custom",
    "created_at": datetime.now().isoformat(),
    "updated_at": "2024-09-27T10:05:00",
    "last_message_at": "2024-09-27T10:05:00",
    "status": "active",
    "csr_handoff_needed": False,
    "csr_assigned_to": None,
    "topic_label": "greeting",
    "intent_label": "BILLING",
    "sentiment_label": "positive",
    "summary": "User greeted the bot.",
    "outcome": "greeted",
    "user_feedback": "very helpful",
    "language": "en_in"
}

store_conversation(sample_json, db_config)