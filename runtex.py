#! /usr/bin/python3.8
# PYTHON_ARGCOMPLETE_OK

import argparse, argcomplete
from glob import glob
import yaml
import os

# Argument parsing {{{
options = ['init', 'save', 'run']
runtex_home = os.environ['RUNTEX_HOME']

parser = argparse.ArgumentParser(prog='RUNTEX')
subparsers = parser.add_subparsers(dest='action', required=True, help=f'Choose what to do')

parse_init = subparsers.add_parser('init',
	help='Copy a template structure in the current directory')
parse_init.add_argument('template', help='Choose a template')

parse_list = subparsers.add_parser('list', help='List the currently available templates')

parse_save = subparsers.add_parser('save', help='Save current project as a template')
parse_save.add_argument('template', help='Name of the new template')
parse_save.add_argument('-u', '--update', action='store_true', help='Update existing')

parse_run  = subparsers.add_parser('run', help='Compile current project')
parse_run.add_argument('--update-figures', action='store_true', help='Use inkscape to convert'+\
    'svg figures to pdf in the figures directory')

parse_delete = subparsers.add_parser('delete', help='Delete existing template')
parse_delete.add_argument('template', help='Name of the template to delete')

argcomplete.autocomplete(parser)
args = parser.parse_args()
action = args.action

files = os.listdir()
templates_dir = os.path.join(runtex_home, 'templates')
templates = os.listdir(templates_dir)
ws_dir = os.path.abspath(os.curdir)
# }}}

if args.action == 'init': # {{{
	if 'main.tex' in files:
		print('There is already a \'main.tex\'')
		quit()

	try:
		idx = int(args.template)
		if idx >= len(templates) or idx < 0:
			print('Wrong index')
			quit()
		tmp = templates[idx]
	except ValueError:
		if not args.template in templates:
			print('Wrong template name')
			quit()
		tmp = args.template

	config_file = os.path.join(runtex_home, '.runtex.yaml')
	template_dir = os.path.join(templates_dir, tmp+'/*')

	os.system(f'cp -r {template_dir} {ws_dir}')
	os.system(f'cp {config_file} {ws_dir}')
	print(f'Successfully copied \'{tmp}\' tempate here!')
	print('Modify \'.runtex.yaml\' if needed')
# }}}

if args.action == 'list': # {{{
	templatex_text = 'Available templates:'
	for i, tmp in enumerate(templates):
		templatex_text += f'\n - {i}: {tmp}'
	print(templatex_text)
# }}}

if args.action == 'run': # {{{
	if not 'main.tex' in files:
		print('\'main.tex\' not found')
		quit()

	if not '.runtex.yaml' in files:
		print('\'.runtex.yaml\' not found')
		quit()

	with open('.runtex.yaml') as f:
		conf = yaml.load(f, Loader=yaml.FullLoader)

	if not 'build' in files:
		os.system('mkdir build')

	for f in conf['hide_misc']:
		os.system(f'mv build/{f} . 2>/dev/null')


	if 'figures' in files and args.update_figures:
		figs = os.path.join(ws_dir, 'figures', '*.svg')
		print(f'figs = {figs}')
		for fig in glob(figs):
			print(f'fig = {fig}')
			os.system(f'inkscape {fig} --export-area-drawing --batch-process --export-type=pdf --export-filename={fig[:-3]}pdf')

	os.system('pdflatex -halt-on-error main.tex')
	if conf['bibtex']:
		os.system('bibtex main.aux')
	if conf['pythontex']:
		os.system('pythontex main.tex')
		print('pythontex')


	os.system(f'cp main.pdf {conf["document_name"]}.pdf 2> /dev/null')

	for f in conf['hide_misc']:
		os.system(f'mv {f} build/ 2>/dev/null')
# }}}

if args.action == 'save': # {{{
	if not 'main.tex' in files:
		print('\'main.tex\' not found')
		quit()

	if not '.runtex.yaml' in files:
		print('\'.runtex.yaml\' not found')
		quit()

	template_dir = os.path.join(templates_dir, args.template)
	if args.update:
		if not args.template in templates:
			print(f'No such template: \'{args.template}\'')
			quit()

		os.system(f'cp -r ./* {template_dir}')
		print(f'Successfully updated template \'{args.template}\'')

	else:
		if args.template in templates:
			print(f'There is already a template: \'{args.template}\'')
			quit()

		os.system(f'mkdir {template_dir}')
		os.system(f'cp -r ./* {template_dir}')
		print(f'Successfully created template \'{args.template}\'')
# }}}

if args.action == 'delete': # {{{
	try:
		idx = int(args.template)
		if idx >= len(templates) or idx < 0:
			print('Wrong index')
			quit()
		tmp = templates[idx]
	except ValueError:
		if not args.template in templates:
			print('Wrong template name')
			quit()
		tmp = args.template

	template_dir = os.path.join(templates_dir, tmp)
	os.system(f'rm -r {template_dir}')
	print(f'Successfully deleted template \'{tmp}\'')
# }}}
