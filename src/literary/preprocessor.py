import traitlets
from nbconvert import preprocessors


class LiteraryTagAllowListPreprocessor(preprocessors.Preprocessor):
    allow_cell_tags = traitlets.Set(
        traitlets.Unicode(), default_value={"export", "docstring"}
    )

    def check_cell_conditions(self, cell, resources: dict, index: int) -> bool:
        tags = cell.metadata.get("tags", [])
        return bool(self.allow_cell_tags.intersection(tags))

    def preprocess(self, nb, resources: dict):
        nb.cells = [
            self.preprocess_cell(cell, resources, i)[0]
            for i, cell in enumerate(nb.cells)
            if self.check_cell_conditions(cell, resources, i)
        ]
        return nb, resources

    def preprocess_cell(self, cell, resources: dict, index: int):
        return cell, resources
