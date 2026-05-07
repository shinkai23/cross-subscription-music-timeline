from app.repositories.post_repository import PostRepository
from app.schemas.post_schema import PostCreate


class PostService:
    def __init__(self, repository: PostRepository) -> None:
        self.repository = repository

    def list_posts(self, limit: int = 50, offset: int = 0):
        return self.repository.list_posts(limit=limit, offset=offset)

    def create_post(self, post_in: PostCreate):
        return self.repository.create_post(post_in)
