import traitlets
from nbconvert import preprocessors


class LiteraryPythonPreprocessor(preprocessors.Preprocessor):
    default_include_tags = traitlets.Set(
        traitlets.Unicode(), default_value={"export", "docstring"}
    )

    def preprocess(self, nb, resources):
        nb.cells = [*self.iter_permitted_cells(nb, resources)]
        return nb, resources

    def iter_permitted_cells(self, nb, resources):
        for i, cell in enumerate(nb.cells):
            tags = set(cell.metadata.get("tags", []))

            if self.default_include_tags & tags:
                yield cell
