import unittest
from osm_export_tool.sql import SQLValidator, Matcher

class TestSql(unittest.TestCase):

    def test_basic(self):
        s = SQLValidator("name = 'a name'")
        self.assertTrue(s.valid)

    def test_identifier_list(self):
        s = SQLValidator("natural in ('water','cliff')")
        self.assertTrue(s.valid)

    #TODO OGR uses text for all things so numerical comparisons will not be correct
    def test_float_value(self):
        s = SQLValidator("height > 20")
        self.assertTrue(s.valid)

    def test_not_null(self):
        s = SQLValidator("height IS NOT NULL")
        self.assertTrue(s.valid)

    def test_and_or(self):
        s = SQLValidator("height IS NOT NULL and height > 20")
        self.assertTrue(s.valid)
        s = SQLValidator("height IS NOT NULL or height > 20")
        self.assertTrue(s.valid)
        s = SQLValidator("height IS NOT NULL or height > 20 and height < 30")
        self.assertTrue(s.valid)

    def test_parens(self):
        s = SQLValidator("(admin IS NOT NULL and level > 4)")
        self.assertTrue(s.valid)
        s = SQLValidator("(admin IS NOT NULL and level > 4) AND height is not null")
        self.assertTrue(s.valid)

    def test_colons_etc(self):
        s = SQLValidator("addr:housenumber IS NOT NULL")
        self.assertTrue(s.valid)
        s = SQLValidator("admin_level IS NOT NULL")
        self.assertTrue(s.valid)

    def test_invalid_sql(self):
        s = SQLValidator("drop table planet_osm_polygon")
        self.assertFalse(s.valid)
        self.assertEqual(s.errors,['SQL could not be parsed.'])
        s = SQLValidator("(drop table planet_osm_polygon)")
        self.assertFalse(s.valid)
        self.assertEqual(s.errors,['SQL could not be parsed.'])
        s = SQLValidator ("")
        self.assertFalse(s.valid)
        self.assertEqual(s.errors,['SQL could not be parsed.'])
        s = SQLValidator("name = 'a name'; blah")
        self.assertFalse(s.valid)
        self.assertEqual(s.errors,['SQL could not be parsed.'])

    def test_column_names(self):
        s = SQLValidator("(admin IS NOT NULL and level > 4) AND height is not null")
        self.assertTrue(s.valid)
        self.assertEqual(s.column_names,['admin','level','height'])

class TestMatcher(unittest.TestCase):
    def test_matcher_binop(self):
        m = Matcher("building = 'yes'")
        self.assertTrue(m.matches({'building':'yes'}))
        self.assertFalse(m.matches({'building':'no'}))

        m = Matcher("building != 'yes'")
        self.assertFalse(m.matches({'building':'yes'}))
        self.assertTrue(m.matches({'building':'no'}))

    def test_matcher_colon(self):
        m = Matcher("addr:housenumber = 1")
        self.assertTrue(m.matches({'addr:housenumber':'1'}))

        m = Matcher("building != 'yes'")
        self.assertFalse(m.matches({'building':'yes'}))
        self.assertTrue(m.matches({'building':'no'}))

    def test_matcher_or(self):
        m = Matcher("building = 'yes' OR amenity = 'bank'")
        self.assertTrue(m.matches({'building':'yes'}))
        self.assertTrue(m.matches({'amenity':'bank'}))
        self.assertFalse(m.matches({}))

    def test_matcher_and(self):
        m = Matcher("building = 'yes' AND amenity = 'bank'")
        self.assertFalse(m.matches({'building':'yes'}))
        self.assertFalse(m.matches({'amenity':'bank'}))

    def test_matcher_is_not_null(self):
        m = Matcher("building IS NOT NULL")
        self.assertTrue(m.matches({'building':'one'}))
        self.assertTrue(m.matches({'building':'two'}))
        self.assertFalse(m.matches({}))

    def test_in(self):
        m = Matcher("building IN ('one','two')")
        self.assertTrue(m.matches({'building':'one'}))
        self.assertTrue(m.matches({'building':'two'}))
        self.assertFalse(m.matches({}))
        self.assertFalse(m.matches({'building':'three'}))
