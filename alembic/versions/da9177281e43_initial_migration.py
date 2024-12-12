
"""initial migration

Revision ID: da9177281e43
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from app.models import PropertyType, ImageType, CompanyType, UserType, UserRole, SaleType, SaleStatus, ConsultationType

# revision identifiers, used by Alembic.
revision = 'da9177281e43'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Drop existing enums if exist
    op.execute('DROP TYPE IF EXISTS propertytype')
    op.execute('DROP TYPE IF EXISTS imagetype')
    op.execute('DROP TYPE IF EXISTS companytype')
    op.execute('DROP TYPE IF EXISTS usertype')
    op.execute('DROP TYPE IF EXISTS userrole')
    op.execute('DROP TYPE IF EXISTS saletype')
    op.execute('DROP TYPE IF EXISTS salestatus')
    op.execute('DROP TYPE IF EXISTS consultationtype')

    # Create companies table
    op.create_table('companies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('company_type', sa.Enum(CompanyType, name='companytype'), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('website', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create users table
    op.create_table('users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('user_type', sa.Enum(UserType, name='usertype'), nullable=False),
        sa.Column('role', sa.Enum(UserRole, name='userrole'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('last_sign_in', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # Create seller_profiles table
    op.create_table('seller_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('company_name', sa.String(), nullable=True),
        sa.Column('representative_name', sa.String(), nullable=True),
        sa.Column('postal_code', sa.String(), nullable=True),
        sa.Column('address', sa.String(), nullable=True),
        sa.Column('phone_number', sa.String(), nullable=True),
        sa.Column('business_registration_number', sa.String(), nullable=True),
        sa.Column('tax_registration_number', sa.String(), nullable=True),
        sa.Column('stripe_account_id', sa.String(), nullable=True),
        sa.Column('stripe_account_status', sa.String(), nullable=True),
        sa.Column('stripe_account_type', sa.String(), nullable=True),
        sa.Column('stripe_onboarding_completed', sa.Boolean(), nullable=True),
        sa.Column('stripe_charges_enabled', sa.Boolean(), nullable=True),
        sa.Column('stripe_payouts_enabled', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('stripe_account_id')
    )

    # Create properties table
    op.create_table('properties',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('property_type', sa.Enum(PropertyType, name='propertytype'), nullable=False),
        sa.Column('prefecture', sa.String(), nullable=False),
        sa.Column('layout', sa.String(), nullable=True),
        sa.Column('construction_year', sa.Integer(), nullable=True),
        sa.Column('construction_month', sa.Integer(), nullable=True),
        sa.Column('site_area', sa.Float(), nullable=True),
        sa.Column('building_area', sa.Float(), nullable=True),
        sa.Column('floor_count', sa.Integer(), nullable=True),
        sa.Column('structure', sa.String(), nullable=True),
        sa.Column('design_company_id', sa.Integer(), nullable=True),
        sa.Column('construction_company_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['construction_company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['design_company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create product_categories table
    op.create_table('product_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create rooms table
    op.create_table('rooms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('property_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['property_id'], ['properties.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create products table
    op.create_table('products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('property_id', sa.Integer(), nullable=False),
        sa.Column('room_id', sa.Integer(), nullable=False),
        sa.Column('product_category_id', sa.Integer(), nullable=False),
        sa.Column('manufacturer_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('model_number', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('catalog_url', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['manufacturer_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['product_category_id'], ['product_categories.id'], ),
        sa.ForeignKeyConstraint(['property_id'], ['properties.id'], ),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create images table
    op.create_table('images',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('image_type', sa.Enum(ImageType, name='imagetype'), nullable=False),
        sa.Column('property_id', sa.Integer(), nullable=True),
        sa.Column('room_id', sa.Integer(), nullable=True),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.ForeignKeyConstraint(['property_id'], ['properties.id'], ),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create product_specifications table
    op.create_table('product_specifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('spec_type', sa.String(), nullable=False),
        sa.Column('spec_value', sa.String(), nullable=False),
        sa.Column('manufacturer_id', sa.Integer(), nullable=True),
        sa.Column('model_number', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['manufacturer_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create product_dimensions table
    op.create_table('product_dimensions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('dimension_type', sa.String(), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create products_for_sale table
    op.create_table('products_for_sale',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('seller_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price', sa.Integer(), nullable=False),
        sa.Column('sale_type', sa.Enum(SaleType, name='saletype'), nullable=False),
        sa.Column('consultation_type', sa.Enum(ConsultationType, name='consultationtype'), nullable=True),
        sa.Column('status', sa.Enum(SaleStatus, name='salestatus'), nullable=True),
        sa.Column('property_id', sa.Integer(), nullable=True),
        sa.Column('room_id', sa.Integer(), nullable=True),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('is_negotiable', sa.Boolean(), nullable=True),
        sa.Column('consultation_minutes', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.ForeignKeyConstraint(['property_id'], ['properties.id'], ),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ),
        sa.ForeignKeyConstraint(['seller_id'], ['seller_profiles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create purchases table
    op.create_table('purchases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('buyer_id', sa.String(), nullable=False),
        sa.Column('product_for_sale_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('stripe_payment_intent_id', sa.String(), nullable=True),
        sa.Column('stripe_payment_status', sa.String(), nullable=True),
        sa.Column('stripe_transfer_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['buyer_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['product_for_sale_id'], ['products_for_sale.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('stripe_payment_intent_id'),
        sa.UniqueConstraint('stripe_transfer_id')
    )

    # Create sales table
    op.create_table('sales',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('seller_id', sa.Integer(), nullable=False),
        sa.Column('product_for_sale_id', sa.Integer(), nullable=False),
        sa.Column('purchase_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('platform_fee', sa.Integer(), nullable=False),
        sa.Column('seller_amount', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('stripe_transfer_id', sa.String(), nullable=True),
        sa.Column('stripe_transfer_status', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['product_for_sale_id'], ['products_for_sale.id'], ),
        sa.ForeignKeyConstraint(['purchase_id'], ['purchases.id'], ),
        sa.ForeignKeyConstraint(['seller_id'], ['seller_profiles.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('purchase_id'),
        sa.UniqueConstraint('stripe_transfer_id')
    )

def downgrade():
    # テーブルの削除順序を定義
    tables = [
        'sales', 'purchases', 'products_for_sale', 'product_specifications',
        'product_dimensions', 'images', 'products', 'rooms', 'properties',
        'seller_profiles', 'users', 'companies', 'product_categories'
    ]
    
    # enumの削除順序を定義
    enums = [
        'propertytype', 'imagetype', 'companytype', 'usertype',
        'userrole', 'saletype', 'salestatus', 'consultationtype'
    ]

    # 各テーブルを個別のトランザクションで削除
    for table in tables:
        try:
            with op.get_context().begin_transaction():
                op.drop_table(table)
        except Exception as e:
            print(f"Warning: Could not drop table {table}: {str(e)}")
            
    # 各enumを個別のトランザクションで削除
    for enum in enums:
        try:
            with op.get_context().begin_transaction():
                op.execute(f'DROP TYPE IF EXISTS {enum}')
        except Exception as e:
            print(f"Warning: Could not drop enum {enum}: {str(e)}")
    op.execute('DROP TYPE IF EXISTS imagetype')
    op.execute('DROP TYPE IF EXISTS companytype')
    op.execute('DROP TYPE IF EXISTS usertype')
    op.execute('DROP TYPE IF EXISTS userrole')
    op.execute('DROP TYPE IF EXISTS saletype')
    op.execute('DROP TYPE IF EXISTS salestatus')
    op.execute('DROP TYPE IF EXISTS consultationtype')
