from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from database.db import get_session
from schemas.member import MemberCreate, MemberResponse, MemberUpdate
from services.member_service import MemberService
from models.member import Member

class MemberRouter:

    def __init__(self):
        self.router = APIRouter(prefix="/members", tags=["Members"])
        self._register_routes()

    def _get_service(self, session: Session = Depends(get_session)) -> MemberService:
        return MemberService(session)

    def _register_routes(self):
        self.router.add_api_route(
            "/",
            self.create_member,
            methods=["POST"],
            response_model=MemberResponse,
            status_code=status.HTTP_201_CREATED,
        )
        self.router.add_api_route(
            "/",
            self.list_members,
            methods=["GET"],
            response_model=list[MemberResponse],
        )
        self.router.add_api_route(
            "/{member_id}",
            self.get_member,
            methods=["GET"],
            response_model=MemberResponse,
        )
        self.router.add_api_route(
            "/{member_id}",
            self.update_member,
            methods=["PATCH"],
            response_model=MemberResponse,
        )
        self.router.add_api_route(
            "/{member_id}",
            self.deactivate_member,
            methods=["DELETE"],
            status_code=status.HTTP_204_NO_CONTENT,
        )

    def create_member(
        self,
        data: MemberCreate,
        service: MemberService = Depends(_get_service),
    ) -> Member:
        return service.create(data)

    def list_members(
        self,
        service: MemberService = Depends(_get_service),
        search: Optional[str] = Query(None, description="Search by name or email"),
        active_only: bool = Query(True),
        offset: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
    ) -> list[Member]:
        return service.list(
            search=search,
            active_only=active_only,
            offset=offset,
            limit=limit,
        )

    def get_member(
        self,
        member_id: int,
        service: MemberService = Depends(_get_service),
    ) -> Member:
        return service.get_by_id(member_id)

    def update_member(
        self,
        member_id: int,
        data: MemberUpdate,
        service: MemberService = Depends(_get_service),
    ) -> Member:
        return service.update(member_id, data)

    def deactivate_member(
        self,
        member_id: int,
        service: MemberService = Depends(_get_service),
    ) -> None:
        service.deactivate(member_id)


router = MemberRouter().router
