-- =====================================================
-- Taxonomie des sentiments pour le projet RAG Tickets
-- =====================================================

CREATE OR REPLACE TABLE PROJET_TAL.PUBLIC.TAXONOMY_SENTIMENT (
    SENTIMENT_ID INTEGER AUTOINCREMENT,
    SENTIMENT_NAME STRING,
    SENTIMENT_CATEGORY STRING,
    DESCRIPTION STRING
);

-- -----------------------------------------------------
-- Sentiments négatifs
-- -----------------------------------------------------

INSERT INTO PROJET_TAL.PUBLIC.TAXONOMY_SENTIMENT 
(SENTIMENT_NAME, SENTIMENT_CATEGORY, DESCRIPTION)
VALUES
('Frustration', 'Negative', 'L’utilisateur exprime un mécontentement ou une irritation face à un problème.'),
('Stress', 'Negative', 'L’utilisateur montre une pression ou une inquiétude liée à la situation.'),
('Confusion', 'Negative', 'L’utilisateur ne comprend pas la situation ou la procédure.'),
('Insatisfaction', 'Negative', 'L’utilisateur indique que le service ou la solution ne répond pas à ses attentes.');

-- -----------------------------------------------------
-- Sentiments neutres
-- -----------------------------------------------------

INSERT INTO PROJET_TAL.PUBLIC.TAXONOMY_SENTIMENT 
(SENTIMENT_NAME, SENTIMENT_CATEGORY, DESCRIPTION)
VALUES
('Neutralité', 'Neutral', 'Le message est factuel, sans charge émotionnelle claire.');

-- -----------------------------------------------------
-- Sentiments positifs
-- -----------------------------------------------------

INSERT INTO PROJET_TAL.PUBLIC.TAXONOMY_SENTIMENT 
(SENTIMENT_NAME, SENTIMENT_CATEGORY, DESCRIPTION)
VALUES
('Positif', 'Positive', 'L’utilisateur exprime de la satisfaction ou de la gratitude.');
