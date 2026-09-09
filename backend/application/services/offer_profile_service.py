import json

from infrastructure.services.path_service import PathService
from infrastructure.logging.logger import Logger
from infrastructure.parsers.docx_parser import DocxParser
from infrastructure.parsers.txt_parser import TxtParser
from application.services.ai_service import AiService
from application.dtos.offer_profiles.offer_profile_dto import OfferProfileDto
from infrastructure.repositories.offer_profile_repository import OfferProfileRepository
from application.mappers.offer_profile_mapper import OfferProfileMapper
from application.assemblers.offer_profile_assembler import OfferProfileAssembler
from application.services.llm_context_builder import build_llm_section
from domain.enums.context_section_purpose import ContextSectionPurpose

class OfferProfileService:

    def __init__(
        self,
        logger: Logger,
        docx_parser: DocxParser,
        txt_parser: TxtParser,
        ai_service: AiService,
        path_service: PathService,
        offer_profile_repository : OfferProfileRepository,
        offer_profile_assembler : OfferProfileAssembler
    ):
        self.logger = logger
        self.docx_parser = docx_parser
        self.path_service = path_service
        self.txt_parser = txt_parser
        self.ai_service = ai_service
        self.offer_profile_repository = offer_profile_repository
        self.offer_profile_assembler = offer_profile_assembler



    def get_offer_profile_details_by_id(self, offer_profile_id : int ) -> OfferProfileDto :
        offer_profile_db = self.offer_profile_repository.get_by_id( id=offer_profile_id)
        offer_profile_dto = OfferProfileMapper.to_dto(item=offer_profile_db)
        assembled_offer_profile = self.offer_profile_assembler.assemble_dto(item=offer_profile_dto)
        return assembled_offer_profile



    def build_llm_context(self, offer_profile_id: int) -> str:
        assembled_offer_profile = self.get_offer_profile_details_by_id(offer_profile_id=offer_profile_id)

        offer_profile_json = json.dumps(
            assembled_offer_profile.to_content_dict(),
            ensure_ascii=False,
            indent=2,
            default=str
        )

        return build_llm_section("offer_profile", offer_profile_json, purpose=ContextSectionPurpose.OFFER_PROFILE.value)



    def build_offer_profile_from_materials_raw(self):
        self.logger.info("Build offer_profile from materials raw start")

        # 🔹 folder RAW
        raw_folder = self.path_service.RAW_ECOMMERCE_OFFER_PROFILE

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
            "message": "OfferProfile build completed",
            "files_count": len(files),
            "parsed_count": len(parsed_documents),
            # "documents": parsed_documents
        }
