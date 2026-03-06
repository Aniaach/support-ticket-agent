CREATE OR REPLACE VIEW PROJET_TAL.PUBLIC.CLEAN_TICKETS AS
WITH raw_concat AS (
    SELECT
        SUBJECT,
        BODY,
        ANSWER,
        LANGUAGE,
        QUEUE,
        TYPE,
        PRIORITY,
        TAG_1, TAG_2, TAG_3, TAG_4, TAG_5, TAG_6, TAG_7, TAG_8,
        COALESCE(SUBJECT, '') || ' ' || COALESCE(BODY, '') || ' ' || COALESCE(ANSWER, '') AS RAW_TEXT
    FROM PROJET_TAL.PUBLIC.TICKETS
),
cleaned AS (
    SELECT
        *,
        REGEXP_REPLACE(
            REGEXP_REPLACE(
                REGEXP_REPLACE(
                    REGEXP_REPLACE(
                        REGEXP_REPLACE(
                            REGEXP_REPLACE(
                                LOWER(RAW_TEXT),

                                -- Salutations (EN + DE uniquement)
                                '(^|\\n)\\s*(dear\\s+(sir|madam|customer|team|support)|hello|hi there|hi|hey|good morning|good afternoon|good evening|hallo|guten\\s+(tag|morgen|abend)|sehr\\s+geehrte[r]?\\s*(damen\\s+und\\s+herren|herr|frau)?|liebe[r]?\\s*(kunde|kundin)?)[,\\s]*',
                                ' ', 1, 0, 'i'
                            ),

                            -- Signatures / politesse
                            '(best\\s+regards|kind\\s+regards|regards|sincerely|yours\\s+(truly|faithfully)|thank\\s+you|thanks|cheers|mit\\s+freundlichen\\s+gr[üu]ßen|freundliche\\s+gr[üu]ße|mfg|vielen\\s+dank|danke\\s*(sch[oö]n|sehr)?|hochachtungsvoll)[,\\s]*',
                            ' ', 1, 0, 'i'
                        ),

                        -- Boilerplate email
                        '(sent\\s+from\\s+my\\s+(iphone|android|mobile)|--+\\s*original\\s+message|---+)',
                        ' ', 1, 0, 'i'
                    ),

                    -- Suppression HTML
                    '<[^>]+>',
                    ' '
                ),

                -- Suppression URLs
                'https?://[^\\s]+|www\\.[^\\s]+',
                ' '
            ),

            -- Normalisation espaces
            '\\s{2,}',
            ' '
        ) AS CLEAN_TEXT_RAW
    FROM raw_concat
)
SELECT
    SUBJECT,
    BODY,
    ANSWER,
    LANGUAGE,
    QUEUE,
    TYPE,
    PRIORITY,
    TAG_1, TAG_2, TAG_3, TAG_4, TAG_5, TAG_6, TAG_7, TAG_8,
    TRIM(CLEAN_TEXT_RAW) AS CLEAN_TEXT
FROM cleaned
WHERE TRIM(CLEAN_TEXT_RAW) IS NOT NULL
  AND LENGTH(TRIM(CLEAN_TEXT_RAW)) > 10;