class BioEntity:
    def __init__(self, id, type, features, metadata=None):
        self.id = id
        self.type = type
        self.features = features
        self.metadata = metadata or {}

class Gene(BioEntity):
    def __init__(self, name, cnv=0, expression=0):
        super().__init__(
            id=name,
            type="Gene",
            features={"cnv": cnv, "expression": expression}
        )


class Enhancer(BioEntity):
    def __init__(self, id, activity, accessibility):
        super().__init__(
            id=id,
            type="Enhancer",
            features={"activity": activity, "accessibility": accessibility}
        )


class Promoter(BioEntity):
    def __init__(self, id, methylation):
        super().__init__(
            id=id,
            type="Promoter",
            features={"methylation": methylation}
        )
