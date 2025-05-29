import logging
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.sql.expression import func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from models import Session, User, Post, create_tables
from jsonplaceholder_requests import fetch_all_data
from main import create_users_in_db, create_posts_in_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserCreate(BaseModel):
    name: str
    username: str
    email: str


class PostCreate(BaseModel):
    user_id: int
    title: str
    body: str


class UserResponse(BaseModel):
    id: int
    name: str
    username: str
    email: str

    class Config:
        from_attributes = True


class PostResponse(BaseModel):
    id: int
    user_id: int
    title: str
    body: str

    class Config:
        from_attributes = True


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting up...")
    await create_tables()
    logger.info("Database initialized")

    yield

    logger.info("Shutting down...")


app = FastAPI(
    title="Users & Posts API",
    description="A FastAPI application for managing users and posts with JSONPlaceholder API integration",
    version="0.2.0",
    lifespan=lifespan,
)

templates = Jinja2Templates(directory="templates")


async def get_db_session():
    """Dependency to get database session"""
    async with Session() as session:
        yield session


# Web Routes
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Home page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/users", response_class=HTMLResponse)
async def users_page(request: Request, db: AsyncSession = Depends(get_db_session)):
    """Users list page"""
    result = await db.execute(select(User).order_by(User.id))
    users = result.scalars().all()
    return templates.TemplateResponse(
        "users.html", {"request": request, "users": users}
    )


@app.get("/posts", response_class=HTMLResponse)
async def posts_page(request: Request, db: AsyncSession = Depends(get_db_session)):
    """Posts list page"""
    result = await db.execute(select(Post).order_by(Post.id.desc()))
    posts = result.scalars().all()
    return templates.TemplateResponse(
        "posts.html", {"request": request, "posts": posts}
    )


# API Routes
@app.post("/api/load-data")
async def load_data_from_api():
    """Load data from JSONPlaceholder API"""
    try:
        logger.info("Starting data load from API...")
        users_data, posts_data = await fetch_all_data()

        await create_users_in_db(users_data)
        await create_posts_in_db(posts_data)

        logger.info("Data loaded successfully")
        return {
            "message": "Data loaded successfully",
            "users": len(users_data),
            "posts": len(posts_data),
        }
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        raise HTTPException(status_code=500, detail="Error loading data from API")


@app.get("/api/users", response_model=List[UserResponse])
async def get_users_api(db: AsyncSession = Depends(get_db_session)):
    """Get all users as JSON"""
    result = await db.execute(select(User).order_by(User.id))
    users = result.scalars().all()
    return users


@app.post("/api/users", response_model=UserResponse)
async def create_user_api(
    user_data: UserCreate, db: AsyncSession = Depends(get_db_session)
):
    """Create new user via API"""
    try:
        result = await db.execute(select(func.max(User.id)))
        max_id = result.scalar()
        next_id = (max_id or 0) + 1

        user = User(
            id=next_id,
            name=user_data.name,
            username=user_data.username,
            email=user_data.email,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Error creating user")


@app.get("/api/posts", response_model=List[PostResponse])
async def get_posts_api(db: AsyncSession = Depends(get_db_session)):
    """Get all posts as JSON"""
    result = await db.execute(select(Post).order_by(Post.id.desc()))
    posts = result.scalars().all()
    return posts


@app.post("/api/posts", response_model=PostResponse)
async def create_post_api(
    post_data: PostCreate, db: AsyncSession = Depends(get_db_session)
):
    """Create new post via API"""
    try:
        user = await db.get(User, post_data.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        result = await db.execute(select(func.max(Post.id)))
        max_id = result.scalar()
        next_id = (max_id or 0) + 1

        post = Post(
            id=next_id,
            user_id=post_data.user_id,
            title=post_data.title,
            body=post_data.body,
        )
        db.add(post)
        await db.commit()
        await db.refresh(post)
        return post
    except Exception as e:
        logger.error(f"Error creating post: {e}")
        raise HTTPException(status_code=500, detail="Error creating post")


@app.get("/api/users/{user_id}/posts", response_model=List[PostResponse])
async def get_user_posts_api(user_id: int, db: AsyncSession = Depends(get_db_session)):
    """Get all posts for a specific user"""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    result = await db.execute(
        select(Post).where(Post.user_id == user_id).order_by(Post.id.desc())
    )
    posts = result.scalars().all()
    return posts
