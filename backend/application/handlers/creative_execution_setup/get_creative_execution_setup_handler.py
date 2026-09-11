from di.container import Container


def get_creative_execution_setup_handler(id: int):
    return (
        Container()
        .creative_execution_setup_service()
        .get_creative_execution_setup_details_by_id(id)
    )
