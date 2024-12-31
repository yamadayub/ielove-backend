-- ユーザーの作成
INSERT INTO users (
    clerk_user_id,
    email,
    name,
    user_type,
    role,
    is_active,
    created_at
) VALUES (
    'user_2YCBNZdMXPd4fzGzrZe1xVTFzK1',
    'buyer@example.com',
    'テストバイヤー',
    'individual',
    'buyer',
    true,
    CURRENT_TIMESTAMP
) RETURNING id;

-- buyer_profilesの作成（上記のユーザーIDを使用）
INSERT INTO buyer_profiles (
    user_id,
    stripe_customer_id,
    shipping_postal_code,
    shipping_prefecture,
    shipping_city,
    shipping_address1,
    created_at
) VALUES (
    (SELECT id FROM users WHERE email = 'buyer@example.com'),
    'cus_test123',
    '100-0001',
    '東京都',
    '千代田区',
    '千代田1-1-1',
    CURRENT_TIMESTAMP
); 