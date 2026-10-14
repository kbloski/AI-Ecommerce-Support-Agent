from typing import List

from infrastructure.logging.logger import Logger
from domain.models.page.page_copy import PageCopy
from application.dtos.page_copy.page_copy_response_dto import PageCopyDto
from infrastructure.repositories.page_copy_repository import PageCopyRepository
from application.mappers.page_copy_mapper import PageCopyMapper
from application.assemblers.page_copy_assembler import PageCopyAssembler


class PageCopyService:

    def __init__(
        self,
        logger: Logger,
        page_copy_repository: PageCopyRepository,
        page_copy_assembler: PageCopyAssembler,
    ):
        self.logger = logger
        self.page_copy_repository = page_copy_repository
        self.page_copy_assembler = page_copy_assembler

    def create_page_copy(self, page_copy: PageCopy) -> PageCopyDto:
        created = self.page_copy_repository.create(page_copy)
        return self.get_page_copy_by_id(id=created.id)

    def get_page_copy_by_id(self, id: int) -> PageCopyDto:
        page_copy_db = self.page_copy_repository.get_by_id(id)

        if not page_copy_db:
            raise ValueError(f"Page copy {id} not found")

        page_copy_dto = PageCopyMapper.to_dto(page_copy_db)
        return self.page_copy_assembler.assemble_dto(page_copy_dto)

    def get_page_copies_by_page_content_plan(self, page_content_plan_id: int) -> List[PageCopyDto]:
        items = self.page_copy_repository.get_by_page_content_plan_id(page_content_plan_id)
        dtos = [PageCopyMapper.to_dto(item) for item in items]
        return [self.page_copy_assembler.assemble_dto(dto) for dto in dtos]
