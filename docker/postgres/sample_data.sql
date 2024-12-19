-- Sample Data Population Script
-- This script adds sample data for testing and development

-- Clear existing data (if needed) while maintaining referential integrity
DO $$ BEGIN
    -- Disable triggers temporarily
    ALTER TABLE users DISABLE TRIGGER ALL;
    ALTER TABLE files DISABLE TRIGGER ALL;
    ALTER TABLE flashcard_decks DISABLE TRIGGER ALL;
    ALTER TABLE flashcards DISABLE TRIGGER ALL;
    ALTER TABLE learning_progress DISABLE TRIGGER ALL;
    
    -- Clear data
    DELETE FROM learning_progress;
    DELETE FROM flashcards;
    DELETE FROM flashcard_decks;
    DELETE FROM files;
    DELETE FROM users;
    
    -- Re-enable triggers
    ALTER TABLE users ENABLE TRIGGER ALL;
    ALTER TABLE files ENABLE TRIGGER ALL;
    ALTER TABLE flashcard_decks ENABLE TRIGGER ALL;
    ALTER TABLE flashcards ENABLE TRIGGER ALL;
    ALTER TABLE learning_progress ENABLE TRIGGER ALL;
END $$;

-- Insert admin user
INSERT INTO users (
    id,
    email,
    username,
    password_hash,
    full_name,
    is_active,
    created_at,
    updated_at
) VALUES (
    '340003bc-3dbc-4c0b-8c4c-777126934e5d',
    'admin@gmail.com',
    'admin',
    '$2b$12$XG5nODyQtvlyySXgowYcW.axuiBncZvtxaOf3d12s0fXujy.9l.Mi',  -- Note: In production, this should be properly hashed
    'Admin User',
    true,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

-- Insert sample files
INSERT INTO files (
    id,
    user_id,
    filename,
    s3_key,
    file_size,
    mime_type,
    created_at,
    updated_at,
    is_deleted
) VALUES 
(
    '70160a20-bec3-4128-a7f0-132efbf294fa',
    '340003bc-3dbc-4c0b-8c4c-777126934e5d',
    'chat_export (11).pdf',
    'users/340003bc-3dbc-4c0b-8c4c-777126934e5d/25a48056-9810-43e6-8275-dcde8328cf8f.pdf',
    236395,
    'application/pdf',
    '2024-12-01 20:16:15.79933+00',
    '2024-12-01 20:16:15.799335+00',
    false
),
(
    '32db86f1-3420-4f0d-aaa0-966673819605',
    '340003bc-3dbc-4c0b-8c4c-777126934e5d',
    'chat_export (11).pdf',
    'users/340003bc-3dbc-4c0b-8c4c-777126934e5d/109076fb-0435-4c73-a6c4-33f975ef015e.pdf',
    236395,
    'application/pdf',
    '2024-12-01 20:22:14.446214+00',
    '2024-12-01 20:22:14.44622+00',
    false
),
(
    'f7ecee5f-c227-4102-b5ea-ae44469a5ed2',
    '340003bc-3dbc-4c0b-8c4c-777126934e5d',
    'chat_export (11).pdf',
    'users/340003bc-3dbc-4c0b-8c4c-777126934e5d/f5a26867-515d-4140-bf85-7c67bce857b5.pdf',
    236395,
    'application/pdf',
    '2024-12-01 20:56:13.619292+00',
    '2024-12-01 20:56:13.619303+00',
    false
);

-- Insert sample flashcard decks
INSERT INTO flashcard_decks (
    id,
    user_id,
    file_id,
    title,
    description,
    is_active,
    created_at,
    updated_at
) VALUES 
(
    '98f0f1d0-0000-4000-a000-000000000001',
    '340003bc-3dbc-4c0b-8c4c-777126934e5d',
    '70160a20-bec3-4128-a7f0-132efbf294fa',
    'Machine Learning Concepts',
    'Key concepts and definitions from Machine Learning course',
    true,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
),
(
    '98f0f1d0-0000-4000-a000-000000000002',
    '340003bc-3dbc-4c0b-8c4c-777126934e5d',
    '32db86f1-3420-4f0d-aaa0-966673819605',
    'Deep Learning Fundamentals',
    'Neural networks and deep learning concepts',
    true,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
),
(
    '98f0f1d0-0000-4000-a000-000000000003',
    '340003bc-3dbc-4c0b-8c4c-777126934e5d',
    'f7ecee5f-c227-4102-b5ea-ae44469a5ed2',
    'Data Science Notes',
    'Important data science concepts and formulas',
    true,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

-- Insert sample flashcards
-- Machine Learning Concepts Deck
INSERT INTO flashcards (
    id, deck_id, front_content, back_content, page_number, is_active
) VALUES 
(
    '99f0f1d0-0000-4000-a000-000000000001',
    '98f0f1d0-0000-4000-a000-000000000001',
    'What is supervised learning?',
    'A type of machine learning where models are trained on labeled data to predict outputs for unseen inputs.',
    1,
    true
),
(
    '99f0f1d0-0000-4000-a000-000000000002',
    '98f0f1d0-0000-4000-a000-000000000001',
    'What is gradient descent?',
    'An optimization algorithm used to minimize the cost function by iteratively moving towards the minimum.',
    2,
    true
);

-- Deep Learning Fundamentals Deck
INSERT INTO flashcards (
    id, deck_id, front_content, back_content, page_number, is_active
) VALUES 
(
    '99f0f1d0-0000-4000-a000-000000000003',
    '98f0f1d0-0000-4000-a000-000000000002',
    'What is a neural network?',
    'A computational model inspired by biological neural networks, consisting of interconnected nodes organized in layers.',
    1,
    true
),
(
    '99f0f1d0-0000-4000-a000-000000000004',
    '98f0f1d0-0000-4000-a000-000000000002',
    'Explain backpropagation',
    'Algorithm for training neural networks by calculating gradients of the loss function with respect to weights.',
    2,
    true
);

-- Data Science Notes Deck
INSERT INTO flashcards (
    id, deck_id, front_content, back_content, page_number, is_active
) VALUES 
(
    '99f0f1d0-0000-4000-a000-000000000005',
    '98f0f1d0-0000-4000-a000-000000000003',
    'What is feature engineering?',
    'The process of creating new features or transforming existing ones to improve model performance.',
    1,
    true
),
(
    '99f0f1d0-0000-4000-a000-000000000006',
    '98f0f1d0-0000-4000-a000-000000000003',
    'Explain p-value',
    'A statistical measure that helps determine the significance of results, ranging from 0 to 1.',
    2,
    true
);

-- Insert sample learning progress
INSERT INTO learning_progress (
    id,
    user_id,
    flashcard_id,
    ease_factor,
    interval,
    repetitions,
    last_reviewed,
    next_review,
    created_at,
    updated_at
)
SELECT 
    uuid_generate_v4(),
    '340003bc-3dbc-4c0b-8c4c-777126934e5d',
    id,
    2.5,  -- Default ease factor
    floor(random() * 20 + 1)::integer,  -- Random interval between 1 and 20
    floor(random() * 5)::integer,  -- Random number of repetitions
    CURRENT_TIMESTAMP - (random() * interval '30 days'),  -- Random last review date within last 30 days
    CURRENT_TIMESTAMP + (random() * interval '30 days'),  -- Random next review date within next 30 days
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
FROM flashcards;

-- Verify data
DO $$ 
DECLARE 
    user_count integer;
    file_count integer;
    deck_count integer;
    card_count integer;
    progress_count integer;
BEGIN
    SELECT COUNT(*) INTO user_count FROM users;
    SELECT COUNT(*) INTO file_count FROM files;
    SELECT COUNT(*) INTO deck_count FROM flashcard_decks;
    SELECT COUNT(*) INTO card_count FROM flashcards;
    SELECT COUNT(*) INTO progress_count FROM learning_progress;
    
    RAISE NOTICE 'Data loaded: % users, % files, % decks, % cards, % progress records', 
        user_count, file_count, deck_count, card_count, progress_count;
END $$;