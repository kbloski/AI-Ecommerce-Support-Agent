from di.container import Container
from application.mappers.offer_mapper import OfferMapper

def get_offer_handler(id : int):
    container = Container()
    offer_assembler = container.offer_assembler()
    offers_repository = container.offers_repository()
    
    offer = offers_repository.get_by_id(  id = id )

    if not offer:
        return None

    offer_dto = OfferMapper.to_dto( item=offer )

    result = offer_assembler.assemble_dto( offer_dto )

    return result
        

