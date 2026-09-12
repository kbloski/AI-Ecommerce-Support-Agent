from di.container import Container


def get_all_generate_ads_handler():
    return Container().generate_ad_service().get_all_generate_ads()
