-- トランザクション開始
BEGIN;

-- 1. ユーザーの登録（テスト用）
INSERT INTO users (clerk_user_id, email, name, user_type, role) VALUES
('user_123', 'test@example.com', 'テストユーザー', 'individual', 'seller');

-- 2. 製造会社の登録
INSERT INTO companies (name, company_type, description) VALUES
('ナチュラルウッド', 'manufacturer', '床材メーカー'),
('エコウォール', 'manufacturer', '壁材メーカー'),
('スカイテック', 'manufacturer', '天井材メーカー'),
('ライトマスター', 'manufacturer', '照明機器メーカー'),
('セーフティドア', 'manufacturer', 'ドアメーカー');

-- 3. 物件の登録
INSERT INTO properties (
  user_id,
  name,
  description,
  property_type,
  prefecture,
  layout,
  construction_year,
  construction_month,
  site_area,
  building_area,
  floor_count,
  structure
) VALUES
(1, 'グランドメゾン青山', '緑豊かな環境と都会の利便性を兼ね備えた邸宅', 'house', '東京都', '3LDK', 2020, 4, 120.5, 95.2, 3, 'RC造'),
(1, 'パークサイドレジデンス', '都心へのアクセス良好な低層マンション', 'apartment', '東京都', '2LDK', 2021, 8, 85.3, 70.2, 2, 'RC造');

-- 4. 物件の画像を登録
INSERT INTO images (url, image_type, property_id, description) VALUES
('https://images.unsplash.com/photo-1580587771525-78b9dba3b914', 'main', 1, 'メイン外観写真'),
('https://images.unsplash.com/photo-1600607687939-ce8a6c25118c', 'sub', 1, 'エントランス'),
('https://images.unsplash.com/photo-1600607687644-c7171b42498b', 'sub', 1, '外観別角度'),
('https://images.unsplash.com/photo-1512917774080-9991f1c4c750', 'main', 2, 'メイン外観写真'),
('https://images.unsplash.com/photo-1600566752355-35792bedcfea', 'sub', 2, 'エントランス');

-- 5. 部屋の登録（物件1用）
INSERT INTO rooms (property_id, name, description) VALUES
(1, 'リビングダイニング', 'リビングダイニングの説明文がここに入ります。'),
(1, 'キッチン', 'キッチンの説明文がここに入ります。'),
(1, '主寝室', '主寝室の説明文がここに入ります。'),
(1, '玄関', '玄関の説明文がここに入ります。'),
(1, '廊下', '廊下の説明文がここに入ります。'),
(1, '洗面所', '洗面所の説明文がここに入ります。'),
(1, '風呂', '風呂の説明文がここに入ります。'),
(1, 'トイレ', 'トイレの説明文がここに入ります。');

-- 6. 部屋の画像を登録
INSERT INTO images (url, image_type, room_id, description) VALUES
('https://images.unsplash.com/photo-1600210492486-724fe5c67fb0', 'main', 1, 'リビングダイニング'),
('https://images.unsplash.com/photo-1600210492486-724fe5c67fb0', 'main', 2, 'キッチン'),
('https://images.unsplash.com/photo-1600210492486-724fe5c67fb0', 'main', 3, '主寝室'),
('https://images.unsplash.com/photo-1600210492486-724fe5c67fb0', 'main', 4, '玄関'),
('https://images.unsplash.com/photo-1600210492486-724fe5c67fb0', 'main', 5, '廊下'),
('https://images.unsplash.com/photo-1600210492486-724fe5c67fb0', 'main', 6, '洗面所'),
('https://images.unsplash.com/photo-1600210492486-724fe5c67fb0', 'main', 7, '風呂'),
('https://images.unsplash.com/photo-1600210492486-724fe5c67fb0', 'main', 8, 'トイレ');

-- 7. 製品カテゴリーを登録
INSERT INTO product_categories (name, description) VALUES
('床材', 'フローリングなどの床材'),
('壁材', '壁紙、クロスなどの壁材'),
('天井材', '天井材、天井パネル'),
('照明', '照明器具、ライト'),
('ドア', 'ドア、引き戸');

-- 8. 製品を登録（リビングダイニング用）
INSERT INTO products (
  room_id,
  product_category_id,
  manufacturer_id,
  name,
  product_code,
  description,
  catalog_url
) VALUES
(1, 1, 1, '無垢材フローリング', 'NW-OF-123', '25年保証付き', 'https://example.com/catalog/flooring'),
(1, 2, 2, '珪藻土クロス', 'EW-DC-456', '調湿機能付き', 'https://example.com/catalog/wallpaper'),
(1, 3, 3, '高機能天井材', 'ST-C-789', '防音・断熱仕様', 'https://example.com/catalog/ceiling'),
(1, 4, 4, 'LEDシーリングライト', 'LM-567', 'リモコン調光・調色機能付き', 'https://example.com/catalog/lighting'),
(1, 5, 5, '防音ドア', 'SD-234', '遮音性能T-2等級', 'https://example.com/catalog/door');

-- 9. 製品仕様を登録
INSERT INTO product_specifications (
  product_id,
  spec_type,
  spec_value,
  manufacturer_id,
  model_number
) VALUES
(1, '耐久性', '25年保証', 1, 'NW-OF-123'),
(1, '施工方法', '接着剤併用フローティング工法', 1, 'NW-OF-123'),
(2, '防火性能', '不燃', 2, 'EW-DC-456'),
(2, '調湿機能', 'あり', 2, 'EW-DC-456'),
(3, '防音性能', '遮音等級D-65', 3, 'ST-C-789'),
(3, '断熱性能', 'H-4', 3, 'ST-C-789'),
(4, '調光範囲', '1-100%', 4, 'LM-567'),
(4, '専用リモコン', '付属', 4, 'LM-567'),
(5, '防音性能', '遮音等級T-2', 5, 'SD-234'),
(5, '耐火性能', '30分耐火', 5, 'SD-234');

-- 10. 製品画像を登録
INSERT INTO images (url, image_type, product_id, description) VALUES
('https://images.unsplash.com/photo-1516455590571-18256e5bb9ff', 'main', 1, '床材メイン画像'),
('https://images.unsplash.com/photo-1615873968403-89e068629265', 'main', 2, '壁材メイン画像'),
('https://images.unsplash.com/photo-1595428774223-ef52624120d2', 'main', 3, '天井材メイン画像'),
('https://images.unsplash.com/photo-1524484485831-a92ffc0de03f', 'main', 4, '照明メイン画像'),
('https://images.unsplash.com/photo-1534172553917-0ce2ef189cda', 'main', 5, 'ドアメイン画像');

-- トランザクション終了
COMMIT;