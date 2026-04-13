from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from database.db import get_session
from schemas.loan import LoanResponse, LoanCreate, ReturnResponse
from services.loan_service import LoanService


class LoanRouter:

    def __init__(self):
        self.router = APIRouter(prefix="/loans", tags=["Loans"])
        self._register_routes()

    def _get_service(self, session: Session = Depends(get_session)) -> LoanService:
        return LoanService(session)

    def _register_routes(self):
        self.router.add_api_route(
            "/",
            self.borrow_book,
            methods=["POST"],
            response_model=LoanResponse,
            status_code=status.HTTP_201_CREATED,
        )
        self.router.add_api_route(
            "/{loan_id}/return",
            self.return_book,
            methods=["POST"],
            response_model=ReturnResponse,
        )
        self.router.add_api_route(
            "/",
            self.list_loans,
            methods=["GET"],
            response_model=list[LoanResponse],
        )
        self.router.add_api_route(
            "/{loan_id}",
            self.get_loan,
            methods=["GET"],
            response_model=LoanResponse,
        )

    def borrow_book(
        self,
        data: LoanCreate,
        service: LoanService = Depends(_get_service),
    ) -> LoanResponse:
        return service.borrow(data)

    def return_book(
        self,
        loan_id: int,
        service: LoanService = Depends(_get_service),
    ) -> ReturnResponse:
        return service.return_book(loan_id)

    def list_loans(
        self,
        service: LoanService = Depends(_get_service),
        member_id: Optional[int] = Query(None),
        book_id: Optional[int] = Query(None),
        active_only: bool = Query(False),
        overdue_only: bool = Query(False),
        offset: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
    ) -> list[LoanResponse]:
        return service.list(
            member_id=member_id,
            book_id=book_id,
            active_only=active_only,
            overdue_only=overdue_only,
            offset=offset,
            limit=limit,
        )

    def get_loan(
        self,
        loan_id: int,
        service: LoanService = Depends(_get_service),
    ) -> LoanResponse:
        loan = service.get_by_id_or_raise(loan_id)
        from schemas.loan import LoanResponse
        return LoanResponse.from_loan(loan)


router = LoanRouter().router
