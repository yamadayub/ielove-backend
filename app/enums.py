from enum import Enum
from typing import Dict, List


class BaseEnum(str, Enum):
    @classmethod
    def get_labels(cls) -> List[Dict[str, str]]:
        return [{"value": e.value, "label": cls.labels()[e.value]} for e in cls]

    @classmethod
    def labels(cls) -> Dict[str, str]:
        raise NotImplementedError


class CompanyType(BaseEnum):
    MANUFACTURER = "MANUFACTURER"
    DESIGN = "DESIGN"
    CONSTRUCTION = "CONSTRUCTION"

    @classmethod
    def labels(cls) -> Dict[str, str]:
        return {
            "MANUFACTURER": "製造会社",
            "DESIGN": "設計会社",
            "CONSTRUCTION": "建設会社"
        }


class PropertyType(BaseEnum):
    HOUSE = "HOUSE"
    APARTMENT = "APARTMENT"
    OTHER = "OTHER"

    @classmethod
    def labels(cls) -> Dict[str, str]:
        return {
            "HOUSE": "戸建",
            "APARTMENT": "マンション",
            "OTHER": "その他"
        }


class StructureType(BaseEnum):
    WOODEN = "WOODEN"
    STEEL_FRAME = "STEEL_FRAME"
    RC = "RC"
    SRC = "SRC"
    LIGHT_STEEL = "LIGHT_STEEL"

    @classmethod
    def labels(cls) -> Dict[str, str]:
        return {
            "WOODEN": "木造",
            "STEEL_FRAME": "鉄骨造",
            "RC": "RC造",
            "SRC": "SRC造",
            "LIGHT_STEEL": "軽量鉄骨造"
        }


class DimensionType(BaseEnum):
    WIDTH = "WIDTH"
    HEIGHT = "HEIGHT"
    DEPTH = "DEPTH"
    DIAMETER = "DIAMETER"
    LENGTH = "LENGTH"

    @classmethod
    def labels(cls) -> Dict[str, str]:
        return {
            "WIDTH": "幅",
            "HEIGHT": "高さ",
            "DEPTH": "奥行き",
            "DIAMETER": "直径",
            "LENGTH": "長さ"
        }


class ImageType(BaseEnum):
    MAIN = "MAIN"
    SUB = "SUB"
    PAID = "PAID"

    @classmethod
    def labels(cls) -> Dict[str, str]:
        return {
            "MAIN": "メイン画像",
            "SUB": "サブ画像",
            "PAID": "有料画像"
        }


class ListingType(BaseEnum):
    PROPERTY_SPECS = "PROPERTY_SPECS"
    ROOM_SPECS = "ROOM_SPECS"
    PRODUCT_SPECS = "PRODUCT_SPECS"
    CONSULTATION = "CONSULTATION"
    PROPERTY_VIEWING = "PROPERTY_VIEWING"

    @classmethod
    def labels(cls) -> Dict[str, str]:
        return {
            "PROPERTY_SPECS": "物件仕様",
            "ROOM_SPECS": "部屋仕様",
            "PRODUCT_SPECS": "製品仕様",
            "CONSULTATION": "相談",
            "PROPERTY_VIEWING": "内覧"
        }


class ListingStatus(BaseEnum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    RESERVED = "RESERVED"
    SOLD = "SOLD"
    CANCELLED = "CANCELLED"

    @classmethod
    def labels(cls) -> Dict[str, str]:
        return {
            "DRAFT": "下書き",
            "PUBLISHED": "公開中",
            "RESERVED": "予約済み",
            "SOLD": "売約済み",
            "CANCELLED": "キャンセル"
        }


class Visibility(BaseEnum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"

    @classmethod
    def labels(cls) -> Dict[str, str]:
        return {
            "PUBLIC": "公開",
            "PRIVATE": "非公開"
        }


class TransactionStatus(BaseEnum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"

    @classmethod
    def labels(cls) -> Dict[str, str]:
        return {
            "PENDING": "取引開始",
            "CONFIRMED": "取引確定",
            "COMPLETED": "取引完了",
            "CANCELLED": "取引キャンセル",
            "REFUNDED": "返金済み"
        }


class PaymentStatus(BaseEnum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"

    @classmethod
    def labels(cls) -> Dict[str, str]:
        return {
            "PENDING": "支払い待ち",
            "PROCESSING": "処理中",
            "SUCCEEDED": "支払い完了",
            "FAILED": "支払い失敗",
            "REFUNDED": "返金済み"
        }


class TransferStatus(BaseEnum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"

    @classmethod
    def labels(cls) -> Dict[str, str]:
        return {
            "PENDING": "送金待ち",
            "PROCESSING": "処理中",
            "SUCCEEDED": "送金完了",
            "FAILED": "送金失敗"
        }


class ChangeType(BaseEnum):
    SYSTEM = "SYSTEM"
    USER = "USER"
    WEBHOOK = "WEBHOOK"

    @classmethod
    def labels(cls) -> Dict[str, str]:
        return {
            "SYSTEM": "システム変更",
            "USER": "ユーザー変更",
            "WEBHOOK": "Webhook変更"
        }


class ErrorType(BaseEnum):
    STRIPE_PAYMENT_ERROR = "STRIPE_PAYMENT_ERROR"
    STRIPE_TRANSFER_ERROR = "STRIPE_TRANSFER_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    SYSTEM_ERROR = "SYSTEM_ERROR"

    @classmethod
    def labels(cls) -> Dict[str, str]:
        return {
            "STRIPE_PAYMENT_ERROR": "Stripe決済エラー",
            "STRIPE_TRANSFER_ERROR": "Stripe送金エラー",
            "VALIDATION_ERROR": "バリデーションエラー",
            "SYSTEM_ERROR": "システムエラー"
        }
