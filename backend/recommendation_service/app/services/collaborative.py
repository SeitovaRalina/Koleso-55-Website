import logging
import joblib
from pathlib import Path
from typing import List, Dict, Union

import numpy as np
import scipy.sparse as sp
import implicit

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models.excursions import Excursion
from app.models.profile import UserProfile
from app.models.interaction import UserInteraction
from app.models.training import TrainingState
from app.services.cache import CacheService

logger = logging.getLogger(__name__)


class CollaborativeService:
    """Collaborative filtering recommendation service with iALS"""

    def __init__(self, db: Union[AsyncSession, Session], settings: Settings, cache_service: CacheService):
        self.db = db
        self.settings = settings
        self.cache_service = cache_service

        self.model = None
        self.user_to_index: Dict[int, int] = {}
        self.item_to_index: Dict[int, int] = {}
        self.index_to_user: Dict[int, int] = {}
        self.index_to_item: Dict[int, int] = {}

        self.model_path = Path(settings.MODEL_PATH) / "ials_model.pkl"
        self.model_path.parent.mkdir(parents=True, exist_ok=True)

        self.is_async = isinstance(db, AsyncSession)

    async def _execute(self, stmt):
        """Unified execute method for async and sync sessions"""
        if self.is_async:
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)
        return result

    async def _commit(self):
        """Unified commit method for async and sync sessions"""
        if self.is_async:
            await self.db.commit()
        else:
            self.db.commit()

    async def _rollback(self):
        """Unified rollback method for async and sync sessions"""
        if self.is_async:
            await self.db.rollback()
        else:
            self.db.rollback()

    async def train(self) -> bool:
        """
        Train iALS collaborative filtering model using implicit library
        """
        try:
            logger.info("Starting iALS collaborative filtering training...")

            # 1. Get all UserInteraction records
            result = await self._execute(
                select(UserInteraction.user_id, UserInteraction.excursion_id, UserInteraction.weight)
                    .where(UserInteraction.user_id.is_not(None))
            )
            interactions = result.all()

            if len(interactions) < self.settings.COLD_START_MIN_INTERACTIONS:
                logger.warning(f"Insufficient interactions for training: {len(interactions)}")
                return False

            # 2. Build user_index and item_index mappings
            users = sorted({row.user_id for row in interactions})
            items = sorted({row.excursion_id for row in interactions})

            self.user_to_index = {user: idx for idx, user in enumerate(users)}
            self.item_to_index = {item: idx for idx, item in enumerate(items)}
            self.index_to_user = {idx: user for user, idx in self.user_to_index.items()}
            self.index_to_item = {idx: item for item, idx in self.item_to_index.items()}

            # 3. Build sparse confidence matrix for implicit library
            rows, cols, data = [], [], []
            for user_id, item_id, weight in interactions:
                u_idx = self.user_to_index[user_id]
                i_idx = self.item_to_index[item_id]

                # Use weight as confidence (implicit library handles alpha internally)
                confidence = 1 + weight * self.settings.IALS_ALPHA
                rows.append(u_idx)
                cols.append(i_idx)
                data.append(confidence)

            C = sp.csr_matrix((data, (rows, cols)), shape=(len(users), len(items)))

            # 4. Train using implicit library
            logger.info(f"Training iALS with {len(users)} users, {len(items)} items, {len(interactions)} interactions")

            self.model = implicit.als.AlternatingLeastSquares(
                factors=self.settings.IALS_FACTORS,
                regularization=self.settings.IALS_REGULARIZATION,
                iterations=self.settings.IALS_ITERATIONS,
                alpha=self.settings.IALS_ALPHA,
                random_state=42
            )

            self.model.fit(C, show_progress=True)

            joblib.dump(self.model, self.model_path)
            logger.info(f"Saved iALS model to {self.model_path}")

            # 5. Save factors to database
            await self._save_factors_to_db(users, items)

            # 6. Update TrainingState
            await self._update_training_state(len(interactions))

            logger.info("iALS collaborative filtering training completed successfully")
            return True

        except Exception as e:
            logger.error(f"Error in collaborative training: {e}")
            await self._rollback()
            return False

    async def _save_factors_to_db(self, users: List[int], items: List[int]):
        """Save trained factors to database"""
        if self.model is None:
            logger.warning("No model to save factors from")
            return

        user_factors = self.model.user_factors
        item_factors = self.model.item_factors

        # --- Item factors (Excursion) ---
        for i_idx, excursion_id in enumerate(items):
            factors = item_factors[i_idx].tolist()
            await self._execute(
                update(Excursion)
                .where(Excursion.excursion_id == excursion_id)
                .values(ials_factors=factors)
            )

        # --- User factors (UserProfile) ---
        for u_idx, user_id in enumerate(users):
            factors = user_factors[u_idx].tolist()

            user_profile = await self.db.get(UserProfile, user_id) if self.is_async else self.db.get(UserProfile, user_id)
            if user_profile:
                user_profile.ials_factors = factors
            else:
                user_profile = UserProfile(
                    user_id=user_id,
                    ials_factors=factors,
                    interaction_count=0,
                    last_updated=func.now()
                )
                self.db.add(user_profile)

        await self._commit()
        logger.info("Saved collaborative factors to database")

    async def _update_training_state(self, total_interactions: int):
        """Update training state after successful training"""
        training_state = await self.db.get(TrainingState, 1) if self.is_async else self.db.get(TrainingState, 1)

        if not training_state:
            training_state = TrainingState(id=1)
            self.db.add(training_state)

        training_state.last_training_time = func.now()
        training_state.total_interactions = total_interactions
        training_state.interactions_since_training = 0
        training_state.models_ready = True

        await self._commit()
        logger.info("Updated training state")

    async def predict(self, user_id: int, item_id: int) -> float:
        """
        Predict user's preference for an item using collaborative filtering
        """
        if self.model is None:
            logger.warning("Collaborative model not trained")
            return 0.0

        if user_id not in self.user_to_index or item_id not in self.item_to_index:
            logger.warning(f"User {user_id} or item {item_id} not in training data")
            return 0.0

        try:
            u_idx = self.user_to_index[user_id]
            i_idx = self.item_to_index[item_id]

            # Use implicit library's predict method
            prediction = self.model.user_factors[u_idx] @ self.model.item_factors[i_idx]

            # Normalize to [0, 1] range using sigmoid
            normalized_score = 1 / (1 + np.exp(-prediction))

            return float(normalized_score)
        except Exception as e:
            logger.error(f"Error predicting user {user_id}, item {item_id}: {e}")
            return 0.0
