# app/socket/events.py
import uuid
import logging
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from ..db_models import Post, Like, Comment
from .schemas import PostSchema, CommentSchema
from ...main import async_session
from .utils import get_current_user, validate_uuid
from fastapi_socketio import SocketManager

logger = logging.getLogger(__name__)
socket_manager = SocketManager()

post_schema = PostSchema()
comment_schema = CommentSchema()


@socket_manager.on('connect')
async def handle_connect(sid, environ):
    logger.info(f"Client connected: {sid}")
    try:
        user_id = await get_current_user(environ)
        logger.info(f"User {user_id} authenticated successfully")
    except Exception:
        await socket_manager.emit('error', {'message': 'Authentication failed'}, to=sid)
        await socket_manager.disconnect(sid)


@socket_manager.on('disconnect')
async def handle_disconnect(sid):
    logger.info(f"Client disconnected: {sid}")


@socket_manager.on('like_post')
async def on_like_post(sid, data):
    logger.info(f"like_post event received: {data}")
    try:
        user_id = await get_current_user(socket_manager.environ[sid])
        post_id = validate_uuid(data.get('post_id'), 'Post ID')
    except Exception:
        return

    try:
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(select(Post).where(Post.id == post_id).with_for_update())
                post = result.scalar_one_or_none()

                if not post:
                    await socket_manager.emit('error', {'message': 'Post not found'}, to=sid)
                    return

                like = await session.execute(select(Like).where(Like.user_id == user_id, Like.post_id == post_id))
                like_obj = like.scalar_one_or_none()

                if like_obj:
                    await session.delete(like_obj)
                    post.likes_count = max(post.likes_count - 1, 0)
                else:
                    new_like = Like(user_id=user_id, post_id=post_id)
                    session.add(new_like)
                    post.likes_count += 1

        await socket_manager.emit('update_likes', post_schema.dump(post), broadcast=True)

    except (IntegrityError, SQLAlchemyError) as e:
        logger.error(f"DB error on like_post: {str(e)}")
        await socket_manager.emit('error', {'message': 'Database error'}, to=sid)


@socket_manager.on('comment_post')
async def on_comment_post(sid, data):
    logger.info(f"comment_post event received: {data}")
    try:
        user_id = await get_current_user(socket_manager.environ[sid])
        post_id = validate_uuid(data.get('post_id'), 'Post ID')
        content = data.get('content', '').strip()

        if not content or not (1 <= len(content) <= 500):
            await socket_manager.emit('error', {'message': 'Invalid content length'}, to=sid)
            return

    except Exception:
        return

    try:
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(select(Post).where(Post.id == post_id).with_for_update())
                post = result.scalar_one_or_none()
                if not post:
                    await socket_manager.emit('error', {'message': 'Post not found'}, to=sid)
                    return

                comment = Comment(content=content, user_id=user_id, post_id=post_id)
                session.add(comment)
                post.comments_count += 1

        await socket_manager.emit('new_comment', comment_schema.dump(comment), broadcast=True)

    except (IntegrityError, SQLAlchemyError) as e:
        logger.error(f"DB error on comment_post: {str(e)}")
        await socket_manager.emit('error', {'message': 'Database error'}, to=sid)
