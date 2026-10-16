from pathlib import Path
from infrastructure.logging.logger import Logger
from domain.enums.llm_rule_set import LlmRuleSet

class PathService:
    def __init__(self,
            logger: Logger
        ):

        self.BASE_DIR = Path(__file__).resolve().parent.parent.parent

        self.UPLOADS_DEV = self.BASE_DIR / "uploads" / "dev"
        self.UPLOADS_PROD = self.BASE_DIR / "uploads" / "prod"

        self.PROMPTS_DIR = self.BASE_DIR / "infrastructure" / "ai" / "prompts"

        self.RULES_DIR = self.BASE_DIR / "infrastructure" / "ai" / "rules"
        self.RULE_SET_PATHS = {
            LlmRuleSet.JSON_OUTPUT: self.RULES_DIR / "json_output.rules.md",
            LlmRuleSet.ENGLISH_OUTPUT: self.RULES_DIR / "english_output.rules.md",
        }

        self.FRAMEWORKS_DIR = self.BASE_DIR / "infrastructure" / "ai" / "frameworks"

        self.ADS_DIR = self.BASE_DIR / "infrastructure" / "ads"
        self.AD_FRAMEWORKS_FILE = self.ADS_DIR / "ads_frameworks.json"
        self.AD_COPY_STRUCTURES_FILE = self.ADS_DIR / "ad_copy_structures.json"
        self.CREATIVE_ANGELS_FILE = self.ADS_DIR / "creative_angels.json"
        self.EXECUTION_STYLES_FILE = self.ADS_DIR / "execution_styles.json"
        self.PLATFORMS_FILE = self.ADS_DIR / "platforms.json"

        self.PAGES_DIR = self.BASE_DIR / "infrastructure" / "pages"
        self.PAGE_SECTION_TYPES_FILE = self.PAGES_DIR / "page_section_types.json"

        # self.DATA_DIR = self.BASE_DIR / "data"
        # self.RAW_ECOMMERCE_OFFER_SOURCE = self.DATA_DIR / "raw" / "ecommerce_offer_source"
        # self.ECOMMERCE_OFFER_SOURCE = self.DATA_DIR / "offer_source" / "ecommerce"

    def rule_set_path(self, rule_set: LlmRuleSet) -> Path:
        return self.RULE_SET_PATHS[rule_set]

