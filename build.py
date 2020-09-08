import yaml
import json
import re
import argparse
import os
from os import path
from pathlib import Path

def var_value(value):
	value = str(value)
	value = re.sub(r'(--[\w\.\-@/]+)', lambda r: 'var({})'.format(var_name(r.group())), value)
	if re.match(r'var\([\w\-]+\)\s+\w+\(', value):
		value = 'color({})'.format(value)
	return value

def var_name(var):
	return re.sub(r'[\.@\$/]', '-', var)

def build(data):
	if 'variables' in data:
		variables = dict()
		for name, value in data['variables'].items():
			variables[var_name(name)] = var_value(value)
		data['variables'] = variables
	if 'globals' in data:
		globals_ = dict()
		for name, value in data['globals'].items():
			globals_[name] = var_value(value)
		data['globals'] = globals_
	if 'syntax' in data:
		rules = []
		for base_scopes, styles in data['syntax'].items():
			base_scopes = base_scopes.split(r'\s*,\s*')
			for scopes, style in styles.items():
				rule = dict()
				name = None
				if 'scope' in style:
					name = scopes
					scopes = style['scope']
					del style['scope']
				if not isinstance(scopes, list):
					scopes = scopes.split(r'\s*,\s*')
				if name:
					rule['name'] = name
				combined_scope = list()
				for base_scope in base_scopes:
					for scope in scopes:
						combined_scope += ['{} {}'.format(base_scope, scope).strip()]
				combined_scope = ', '.join(combined_scope)
				rule['scope'] = combined_scope
				for name, value in style.items():
					rule[name] = var_value(value)
				rules += [rule]
		data['rules'] = rules
	whitelisted_keys = ['name', 'author', 'variables', 'globals', 'rules']
	return { key: data[key] for key in whitelisted_keys }

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('colors', nargs='*', default=['./color_schemes/GitHub.yml', './color_schemes/OneDarkPro.yml'])
	parser.add_argument('--dev', action='store_true', help='watch yml and generate color schemes on changes')
	args = parser.parse_args()

	for src in args.colors:
		color_scheme = path.splitext(path.basename(src))[0]
		dsts = ['color_schemes/{}.sublime-color-scheme'.format(color_scheme)]

		if args.dev:
			dsts += ['{}/Library/Application Support/Sublime Text/Packages/User/{}-dev.sublime-color-scheme'.format(Path.home(), color_scheme)]

		with open(src) as infile:
			data = yaml.load(infile, Loader=yaml.FullLoader)
			result = build(data)
			for dst in dsts:
				with open(dst, 'w') as outfile:
					json.dump(result, outfile, indent=2)
