-- データのクリーンアップとシーケンスのリセット
BEGIN;

-- 外部キー制約を考慮した順序でデータを削除
TRUNCATE TABLE 
  sales,
  purchases,
  products_for_sale,
  seller_profiles,
  product_dimensions,
  product_specifications,
  images,
  products,
  product_categories,
  rooms,
  properties,
  companies,
  users
CASCADE;

-- シーケンスのリセット
ALTER SEQUENCE companies_id_seq RESTART WITH 1;
ALTER SEQUENCE properties_id_seq RESTART WITH 1;
ALTER SEQUENCE rooms_id_seq RESTART WITH 1;
ALTER SEQUENCE product_categories_id_seq RESTART WITH 1;
ALTER SEQUENCE products_id_seq RESTART WITH 1;
ALTER SEQUENCE product_specifications_id_seq RESTART WITH 1;
ALTER SEQUENCE product_dimensions_id_seq RESTART WITH 1;
ALTER SEQUENCE images_id_seq RESTART WITH 1;
ALTER SEQUENCE seller_profiles_id_seq RESTART WITH 1;
ALTER SEQUENCE products_for_sale_id_seq RESTART WITH 1;
ALTER SEQUENCE purchases_id_seq RESTART WITH 1;
ALTER SEQUENCE sales_id_seq RESTART WITH 1;

COMMIT;