from enum import Enum


class ContextSectionPurpose(str, Enum):
    OFFER_PROFILE = "Profile information and attached additional contexts defining the offer perspective."
    TARGET_AUDIENCES = "Selected target audience segments whose needs and buying motivations guide generation."
    MARKETING_ANGLE = "Selected persuasive perspectives that should guide the advertising concept."
    AD_CONCEPT = "Selected advertising concepts defining the creative idea, format, and key message."

    # Core business context
    OFFER_SOURCE = (
        "Facts describing the offer, product, target customers, capabilities, "
        "constraints, and the actual scope of the product."
    )

    # Advertising & Creative

    AD_FRAMEWORK = (
        "Information defining the required advertising framework, its ordered steps, "
        "and structural rules for the execution."
    )

    PLATFORM = (
        "Publishing platform constraints, conventions, formats, and presentation rules."
    )

    CAMPAIGN_STRATEGY = (
        "Information about the objective, audience, offer, and primary strategic "
        "direction of a specific advertising campaign."
    )

    MESSAGE_ANGLE = (
        "Information defining the main argument or communication perspective used "
        "to present the product, problem, benefit, or offer."
    )

    CREATIVE_ANGLE = (
        "Information defining the creative perspective or mechanism used to present "
        "a message, product, problem, or benefit in an advertisement."
    )

    AD_STRUCTURE = (
        "Information defining the structure of an advertisement, the sequence of its "
        "stages, and the role of each stage in communication and conversion."
    )

    EXECUTION_STYLE = (
        "Information defining the visual, stylistic, and production approach used "
        "to execute an advertising creative."
    )

    PLATFORM_REQUIREMENTS = (
        "Information describing the publishing platform, including its formats, "
        "constraints, conventions, and requirements that the creative must follow."
    )


    # Design
    COLOR_PHILOSOPHY = (
        "Reference describing base colors, their associations, suitable brand types "
        "and shades, used to choose colors that fit the desired brand perception."
    )

    TYPOGRAPHY_PHILOSOPHY = (
        "Reference describing typeface styles, their brand personality, suitable brand "
        "types and example fonts, used to choose fonts that fit the desired brand perception."
    )

    EXISTING_BRAND_STYLES = (
        "Brand styles already created for this offer; new proposals should differ from them."
    )

    # Generation
    GENERATION_INSTRUCTIONS = (
        "Additional instructions from the user that guide this generation."
    )

    # Page

    PAGE_BLUEPRINT = (
        "Information defining page blueprint and constraints, including required, "
        "optional, and excluded elements, as well as other structural rules."
    )
