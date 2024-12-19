-- Insert question responses
INSERT INTO question_responses (
    id,
    attempt_id,
    question_id,
    response,
    is_correct,
    confidence_score,
    time_taken,
    created_at
) VALUES 
-- Responses for first ML Quiz attempt
(
    'g1f0f1d0-0000-4000-a000-000000000001'::uuid,
    'f1f0f1d0-0000-4000-a000-000000000001'::uuid,
    'b1f0f1d0-0000-4000-a000-000000000001'::uuid,
    'K-means Clustering',
    true,
    NULL,
    120,
    CURRENT_TIMESTAMP - interval '10 days' + interval '15 minutes'
),
(
    'g1f0f1d0-0000-4000-a000-000000000002'::uuid,
    'f1f0f1d0-0000-4000-a000-000000000001'::uuid,
    'b1f0f1d0-0000-4000-a000-000000000002'::uuid,
    'Gradient descent is an optimization algorithm that minimizes the cost function by iteratively updating parameters in the direction of steepest descent. It calculates gradients to determine the optimal update direction.',
    true,
    0.85,
    180,
    CURRENT_TIMESTAMP - interval '10 days' + interval '30 minutes'
),
-- Responses for Deep Learning Quiz attempt
(
    'g1f0f1d0-0000-4000-a000-000000000003'::uuid,
    'f1f0f1d0-0000-4000-a000-000000000003'::uuid,
    'b1f0f1d0-0000-4000-a000-000000000003'::uuid,
    'Sigmoid',
    true,
    NULL,
    90,
    CURRENT_TIMESTAMP - interval '7 days' + interval '20 minutes'
),
(
    'g1f0f1d0-0000-4000-a000-000000000004'::uuid,
    'f1f0f1d0-0000-4000-a000-000000000003'::uuid,
    'b1f0f1d0-0000-4000-a000-000000000004'::uuid,
    'The vanishing gradient problem is when gradients become too small in deep networks, making it hard for early layers to learn. Solutions include ReLU activation functions and skip connections.',
    true,
    0.92,
    240,
    CURRENT_TIMESTAMP - interval '7 days' + interval '40 minutes'
),
-- Responses for Data Science Quiz attempt
(
    'g1f0f1d0-0000-4000-a000-000000000005'::uuid,
    'f1f0f1d0-0000-4000-a000-000000000004'::uuid,
    'b1f0f1d0-0000-4000-a000-000000000005'::uuid,
    'To equalize feature importance',
    true,
    NULL,
    75,
    CURRENT_TIMESTAMP - interval '3 days' + interval '15 minutes'
),
(
    'g1f0f1d0-0000-4000-a000-000000000006'::uuid,
    'f1f0f1d0-0000-4000-a000-000000000004'::uuid,
    'b1f0f1d0-0000-4000-a000-000000000006'::uuid,
    'P-value measures the probability of getting results as extreme as observed, assuming the null hypothesis is true. Small p-values indicate strong evidence against the null hypothesis.',
    true,
    0.88,
    150,
    CURRENT_TIMESTAMP - interval '3 days' + interval '30 minutes'
);