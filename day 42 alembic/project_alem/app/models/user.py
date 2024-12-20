from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func
from app.models.base import Base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=func.now())

    posts = relationship("Post", back_populates="owner")  # One-to-many relationship
    comments = relationship("Comment", back_populates="author")  # One-to-many relationship

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, email={self.email})>"

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)
    created_at = Column(DateTime, default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))  # Foreign key to User table

    owner = relationship("User", back_populates="posts")  # Many-to-one relationship with User
    comments = relationship("Comment", back_populates="post")  # One-to-many relationship with Comment

    def __repr__(self):
        return f"<Post(id={self.id}, title={self.title})>"

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    created_at = Column(DateTime, default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))  # Foreign key to User table
    post_id = Column(Integer, ForeignKey("posts.id"))  # Foreign key to Post table

    author = relationship("User", back_populates="comments")  # Many-to-one relationship with User
    post = relationship("Post", back_populates="comments")  # Many-to-one relationship with Post

    def __repr__(self):
        return f"<Comment(id={self.id}, content={self.content})>"
