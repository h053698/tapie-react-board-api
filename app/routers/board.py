from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models import Post, Post_Pydantic, User, PostCreate
from app.routers.auth import get_current_user
import logging

router = APIRouter(prefix="/board", tags=["board"])


@router.get("/posts", response_model=List[Post_Pydantic])
async def get_posts():
    return await Post_Pydantic.from_queryset(
        Post.all().prefetch_related("author")
    )


@router.post("/posts")
async def create_post(
    post: PostCreate, current_user: User = Depends(get_current_user)
):
    try:
        post_obj = await Post.create(
            title=post.title,
            content=post.content,
            author=current_user
        )
        print("Created post:", post_obj.id, post_obj.title)

        # Get the post with author information
        created_post = await Post.filter(id=post_obj.id).prefetch_related("author").first()
        if not created_post:
            raise HTTPException(status_code=500, detail="Failed to retrieve created post")

        return await Post_Pydantic.from_tortoise_orm(created_post)
    except Exception as e:
        print("Error creating post:", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error creating post: {str(e)}"
        )


@router.get("/posts/{post_id}")
async def get_post(post_id: int):
    post = await Post.filter(id=post_id).prefetch_related("author").first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return await Post_Pydantic.from_tortoise_orm(post)


@router.put("/posts/{post_id}", response_model=Post_Pydantic)
async def update_post(
    post_id: int, post: PostCreate, current_user: User = Depends(get_current_user)
):
    db_post = await Post.get_or_none(id=post_id)
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    if db_post.author_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this post"
        )

    await db_post.update_from_dict({
        "title": post.title,
        "content": post.content
    }).save()
    return await Post_Pydantic.from_tortoise_orm(db_post)


@router.delete("/posts/{post_id}")
async def delete_post(post_id: int, current_user: User = Depends(get_current_user)):
    post = await Post.get_or_none(id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this post"
        )

    await post.delete()
    return {"message": "Post deleted successfully"}