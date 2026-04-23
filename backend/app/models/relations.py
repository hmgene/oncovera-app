class Relation:
    def __init__(self, src, dst, type, weight=1.0):
        self.src = src
        self.dst = dst
        self.type = type
        self.weight = weight
