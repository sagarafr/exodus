import unittest

from ...models.persons import Person


class TestPerson(unittest.TestCase):

    def test_create_person(self):
        d = {'name': 'Raoul', 'age': 30}
        raoul = Person(**d)
        raoul.check_integrity()
        self.assertEquals(raoul.name, d['name'])
        self.assertEquals(raoul.age, d['age'])

    def test_create_wrong_person(self):
        with self.assertRaises(ValueError):
            Person(name='Raoul', age=-1).check_integrity()
        with self.assertRaises(ValueError):
            Person(name='Raoul', age=500).check_integrity()
        with self.assertRaises(ValueError):
            Person(age=500).check_integrity()
        with self.assertRaises(ValueError):
            Person(name='Raoul').check_integrity()
        with self.assertRaises(ValueError):
            Person(name=None, age=30).check_integrity()
        with self.assertRaises(ValueError):
            Person(name='Raoul', age='30').check_integrity()
        with self.assertRaises(TypeError):
            Person(name='Raoul', age=30, plop='coucou')

    def test_increase_age(self):
        raoul = Person(**{'name': 'Raoul', 'age': 30})
        raoul.increase_age()
        self.assertEquals(raoul.age, 31)

    def test_repr(self):
        raoul = Person(**{'name': 'Raoul', 'age': 30})
        self.assertEqual(repr(raoul), '<Person name=Raoul, age=30>')
