class OfferProfileDto:
    def __init__(self, id, offer_source_id, name, created_at):
        self.id = id
        self.offer_source_id = offer_source_id
        self.name = name
        self.created_at = created_at
        self.additional_contexts = []

    def to_dict(self):
        return {"id": self.id, "offer_source_id": self.offer_source_id, "name": self.name, "created_at": self.created_at, "additional_contexts": self.additional_contexts}

    def to_content_dict(self):
        return {"name": self.name, "additional_contexts": [{"name": context["name"], "content": context["content"]} for context in self.additional_contexts]}
