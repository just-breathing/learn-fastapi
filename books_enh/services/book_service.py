from typing import Optional
from sqlmodel import Session, select, func

from models.models import Book
from schemas.schemas import BookCreate, BookUpdate


class BookService:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, book_id: int) -> Optional[Book]:
        return self.session.get(Book, book_id)

    def get_by_isbn(self, isbn: str) -> Optional[Book]:
        return self.session.exec(
            select(Book).where(Book.isbn == isbn)
        ).first()

    def list(
        self,
        search: Optional[str] = None,
        genre: Optional[str] = None,
        available_only: bool = False,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Book]:
        query = select(Book)

        if search:
            term = f"%{search.lower()}%"
            query = query.where(
                func.lower(Book.title).like(term)
                | func.lower(Book.author).like(term)
            )
        if genre:
            query = query.where(
                func.lower(Book.genre).like(f"%{genre.lower()}%")
            )
        if available_only:
            query = query.where(Book.available_copies > 0)

        return list(self.session.exec(query.offset(offset).limit(limit)).all())

    def create(self, data: BookCreate) -> Book:
        if self.get_by_isbn(data.isbn):
            raise ValueError(f"A book with ISBN '{data.isbn}' already exists")

        book = Book(
            **data.model_dump(),
            available_copies=data.total_copies,
        )
        self.session.add(book)
        self.session.commit()
        self.session.refresh(book)
        return book

    def update(self, book: Book, data: BookUpdate) -> Book:
        changes = data.model_dump(exclude_unset=True)

        if "total_copies" in changes:
            delta = changes["total_copies"] - book.total_copies
            new_available = book.available_copies + delta
            if new_available < 0:
                raise ValueError(
                    "Cannot reduce total_copies below the number currently on loan"
                )
            book.available_copies = new_available

        for field, value in changes.items():
            setattr(book, field, value)

        self.session.add(book)
        self.session.commit()
        self.session.refresh(book)
        return book

    def delete(self, book: Book) -> None:
        if book.available_copies < book.total_copies:
            raise ValueError("Cannot delete a book while copies are on loan")
        self.session.delete(book)
        self.session.commit()