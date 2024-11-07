"""Initial commit

Revision ID: 07f88312f75a
Revises: 
Create Date: 2024-11-05 18:01:41.963479

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "07f88312f75a"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("user_api_key", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_api_key"),
    )
    op.create_table(
        "follow",
        sa.Column("following_user_id", sa.Integer(), nullable=False),
        sa.Column("followed_user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["followed_user_id"], ["user.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["following_user_id"], ["user.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("following_user_id", "followed_user_id"),
    )
    op.create_table(
        "tweet",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["author_id"], ["user.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "like",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("tweet_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["tweet_id"], ["tweet.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "tweet_id"),
    )
    op.create_table(
        "tweet_media",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("image", sa.String(), nullable=False),
        sa.Column("tweet_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["tweet_id"],
            ["tweet.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("tweet_media")
    op.drop_table("like")
    op.drop_table("tweet")
    op.drop_table("follow")
    op.drop_table("user")
    # ### end Alembic commands ###
