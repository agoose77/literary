![Literary logo with an orange cursive uppercase L inside black square brackets](assets/logo.png)

# Literary 
[![pypi-badge][]][pypi] [![binder-badge][]][binder]  

[binder]:
  https://mybinder.org/v2/gh/agoose77/literary/HEAD?urlpath=lab%2Ftree%2Fexamples
[binder-badge]: https://mybinder.org/badge_logo.svg
[pypi-badge]: https://img.shields.io/pypi/v/literary
[pypi]: https://pypi.org/project/literary

This package is an exploration of the [literate programming](http://www.literateprogramming.com) idea [pioneered by
 Donald
Knuth](https://www-cs-faculty.stanford.edu/~knuth/lp.html) and implemented in the
 [`nbdev` package](https://github.com/fastai/nbdev). Although `nbdev` looks to be a very
mature and comprehensive tool, it is quite opinionated. This package is an
investigation into what a smaller `nbdev` might look like.

## Philosophy
1. **Low mental overhead**   
 Realistically, most Python programmers that wish to write packages need to have some
 familiarity with the Python package development model, including the conventional
structure of a package. For this reason, I feel that it is important to design
`literary` such that these skills translate directly to designing libraries with
notebooks
2. **Minimal downstream impact**  
 Users of `literary` packages should not realise that they are consuming 
 notebook-generated code at runtime. This means that a pure-Python package needs to
 be generated from the notebooks, and it must use the conventional import model. For
 this reason, `literary` should only exist as a development dependency of
 the package.
  

## Differences with `nbdev`
* Use of cell tags instead of comments or magics to dictate exports
* Use of `nbconvert` machinery to build the pure-Python lib package
* Use of import hooks to import other notebooks
    * Maintains a similar programming model to conventional module
 development
    * Reduces the need to modify notebook contents during conversion 
* Minimal runtime overhead
    * Features like `patch` are removed from the generated module (& imported notebook source) using AST transformations
* Currently no documentation generation
    * Loosely, the plan is to use existing notebook-book tooling to re-use the
     existing Jupyter ecosystem


## Differences with Knuth
Knuth introduced the `tangle` and `weave` programs to produce separate documentation and source code for compilation. 
Literary differs in treating the notebook as the "ground truth" for documentation + testing, and generating smaller source code for packaging.


## Design
The plan for this package is:
1. Notebooks will be written inside `<PACKAGE_NAME>/` in literary project's root directory
2. Notebooks will respect relative imports and other pure-Python features to minimise the differences between the generated packages and the notebooks
3. A pure-python generated `lib/<PACKAGE_NAME>/` directory will be built before Poetry builds the final project.   
  E.g. 
    ```toml
    [tool.poetry]
    # ...
    packages = [
      { include = "<PACKAGE_NAME>", from = "lib" },
    ]
    ```
