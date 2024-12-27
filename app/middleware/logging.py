import time
import json
from fastapi import Request
import logging
from typing import Callable
import copy

# 他のロガーを無効化
logging.getLogger('sqlalchemy').setLevel(logging.ERROR)
logging.getLogger('uvicorn').setLevel(logging.WARNING)

# APIロガーの設定
api_logger = logging.getLogger("api")
api_logger.setLevel(logging.INFO)

# ハンドラーの設定
handler = logging.StreamHandler()
formatter = logging.Formatter('%(message)s')  # メッセージのみを表示
handler.setFormatter(formatter)

# 既存のハンドラーをクリアして新しいハンドラーを追加
api_logger.handlers.clear()
api_logger.addHandler(handler)
api_logger.propagate = False


async def log_request_middleware(request: Request, call_next):
    """リクエストとレスポンスの情報をログに記録するミドルウェア"""
    # リクエスト開始時刻
    start_time = time.time()

    # リクエスト情報をログに記録
    api_logger.info(
        f"\n"
        f"--- Incoming Request ---\n"
        f"Method: {request.method}\n"
        f"Path: {request.url.path}\n"
        f"Headers: {dict(request.headers)}\n"
        f"Query Params: {dict(request.query_params)}\n"
    )

    # リクエストボディの読み取り（可能な場合）
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.json()
            api_logger.info(f"Body: {json.dumps(body, ensure_ascii=False)}\n")
        except Exception:
            api_logger.info("Body: Could not parse request body\n")

    # レスポンスの処理
    response = await call_next(request)

    # 処理時間の計算
    process_time = time.time() - start_time

    # レスポンス情報をログに記録
    api_logger.info(
        f"\n"
        f"--- Outgoing Response ---\n"
        f"Status: {response.status_code}\n"
        f"Process Time: {process_time:.4f} sec\n"
    )

    # エラーの場合は詳細を表示
    if response.status_code >= 400:
        try:
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
            error_detail = response_body.decode()
            api_logger.error(f"Error Detail: {error_detail}\n")

            # レスポンスボディを再設定
            async def body_iterator():
                yield response_body
            response.body_iterator = body_iterator()
        except Exception as e:
            api_logger.error(f"Error logging failed: {str(e)}\n")

    return response
