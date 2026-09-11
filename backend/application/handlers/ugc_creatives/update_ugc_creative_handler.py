from di.container import Container
from application.mappers.ugc_creative_mapper import UgcCreativeMapper


def update_ugc_creative_handler(id: int, fields: dict):
    container = Container()
    repository = container.ugc_creative_repository()
    creative = repository.get_by_id(id)
    if creative is None:
        raise LookupError(f"UgcCreative with id {id} not found")

    if "is_reviewed" in fields:
        creative.is_reviewed = bool(fields["is_reviewed"])

    return UgcCreativeMapper.to_dto(repository.update(creative)).to_dict()
