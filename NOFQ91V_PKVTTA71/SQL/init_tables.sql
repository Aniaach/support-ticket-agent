CREATE OR REPLACE TABLE support_tickets (
ticket_id INT,
client_id STRING,
ticket_text STRING,
sentiment STRING,
priority STRING,
confidence FLOAT,
department STRING,
generated_response STRING,
status STRING,
feedback STRING,
quality_score FLOAT,
safe_to_send BOOLEAN,
retry_count INT,
created_at TIMESTAMP
);

CREATE OR REPLACE TABLE agent_monitoring (
ticket_id INT,
sentiment STRING,
priority STRING,
department STRING,
quality_score FLOAT,
safe_to_send BOOLEAN,
retry_count INT,
final_status STRING,
created_at TIMESTAMP
);