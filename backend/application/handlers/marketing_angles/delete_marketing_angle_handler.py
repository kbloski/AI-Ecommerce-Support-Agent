from fastapi import HTTPException

from di.container import Container


def delete_marketing_angle_handler(id: int):
    repo = Container().marketing_angles_repository()
    item = repo.get_by_id(id)
    if item is None:
        raise HTTPException(404, "Marketing angle not found")
    repo.delete(item)
    return {"deleted": True}
