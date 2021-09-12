pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'pydrop')
gnome = import('gnome')

subdir('utils')

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'pydrop.in',
  output: 'pydrop',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir')
)

pydrop_sources = [
  '__init__.py',
  'main.py',
  'window.py',
  'style.css',
]

install_data(pydrop_sources, install_dir: moduledir)
