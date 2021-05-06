![Literary logo with an orange cursive uppercase L inside black square brackets](https://raw.githubusercontent.com/agoose77/literary/master/assets/logo.png)

# Literary 
[![pypi-badge][]][pypi] [![binder-badge][]][binder] [![wiki-badge][]][wiki]

[binder-badge]: https://mybinder.org/badge_logo.svg
[binder]:
  https://mybinder.org/v2/gh/agoose77/literary/HEAD?urlpath=lab%2Ftree%2Fexamples
[pypi-badge]: https://img.shields.io/pypi/v/literary
[pypi]: https://pypi.org/project/literary
[wiki-badge]: https://img.shields.io/static/v1?label=wiki&message=read&color=green&logo=github
[wiki]: https://github.com/agoose77/literary/wiki

## TL;DR
Literary is a Python tool to make Jupyter (IPython) notebooks behave like pure-Python packages. This allows pure-Python packages to be generated from notebooks, and notebooks to be imported at runtime.

This package is an exploration of the [literate programming](http://www.literateprogramming.com) idea [pioneered by
 Donald
Knuth](https://www-cs-faculty.stanford.edu/~knuth/lp.html) and implemented in the
 [`nbdev` package](https://github.com/fastai/nbdev). Although `nbdev` looks to be a very
mature and comprehensive tool, it is quite opinionated. This package is an
investigation into what a smaller `nbdev` might look like.

## Philosophy 📖
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
