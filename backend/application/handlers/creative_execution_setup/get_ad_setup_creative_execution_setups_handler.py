from di.container import Container


def get_ad_setup_creative_execution_setups_handler(ad_setup_id: int):
    return Container().creative_execution_setup_service().list_for_ad_setup(ad_setup_id)
