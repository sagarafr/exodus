import unittest

from web_site.foo.apiv6 import (dict_to_camel_case, dict_to_snake_case,
                      to_camel_case, to_snake_case,
                      format_object)


class TestAPIv1(unittest.TestCase):

    def test_to_snake_case(self):
        self.assertEquals(to_snake_case('alongstring'), 'alongstring')
        self.assertEquals(to_snake_case('a_long_string'), 'a_long_string')
        self.assertEquals(to_snake_case('aLongString'), 'a_long_string')
        self.assertEquals(to_snake_case('ALongString'), 'a_long_string')
        self.assertEquals(to_snake_case('ALongSTRING'), 'a_long_string')

    def test_to_camel_case(self):
        self.assertEquals(to_camel_case('alongstring'), 'alongstring')
        self.assertEquals(to_camel_case('aLongString'), 'aLongString')
        self.assertEquals(to_camel_case('ALongString'), 'ALongString')
        self.assertEquals(to_camel_case('a_long_string'), 'aLongString')

    def test_dict_to_other_case(self):
        self.assertDictEqual(dict_to_snake_case({}), {})
        self.assertDictEqual(dict_to_snake_case({'a': 1}), {'a': 1})
        self.assertDictEqual(dict_to_camel_case({}), {})
        self.assertDictEqual(dict_to_camel_case({'a': 1}), {'a': 1})
        input = {
            'name': 'Marcus',
            'petName': 'Le Chat',
            'otherPetName': 'Le Chat2'
        }
        output = {
            'name': 'Marcus',
            'pet_name': 'Le Chat',
            'other_pet_name': 'Le Chat2'
        }
        self.assertDictEqual(dict_to_snake_case(input), output)
        self.assertDictEqual(dict_to_camel_case(output), input)

    def test_format_object(self):
        self.assertDictEqual(
            format_object({'id': 1, 'created_at': 'Monday'},
                          visible=['id', 'createdAt']),
            {'object': {'id': 1, 'createdAt': 'Monday'}}
        )
