import unittest

from fastapi import HTTPException

from app.routers.recommendations import get_recommendations


class RecommendationRouterTests(unittest.IsolatedAsyncioTestCase):
    async def test_missing_identity_returns_bad_request(self):
        with self.assertRaises(HTTPException) as raised:
            await get_recommendations(
                user_id=None,
                session_id=None,
                limit=20,
                db=None,
                hybrid_service=None,
            )

        self.assertEqual(raised.exception.status_code, 400)
        self.assertEqual(
            raised.exception.detail,
            "Either user_id or session_id must be provided",
        )
