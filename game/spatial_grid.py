class SpatialGrid:
    """
    A flat hash-map spatial grid for fast nearest-neighbour queries.

    Usage (in Game.__init__):
        self.spatial_grid = SpatialGrid(cell_size=512)

    Usage (each frame, before any entity update — in update_game_logic):
        self.spatial_grid.rebuild(self.all_entities)

    Usage (inside get_nearest / acquire_target):
        nearby = self.game.spatial_grid.query(self.rect, radius=self.acquire_range)
        # 'nearby' replaces self.game.all_entities in the filtering loop
    """

    def __init__(self, cell_size: int = 512):
        # cell_size should be >= your largest acquire_range
        self.cell_size = cell_size
        # Maps (col, row) → list of entities whose rect overlaps that cell
        self._cells: dict = {}

    # ------------------------------------------------------------------ #
    def _cell_coords(self, rect) -> list:
        """Return every cell (col, row) that the rect overlaps."""
        cs   = self.cell_size
        x0   = rect.left   // cs
        y0   = rect.top    // cs
        x1   = rect.right  // cs
        y1   = rect.bottom // cs
        return [(cx, cy)
                for cx in range(x0, x1 + 1)
                for cy in range(y0, y1 + 1)]

    # ------------------------------------------------------------------ #
    def rebuild(self, entities: list) -> None:
        """
        Clear and repopulate the grid from the current entity list.

        Call once per frame, before any entity calls acquire_target().
        Cost: O(N) — one pass over all entities.

        WHERE TO CALL:
            In Game.update_game_logic() or wherever you currently call
            entity.manage() in a loop — call rebuild() BEFORE that loop.

            Example:
                self.spatial_grid.rebuild(self.all_entities)
                for entity in self.all_entities:
                    entity.manage()
        """
        self._cells.clear()
        for entity in entities:
            if entity.dead or entity.death:
                continue
            for cell in self._cell_coords(entity.rect):
                if cell not in self._cells:
                    self._cells[cell] = []
                self._cells[cell].append(entity)

    # ------------------------------------------------------------------ #
    def query(self, rect, radius: int) -> list:
        """
        Return all entities whose cell overlaps the search area.

        Parameters
        ----------
        rect   : the searcher's pygame.Rect
        radius : how far to search (use self.acquire_range)

        Returns a deduplicated list — safe to filter directly.

        """
        cs = self.cell_size
        # Expand the rect by radius to cover cells at the edge of range
        search_rect_x0 = (rect.left   - radius) // cs
        search_rect_y0 = (rect.top    - radius) // cs
        search_rect_x1 = (rect.right  + radius) // cs
        search_rect_y1 = (rect.bottom + radius) // cs

        seen    = set()
        results = []
        for cx in range(search_rect_x0, search_rect_x1 + 1):
            for cy in range(search_rect_y0, search_rect_y1 + 1):
                for entity in self._cells.get((cx, cy), []):
                    if id(entity) not in seen:
                        seen.add(id(entity))
                        results.append(entity)
        return results