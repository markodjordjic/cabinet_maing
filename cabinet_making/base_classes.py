class BaseCorpus:
    """Dimensions

    """
    def __init__(self,
                 height: int, 
                 width: int, 
                 depth: int, 
                 back_tolerance: int = 2,
                 back_type: str = 'groove'):
        self.height = height
        self.width = width
        self.depth = depth
        self.back_tolerance = back_tolerance
        self.back_type = back_type
        self.side_edge_banding = None
        self.top_bottom_edge_banding = None


class BaseElevation:

    def __init__(self, 
                 height: int,
                 sections: list[int] = [],
                 drawers: list[int] = [],
                 dividers: list[int] = [],
                 shelves: int = None) -> None:
        self.height = height
        self.sections = sections  # From top, gaps and reveals included.
        self.drawers = drawers
        self.dividers = dividers
        self.shelves = shelves