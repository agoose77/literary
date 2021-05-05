from setuptools.build_meta import (
    build_sdist as orig_build_sdist,
    build_wheel as orig_build_wheel,
)
from literary.commands.build import LiteraryBuildApp


def _build_literary():
    LiteraryBuildApp.launch_instance(argv=[])


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    _build_literary()
    return orig_build_wheel(
        wheel_directory,
        config_settings=config_settings,
        metadata_directory=metadata_directory,
    )


def build_sdist(sdist_directory, config_settings=None):
    _build_literary()
    return orig_build_sdist(sdist_directory, config_settings=config_settings)
