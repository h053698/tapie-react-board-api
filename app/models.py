from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel, Field


class User(models.Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    nickname = fields.CharField(max_length=50, unique=True)
    password = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "users"


class Post(models.Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    content = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    author = fields.ForeignKeyField("models.User", related_name="posts")

    class Meta:
        table = "posts"


# Pydantic models for API
User_Pydantic = pydantic_model_creator(User, name="User", exclude=["password"])
UserIn_Pydantic = pydantic_model_creator(User, name="UserIn", exclude_readonly=True)

# Response model with author information
Post_Pydantic = pydantic_model_creator(Post, name="Post")

# Input model for creating posts
class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
