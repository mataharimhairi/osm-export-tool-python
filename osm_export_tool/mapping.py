import yaml
from osm_export_tool import GeomType
from osm_export_tool.sql import Matcher


class Theme:
	def __init__(self,name,d):
		self.name = name

		# set geometry types.
		self.points = False
		self.lines = False
		self.polygons = False
		if 'types' not in d:
			self.points = True
			self.lines = True
			self.polygons = True
		else:
			if 'points' in d['types']:
				self.points = True
			if 'lines' in d['types']:
				self.lines = True
			if 'polygons' in d['types']:
				self.polygons = True

		self.keys = d['select']

		self.matcher = None
		if 'where' in d:
			self.matcher = Matcher(d['where'][0])


	def matches(self,geom_type,tags):
		if geom_type == GeomType.POINT and not self.points:
			return False
		if geom_type == GeomType.LINE and not self.lines:
			return False
		if geom_type == GeomType.POLYGON and not self.polygons:
			return False

		return self.matcher.matches(tags)


class Mapping:
	def __init__(self,y):
		doc = yaml.safe_load(y)
		self.themes = []
		for theme_name, theme_dict in doc.items():
			self.themes.append(Theme(theme_name,theme_dict))

