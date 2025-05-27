import aiohttp
from typing import List, Dict, Any
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

USERS_DATA_URL = "https://jsonplaceholder.typicode.com/users"
POSTS_DATA_URL = "https://jsonplaceholder.typicode.com/posts"


async def fetch_json(session: aiohttp.ClientSession, url: str) -> List[Dict[str, Any]]:
    """
    Basic function for making HTTP requests and returning JSON data.

    Args:
        session: aiohttp ClientSession instance
        url: URL to fetch data from

    Returns:
        List of dictionaries containing JSON data

    Raises:
        aiohttp.ClientError: If request fails
        ValueError: If response is not valid JSON
    """
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            data = await response.json()
            logger.info(f"Successfully fetched {len(data)} items from {url}")
            return data
    except aiohttp.ClientError as e:
        logger.error(f"HTTP error while fetching {url}: {e}")
        raise
    except ValueError as e:
        logger.error(f"JSON decode error for {url}: {e}")
        raise


async def fetch_users_data() -> List[Dict[str, Any]]:
    """
    Fetch users data from JSONPlaceholder API.

    Returns:
        List of user dictionaries with required fields
    """
    async with aiohttp.ClientSession() as session:
        users_raw = await fetch_json(session, USERS_DATA_URL)

        users_data = []
        for user in users_raw:
            user_data = {
                "id": user["id"],
                "name": user["name"],
                "username": user["username"],
                "email": user["email"],
            }
            users_data.append(user_data)

        logger.info(f"Processed {len(users_data)} users")
        return users_data


async def fetch_posts_data() -> List[Dict[str, Any]]:
    """
    Fetch posts data from JSONPlaceholder API.

    Returns:
        List of post dictionaries with required fields
    """
    async with aiohttp.ClientSession() as session:
        posts_raw = await fetch_json(session, POSTS_DATA_URL)

        posts_data = []
        for post in posts_raw:
            post_data = {
                "id": post["id"],
                "user_id": post["userId"],
                "title": post["title"],
                "body": post["body"],
            }
            posts_data.append(post_data)

        logger.info(f"Processed {len(posts_data)} posts")
        return posts_data


async def fetch_all_data() -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Fetch both users and posts data concurrently.

    Returns:
        Tuple of (users_data, posts_data)
    """
    users_data, posts_data = await asyncio.gather(
        fetch_users_data(), fetch_posts_data(), return_exceptions=False
    )

    return users_data, posts_data
