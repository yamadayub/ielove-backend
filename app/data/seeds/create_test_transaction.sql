-- まず、property_id=10に紐づくlisting_itemを取得
WITH listing AS (
    SELECT id 
    FROM listing_items 
    WHERE property_id = 10 
    LIMIT 1
)
-- 取引レコードの作成
INSERT INTO transactions (
    buyer_id,
    seller_id,
    listing_id,
    payment_intent_id,
    total_amount,
    platform_fee,
    seller_amount,
    transaction_status,
    payment_status,
    transfer_status,
    created_at,
    updated_at
) VALUES (
    (SELECT id FROM buyer_profiles WHERE stripe_customer_id = 'cus_test123'),  -- buyer_id
    (SELECT seller_id FROM listing_items WHERE id = (SELECT id FROM listing)), -- seller_id
    (SELECT id FROM listing),                                                  -- listing_id
    'pi_test_completed_123',                                                   -- payment_intent_id
    50000,                                                                     -- total_amount
    5000,                                                                      -- platform_fee
    45000,                                                                     -- seller_amount
    'COMPLETED',                                                              -- transaction_status
    'SUCCEEDED',                                                              -- payment_status
    'SUCCEEDED',                                                              -- transfer_status
    CURRENT_TIMESTAMP - INTERVAL '1 day',                                     -- created_at
    CURRENT_TIMESTAMP                                                         -- updated_at
); 