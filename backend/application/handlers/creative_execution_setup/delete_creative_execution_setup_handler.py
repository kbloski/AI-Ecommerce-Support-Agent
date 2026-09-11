from di.container import Container


def delete_creative_execution_setup_handler(id: int):
    if not Container().creative_execution_setup_repository().delete(id):
        raise ValueError(f"Creative Execution Setup {id} not found")
    return {"deleted": True, "id": id}
