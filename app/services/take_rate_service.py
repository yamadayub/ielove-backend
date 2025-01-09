from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException

from app.models import TakeRate


class TakeRateService:
    @staticmethod
    async def get_take_rate(db: Session, user_id: int, target_date: datetime = None) -> float:
        """
        指定されたユーザーと日付に対する手数料率を取得する

        Args:
            db: データベースセッション
            user_id: 対象ユーザーID
            target_date: 対象日付（指定がない場合は現在時刻）

        Returns:
            float: 手数料率（0-100の範囲）

        Raises:
            HTTPException: デフォルトの手数料率が設定されていない場合
        """
        if target_date is None:
            target_date = datetime.utcnow()

        # 1. ユーザー固有の手数料率を検索
        user_take_rate = db.query(TakeRate).filter(
            and_(
                TakeRate.user_id == user_id,
                TakeRate.date_from <= target_date,
                (TakeRate.date_to.is_(None) | (TakeRate.date_to >= target_date))
            )
        ).order_by(TakeRate.date_from.desc()).first()

        if user_take_rate:
            return float(user_take_rate.take_rate)

        # 2. デフォルトの手数料率を検索
        default_take_rate = db.query(TakeRate).filter(
            and_(
                TakeRate.is_default == True,
                TakeRate.date_from <= target_date,
                (TakeRate.date_to.is_(None) | (TakeRate.date_to >= target_date))
            )
        ).order_by(TakeRate.date_from.desc()).first()

        if default_take_rate:
            return float(default_take_rate.take_rate)

        # 3. デフォルト設定が見つからない場合はエラー
        raise HTTPException(
            status_code=500,
            detail={
                'error': 'System Error',
                'message': 'デフォルトの手数料率が設定されていません。'
            }
        )


take_rate_service = TakeRateService()
