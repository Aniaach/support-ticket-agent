from snowflake.snowpark.context import get_active_session

session = get_active_session()


def sql_escape(value):
    if value is None:
        return ""
    return str(value).replace("'", "''")


def normalize_record_keys(record):
    return {str(k).lower(): v for k, v in record.items()}


def get_all_tickets():
    df = session.sql("""
        SELECT *
        FROM support_tickets
        ORDER BY created_at DESC
    """).to_pandas()

    if df.empty:
        return []

    records = df.to_dict("records")
    return [normalize_record_keys(r) for r in records]


def get_selected_ticket(ticket_id):
    if ticket_id is None:
        return None

    try:
        ticket_id = int(ticket_id)
    except Exception:
        return None

    df = session.sql(f"""
        SELECT *
        FROM support_tickets
        WHERE ticket_id = {ticket_id}
        LIMIT 1
    """).to_pandas()

    if df.empty:
        return None

    record = df.to_dict("records")[0]
    return normalize_record_keys(record)


def get_next_ticket_id():
    result = session.sql("""
        SELECT COALESCE(MAX(ticket_id), 0) + 1 AS NEXT_ID
        FROM support_tickets
    """).collect()

    return int(result[0]["NEXT_ID"])


def insert_ticket(ticket):
    client_id = sql_escape(ticket["client_id"])
    sentiment = sql_escape(ticket["sentiment"])
    priority = sql_escape(ticket["priority"])
    department = sql_escape(ticket["department"])
    status = sql_escape(ticket["status"])
    feedback_sql = "NULL" if ticket["feedback"] is None else f"'{sql_escape(ticket['feedback'])}'"

    session.sql(f"""
        INSERT INTO support_tickets (
            ticket_id,
            client_id,
            ticket_text,
            sentiment,
            priority,
            confidence,
            department,
            generated_response,
            status,
            feedback,
            quality_score,
            safe_to_send,
            retry_count,
            created_at
        )
        VALUES (
            {ticket["ticket_id"]},
            '{client_id}',
            $$ {ticket["ticket_text"]} $$,
            '{sentiment}',
            '{priority}',
            {ticket["confidence"]},
            '{department}',
            $$ {ticket["generated_response"]} $$,
            '{status}',
            {feedback_sql},
            {ticket["quality_score"]},
            {str(ticket["safe_to_send"]).upper()},
            {ticket["retry_count"]},
            CURRENT_TIMESTAMP()
        )
    """).collect()


def insert_monitoring(ticket):
    sentiment = sql_escape(ticket["sentiment"])
    priority = sql_escape(ticket["priority"])
    department = sql_escape(ticket["department"])
    status = sql_escape(ticket["status"])

    session.sql(f"""
        INSERT INTO agent_monitoring (
            ticket_id,
            sentiment,
            priority,
            department,
            quality_score,
            safe_to_send,
            retry_count,
            final_status,
            created_at
        )
        VALUES (
            {ticket["ticket_id"]},
            '{sentiment}',
            '{priority}',
            '{department}',
            {ticket["quality_score"]},
            {str(ticket["safe_to_send"]).upper()},
            {ticket["retry_count"]},
            '{status}',
            CURRENT_TIMESTAMP()
        )
    """).collect()


def update_ticket_status(ticket_id, status):
    safe_status = sql_escape(status)

    session.sql(f"""
        UPDATE support_tickets
        SET status = '{safe_status}'
        WHERE ticket_id = {int(ticket_id)}
    """).collect()


def update_ticket_feedback(ticket_id, feedback):
    safe_feedback = sql_escape(feedback)

    session.sql(f"""
        UPDATE support_tickets
        SET feedback = '{safe_feedback}'
        WHERE ticket_id = {int(ticket_id)}
    """).collect()


def get_tickets_by_client(client_id):
    if not client_id:
        return []

    safe_client = sql_escape(client_id)

    df = session.sql(f"""
        SELECT *
        FROM support_tickets
        WHERE client_id = '{safe_client}'
        ORDER BY created_at DESC
    """).to_pandas()

    if df.empty:
        return []

    records = df.to_dict("records")
    return [normalize_record_keys(r) for r in records]


####################################
#      Monitoring functions        #
####################################

def get_ai_monitoring_stats():

    df = session.sql("""
        SELECT
            COUNT(*) as total_runs,
            AVG(quality_score) as avg_quality,
            AVG(retry_count) as avg_retry,
            AVG(CASE WHEN safe_to_send THEN 1 ELSE 0 END) as safe_rate,
            AVG(CASE WHEN final_status = 'Escalated' THEN 1 ELSE 0 END) as escalation_rate
        FROM agent_monitoring
    """).to_pandas()
    
    if df.empty:
        return None
    
    return normalize_record_keys(df.to_dict("records")[0])


def get_ticket_distribution_by_department():

    df = session.sql("""
        SELECT
            department,
            COUNT(*) as tickets
        FROM support_tickets
        GROUP BY department
        ORDER BY tickets DESC
    """).to_pandas()

    if df.empty:
        return []

    return [normalize_record_keys(r) for r in df.to_dict("records")]

def get_sentiment_distribution():

    df = session.sql("""
        SELECT
            sentiment,
            COUNT(*) as tickets
        FROM support_tickets
        GROUP BY sentiment
    """).to_pandas()

    if df.empty:
        return []

    return [normalize_record_keys(r) for r in df.to_dict("records")]


def get_retry_distribution():

    df = session.sql("""
        SELECT
            retry_count,
            COUNT(*) as tickets
        FROM agent_monitoring
        GROUP BY retry_count
        ORDER BY retry_count
    """).to_pandas()

    if df.empty:
        return []

    return [normalize_record_keys(r) for r in df.to_dict("records")]


def get_top_clients():

    df = session.sql("""
        SELECT
            client_id,
            COUNT(*) as tickets
        FROM support_tickets
        GROUP BY client_id
        ORDER BY tickets DESC
        LIMIT 10
    """).to_pandas()

    if df.empty:
        return []

    return [normalize_record_keys(r) for r in df.to_dict("records")]