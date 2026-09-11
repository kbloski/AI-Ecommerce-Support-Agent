from enum import Enum


class ContextSectionPurpose(str, Enum):
    # Core business context
    OFFER_PROFILE = (
        "Facts describing the offer, product, target customers, capabilities, "
        "constraints, and the actual scope of the product."
    )

    BRAND_STRATEGY = (
        "Strategic information about brand positioning, meaning, desired perception, "
        "personality, and communication direction."
    )

    MARKETING_STRATEGY = (
        "Strategic information about target audiences, channels, customer journey, "
        "customer acquisition, and marketing priorities."
    )

    OFFER_STRATEGY = (
        "Strategic information about how the offer should be presented, including "
        "its value, benefits, value mechanism, and reasons to buy."
    )

    MESSAGE_STRATEGY = (
        "Information defining which messages, arguments, benefits, objections, "
        "and claims may be used in marketing communication."
    )

    AD_STRATEGY = (
        "Information defining which advertising directions, audiences, arguments, "
        "formats, and testing hypotheses should be prioritized."
    )

    # Advertising & Creative
    CREATIVE_STRATEGY = (
        "Information defining how a specific creative concept should work strategically, "
        "who it is for, and which communication mechanism it should use."
    )

    AD_SETUP = (
        "Information defining the platform, format, creative type, and production "
        "configuration used to prepare a specific advertising execution."
    )

    CREATIVE_EXECUTION_SETUP = (
        "Configuration selecting the framework, creative angle, execution style, "
        "medium-specific parameters, and additional generation instructions."
    )

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

    GENERATE_AD = (
        "Information describing a specific final advertising execution prepared "
        "for generation or production."
    )

    # Page
    PAGE_STRATEGY = (
        "Strategic information about the page objective, target audience, primary "
        "message, and how the page should guide users toward the desired action."
    )

    PAGE_REQUIREMENTS = (
        "Information defining page requirements and constraints, including required, "
        "optional, and excluded elements, as well as other structural rules."
    )

    PAGE_BLUEPRINT = (
        "Information defining the page structure, section order, and the role of each "
        "section in communication and conversion."
    )

    PAGE_CONTENT_PLAN = (
        "Information defining which messages, arguments, proof points, and content "
        "should appear within each section of the page."
    )

    PAGE_COPY = (
        "Information containing the final page copy, including headlines, body text, "
        "arguments, proof, calls to action, and other written content."
    )
