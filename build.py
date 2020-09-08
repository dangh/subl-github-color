import yaml
import json
import re
import argparse
import os
from os import path
from pathlib import Path

VAR_REGEX = r'--[^\s,)]+'

def is_color(value):
	if re.match(r'aliceblue|antiquewhite|aqua|aquamarine|azure|beige|bisque|black|blanchedalmond|blue|blueviolet|brown|burlywood|cadetblue|chartreuse|chocolate|coral|cornflowerblue|cornsilk|crimson|cyan|darkblue|darkcyan|darkgoldenrod|darkgray|darkgreen|darkgrey|darkkhaki|darkmagenta|darkolivegreen|darkorange|darkorchid|darkred|darksalmon|darkseagreen|darkslateblue|darkslategray|darkslategrey|darkturquoise|darkviolet|deeppink|deepskyblue|dimgray|dimgrey|dodgerblue|firebrick|floralwhite|forestgreen|fuchsia|gainsboro|ghostwhite|gold|goldenrod|gray|green|greenyellow|grey|honeydew|hotpink|indianred|indigo|ivory|khaki|lavender|lavenderblush|lawngreen|lemonchiffon|lightblue|lightcoral|lightcyan|lightgoldenrodyellow|lightgray|lightgreen|lightgrey|lightpink|lightsalmon|lightseagreen|lightskyblue|lightslategray|lightslategrey|lightsteelblue|lightyellow|lime|limegreen|linen|magenta|maroon|mediumaquamarine|mediumblue|mediumorchid|mediumpurple|mediumseagreen|mediumslateblue|mediumspringgreen|mediumturquoise|mediumvioletred|midnightblue|mintcream|mistyrose|moccasin|navajowhite|navy|oldlace|olive|olivedrab|orange|orangered|orchid|palegoldenrod|palegreen|paleturquoise|palevioletred|papayawhip|peachpuff|peru|pink|plum|powderblue|purple|rebeccapurple|red|rosybrown|royalblue|saddlebrown|salmon|sandybrown|seagreen|seashell|sienna|silver|skyblue|slateblue|slategray|slategrey|snow|springgreen|steelblue|tan|teal|thistle|tomato|turquoise|violet|wheat|white|whitesmoke|yellow|yellowgreen', value):
		return True
	if re.search(r'^(#|rgba?|hsla?|hwb)', value):
		return True
	return False

def var_name(var):
	return re.sub(r'[^\w]', '-', var)

def build(data):
	variables = dict()
	variable_types = dict()
	globals_ = dict()
	rules = list()

	def embed_var(value):
		def embed(match):
			nonlocal variables
			var = match.group()
			if var not in variable_types:
				raise Exception('{} is not defined'.format(var))
			if variable_types[var] == 'embed':
				return variables[var_name(var)]
			return var
		return re.sub(VAR_REGEX, embed, value)

	def ref_var(value):
		def ref(match):
			nonlocal variables
			var = match.group()
			if var not in variable_types:
				raise Exception('{} is not defined'.format(var))
			return 'var({})'.format(var_name(var))
		return re.sub(VAR_REGEX, ref, value)

	def adjust_color(value):
		if re.search(r'\b(blenda?|a(lpha)?|s(aturation)?|l(ightness)?|min-contrast)\(', value):
			return 'color({})'.format(value)
		return value

	# preprocessing variables
	if 'variables' in data:
		for name, value in data['variables'].items():
			value = str(value)
			if re.search(VAR_REGEX, value):
				variable_types[name] = 'ref'
			elif is_color(value):
				variable_types[name] = 'color'
			else:
				variable_types[name] = 'embed'
			variables[var_name(name)] = value
		for name, value in variables.items():
			variables[name] = adjust_color(ref_var(embed_var(value)))
	if 'globals' in data:
		for name, value in data['globals'].items():
			value = str(value)
			globals_[name] = adjust_color(ref_var(embed_var(value)))
	if 'syntax' in data:
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
					rule[name] = adjust_color(ref_var(embed_var(value)))
				rules += [rule]
	return dict(
		variables={ var_name(key): variables[var_name(key)] for key, value in variable_types.items() if value != 'embed' },
		globals=globals_,
		rules=rules
	)

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
