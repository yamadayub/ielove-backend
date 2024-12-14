
-- Delete records from tables with foreign key dependencies first
DELETE FROM sales CASCADE;
DELETE FROM purchases CASCADE;
DELETE FROM products_for_sale CASCADE;
DELETE FROM product_specifications CASCADE;
DELETE FROM product_dimensions CASCADE;
DELETE FROM images CASCADE;
DELETE FROM products CASCADE;
DELETE FROM rooms CASCADE;
DELETE FROM properties CASCADE;

-- Reset sequences
ALTER SEQUENCE sales_id_seq RESTART WITH 1;
ALTER SEQUENCE purchases_id_seq RESTART WITH 1;
ALTER SEQUENCE products_for_sale_id_seq RESTART WITH 1;
ALTER SEQUENCE product_specifications_id_seq RESTART WITH 1;
ALTER SEQUENCE product_dimensions_id_seq RESTART WITH 1;
ALTER SEQUENCE images_id_seq RESTART WITH 1;
ALTER SEQUENCE products_id_seq RESTART WITH 1;
ALTER SEQUENCE rooms_id_seq RESTART WITH 1;
ALTER SEQUENCE properties_id_seq RESTART WITH 1;
