import csv
import os
from sqlalchemy.orm import Session
from app.models import Product, ProductSpecification, ProductDimension
from app.database import SessionLocal

# スクリプトのディレクトリパスを取得
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def import_products(csv_filename: str = "products.csv"):
    # CSVファイルのフルパスを構築
    csv_path = os.path.join(SCRIPT_DIR, csv_filename)

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSVファイルが見つかりません: {csv_path}")

    db = SessionLocal()
    current_product = None
    current_product_id = None

    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                if row['type'] == 'product':
                    # 新しい製品を作成
                    product = Product(
                        room_id=int(row['room_id']),
                        name=row['name'],
                        product_code=row['product_code'],
                        manufacturer_name=row['manufacturer_name'],
                        product_category_id=int(
                            row['product_category_id']) if row['product_category_id'] else None,
                        description=row['description'] if row['description'] else None,
                        catalog_url=row['catalog_url'] if row['catalog_url'] else None
                    )
                    db.add(product)
                    db.flush()  # IDを取得するためにflush
                    current_product_id = product.id
                    current_product = product
                    print(
                        f"製品を作成しました: {product.name} (ID: {product.id}, Room ID: {product.room_id})")

                elif row['type'] == 'spec' and current_product_id:
                    # 仕様を追加
                    spec = ProductSpecification(
                        product_id=current_product_id,
                        spec_type=row['spec_type'],
                        spec_value=row['spec_value'],
                        model_number=row['model_number'] if row['model_number'] else None
                    )
                    db.add(spec)
                    print(f"仕様を追加しました: {spec.spec_type} - {spec.spec_value}")

                elif row['type'] == 'dimension' and current_product_id:
                    # 寸法を追加
                    dimension = ProductDimension(
                        product_id=current_product_id,
                        dimension_type=row['dimension_type'],
                        value=float(row['dimension_value']),
                        unit=row['dimension_unit']
                    )
                    db.add(dimension)
                    print(
                        f"寸法を追加しました: {dimension.dimension_type} - {dimension.value}{dimension.unit}")

            db.commit()
            print(f"\n製品のインポートが完了しました")

    except Exception as e:
        db.rollback()
        print(f"エラーが発生しました: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='製品データをCSVからインポートします')
    parser.add_argument('--csv-file', type=str, default="products.csv",
                        help='CSVファイルの名前（デフォルト: products.csv）')

    args = parser.parse_args()
    import_products(args.csv_file)
