import asyncio
import logging
from typing import List, Dict, Any

from models import Session, User, Post, create_tables, close_db
from jsonplaceholder_requests import fetch_users_data, fetch_posts_data
from sqlalchemy.exc import IntegrityError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_users_in_db(users_data: List[Dict[str, Any]]) -> List[User]:
    """
    Create users in the database from the provided data.

    Args:
        users_data: List of user dictionaries

    Returns:
        List of created User objects
    """
    created_users = []

    async with Session() as session:
        try:
            for user_data in users_data:
                existing_user = await session.get(User, user_data["id"])
                if existing_user:
                    logger.info(
                        f"User {user_data['username']} already exists, skipping"
                    )
                    created_users.append(existing_user)
                    continue

                user = User(
                    id=user_data["id"],
                    name=user_data["name"],
                    username=user_data["username"],
                    email=user_data["email"],
                )
                session.add(user)
                created_users.append(user)
                logger.debug(f"Added user: {user.username}")

            await session.commit()
            logger.info(
                f"Successfully created {len([u for u in created_users if u.id])} users in database"
            )

        except IntegrityError as e:
            await session.rollback()
            logger.error(f"Integrity error while creating users: {e}")
            raise
        except Exception as e:
            await session.rollback()
            logger.error(f"Error creating users: {e}")
            raise

    return created_users


async def create_posts_in_db(posts_data: List[Dict[str, Any]]) -> List[Post]:
    """
    Create posts in the database from the provided data.

    Args:
        posts_data: List of post dictionaries

    Returns:
        List of created Post objects
    """
    created_posts = []

    async with Session() as session:
        try:
            for post_data in posts_data:
                existing_post = await session.get(Post, post_data["id"])
                if existing_post:
                    logger.info(f"Post {post_data['id']} already exists, skipping")
                    created_posts.append(existing_post)
                    continue

                post = Post(
                    id=post_data["id"],
                    user_id=post_data["user_id"],
                    title=post_data["title"],
                    body=post_data["body"],
                )
                session.add(post)
                created_posts.append(post)
                logger.debug(f"Added post: {post.title[:30]}...")

            await session.commit()
            logger.info(
                f"Successfully created {len([p for p in created_posts if p.id])} posts in database"
            )

        except IntegrityError as e:
            await session.rollback()
            logger.error(f"Integrity error while creating posts: {e}")
            raise
        except Exception as e:
            await session.rollback()
            logger.error(f"Error creating posts: {e}")
            raise

    return created_posts
