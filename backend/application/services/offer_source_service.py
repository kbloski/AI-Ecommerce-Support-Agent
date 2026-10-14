import json

from infrastructure.services.path_service import PathService
from infrastructure.logging.logger import Logger
from infrastructure.parsers.docx_parser import DocxParser
from infrastructure.parsers.txt_parser import TxtParser
from application.services.ai_service import AiService
from application.dtos.offer_sources.offer_source_dto import OfferSourceDto
from infrastructure.repositories.offer_source_repository import OfferSourceRepository
from application.mappers.offer_source_mapper import OfferSourceMapper
from application.assemblers.offer_source_assembler import OfferSourceAssembler
from application.services.llm_context_builder import build_llm_section
from domain.enums.context_section_purpose import ContextSectionPurpose

class OfferSourceService:

    def __init__(
        self,
        logger: Logger,
        docx_parser: DocxParser,
        txt_parser: TxtParser,
        ai_service: AiService,
        path_service: PathService,
        offer_source_repository : OfferSourceRepository,
        offer_source_assembler : OfferSourceAssembler
    ):
        self.logger = logger
        self.docx_parser = docx_parser
        self.path_service = path_service
        self.txt_parser = txt_parser
        self.ai_service = ai_service
        self.offer_source_repository = offer_source_repository
        self.offer_source_assembler = offer_source_assembler



    def get_offer_source_details_by_id(self, offer_source_id : int ) -> OfferSourceDto :
        offer_source_db = self.offer_source_repository.get_by_id( id=offer_source_id)
        offer_source_dto = OfferSourceMapper.to_dto(item=offer_source_db)
        assembled_offer_source = self.offer_source_assembler.assemble_dto(item=offer_source_dto)
        return assembled_offer_source



    def build_llm_context(self, offer_source_id: int) -> str:
        assembled_offer_source = self.get_offer_source_details_by_id(offer_source_id=offer_source_id)

        # Nieprzejrzane dane pozostają dostępne w API, ale nie mogą wpływać na
        # generowanie kolejnych elementów przez LLM.
        assembled_offer_source.target_audiences = [
            target_audience
            for target_audience in assembled_offer_source.target_audiences
            if target_audience.is_reviewed
        ]
        assembled_offer_source.offer_source_elements = [
            offer_source_element
            for offer_source_element in assembled_offer_source.offer_source_elements
            if offer_source_element.is_reviewed
        ]

        offer_source_json = json.dumps(
            assembled_offer_source.to_content_dict(),
            ensure_ascii=False,
            indent=2,
            default=str
        )

        return build_llm_section("offer_source", offer_source_json, purpose=ContextSectionPurpose.OFFER_SOURCE.value)



    def build_offer_source_from_materials_raw(self):
        self.logger.info("Build offer_source from materials raw start")

        # 🔹 folder RAW
        raw_folder = self.path_service.RAW_ECOMMERCE_OFFER_SOURCE

        # 🔹 zbieranie plików (AI-friendly)
        allowed_ext = {".docx", ".txt"}
        files = [
            f for f in raw_folder.iterdir()
            if f.is_file() and f.suffix in allowed_ext
        ]
        self.logger.info(f"Found {len(files)} raw files")

        # 🔹 parsing (DOCX na razie)
        parsed_documents = []

        for file in files:
            try:
                if file.suffix == ".docx":
                    text = self.docx_parser.parse(file)
                else:
                    text = self.txt_parser.parse(file)

                parsed_documents.append({
                    "file": str(file),
                    "content": text
                })

            except Exception as e:
                self.logger.error(f"Failed to parse file {file}: {str(e)}")


        return {
            "message": "OfferSource build completed",
            "files_count": len(files),
            "parsed_count": len(parsed_documents),
            # "documents": parsed_documents
        }
