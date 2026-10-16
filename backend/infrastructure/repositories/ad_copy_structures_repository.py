import json


class AdCopyStructuresRepository:
    def __init__(self, path_service):
        self.path = path_service.AD_COPY_STRUCTURES_FILE

    def get_all(self):
        with self.path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def get_by_id(self, structure_id: str):
        return next((item for item in self.get_all() if item["id"] == structure_id), None)
