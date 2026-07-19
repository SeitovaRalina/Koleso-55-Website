"""initial recommender schema

Revision ID: 0001_initial_recommender_schema
Revises:
Create Date: 2026-05-14
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


revision: str = "0001_initial_recommender_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "excursions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("excursion_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("location_type", sa.String(length=20), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("duration", sa.Integer(), nullable=False),
        sa.Column("average_rating", sa.Float(), nullable=True),
        sa.Column("review_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("popularity", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("text_for_embedding", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(768), nullable=True),
        sa.Column("ials_factors", Vector(128), nullable=True),
        sa.Column("has_embedding", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("last_updated", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("excursion_id", name="uq_excursions_excursion_id"),
    )
    op.create_index("idx_excursion_id", "excursions", ["excursion_id"])
    op.create_index("idx_category", "excursions", ["category"])
    op.create_index("idx_location_type", "excursions", ["location_type"])
    op.create_index("idx_popularity", "excursions", ["popularity"])

    op.create_table(
        "user_interactions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("session_id", sa.String(length=255), nullable=True),
        sa.Column("excursion_id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
    )
    op.create_index("idx_user_id", "user_interactions", ["user_id"])
    op.create_index("idx_session_id", "user_interactions", ["session_id"])
    op.create_index("idx_excursion_id_interactions", "user_interactions", ["excursion_id"])
    op.create_index("idx_timestamp", "user_interactions", ["timestamp"])

    op.create_table(
        "user_profiles",
        sa.Column("user_id", sa.Integer(), primary_key=True),
        sa.Column("content_vector", Vector(768), nullable=True),
        sa.Column("ials_factors", Vector(128), nullable=True),
        sa.Column("interaction_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_updated", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "recommendation_cache",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("excursion_ids", sa.JSON(), nullable=False),
        sa.Column("scores", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", name="uq_recommendation_cache_user_id"),
    )
    op.create_index("ix_recommendation_cache_user_id", "recommendation_cache", ["user_id"])

    op.create_table(
        "similar_cache",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("excursion_id", sa.Integer(), nullable=False),
        sa.Column("similar_ids", sa.JSON(), nullable=False),
        sa.Column("scores", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("excursion_id", name="uq_similar_cache_excursion_id"),
    )
    op.create_index("ix_similar_cache_excursion_id", "similar_cache", ["excursion_id"])

    op.create_table(
        "training_state",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("last_training_time", sa.DateTime(), nullable=True),
        sa.Column("total_interactions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("interactions_since_training", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("retrain_threshold", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("models_ready", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("idx_models_ready", "training_state", ["models_ready"])

    op.execute(
        "CREATE INDEX IF NOT EXISTS excursion_embedding_idx "
        "ON excursions USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100) "
        "WHERE embedding IS NOT NULL"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS excursion_ials_idx "
        "ON excursions USING ivfflat (ials_factors vector_cosine_ops) WITH (lists = 100) "
        "WHERE ials_factors IS NOT NULL"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS excursion_ials_idx")
    op.execute("DROP INDEX IF EXISTS excursion_embedding_idx")
    op.drop_table("training_state")
    op.drop_table("similar_cache")
    op.drop_table("recommendation_cache")
    op.drop_table("user_profiles")
    op.drop_table("user_interactions")
    op.drop_table("excursions")
