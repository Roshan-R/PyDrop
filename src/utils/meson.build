pkgdatadir1 = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir1 = join_paths(pkgdatadir1, 'pydrop/utils')

utils_sources = [
  '__init__.py',
  'tools.py'
]

install_data(utils_sources, install_dir: moduledir1)
