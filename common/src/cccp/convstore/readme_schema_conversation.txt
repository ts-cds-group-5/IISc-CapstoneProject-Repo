-- 1. Create enums for controlled values
CREATE TYPE conversation_model_enum AS ENUM ('ollama', '3.2');
CREATE TYPE channel_enum AS ENUM ('web', 'whatsapp', 'sms', 'email');
CREATE TYPE source_enum AS ENUM ('evershop', 'custom');
CREATE TYPE status_enum AS ENUM ('active', 'inactive');
CREATE TYPE intent_enum AS ENUM (
    'BILLING',
    'ORDER_TRACKING',
    'SUPPORT_REQUEST',
    'COMPLAINT',
    'PRODUCT_INFO',
    'INQUIRY',
    'OFF_TOPIC'
);
CREATE TYPE language_enum AS ENUM ('en_in', 'es', 'fr', 'de', 'it', 'pt', 'zh', 'ja', 'ko');

-- 2. Create the table
CREATE TABLE conversation_table (
    conv_id UUID DEFAULT gen_random_uuid() PRIMARY KEY, -- UUID with default generator
    user_id TEXT NOT NULL,                             -- Flexible: arbitrary or evershop user_id
    conversation_blob JSONB NOT NULL,                  -- Conversation JSON (user/system messages)
    conversation_model conversation_model_enum NOT NULL,
    channel channel_enum NOT NULL,
    source source_enum NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    last_message_at TIMESTAMP WITH TIME ZONE,
    status status_enum DEFAULT 'active',
    csr_handoff_needed BOOLEAN DEFAULT false,
    csr_assigned_to TEXT,                              -- Optional user_id for CSR
    topic_label TEXT,                                  -- Optional free-text topic
    intent_label intent_enum,                          -- Optional controlled intent
    sentiment_label TEXT,                              -- Optional sentiment
    summary TEXT,                                      -- Optional summary
    outcome TEXT,                                      -- Optional outcome
    user_feedback TEXT,                                -- Optional feedback
    language language_enum DEFAULT 'en_in'
);

select * from conversation_table