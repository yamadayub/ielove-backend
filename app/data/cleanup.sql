
-- Delete all records from related tables with cascade
DELETE FROM properties;

-- Reset sequences
ALTER SEQUENCE properties_id_seq RESTART WITH 1;
ALTER SEQUENCE rooms_id_seq RESTART WITH 1;
ALTER SEQUENCE products_id_seq RESTART WITH 1;
ALTER SEQUENCE product_specifications_id_seq RESTART WITH 1;
ALTER SEQUENCE product_dimensions_id_seq RESTART WITH 1;
ALTER SEQUENCE images_id_seq RESTART WITH 1;
