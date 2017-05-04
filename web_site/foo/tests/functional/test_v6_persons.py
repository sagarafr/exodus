import json

from web_site.foo.tests.functional import FunctionalTest


class PersonsTest(FunctionalTest):

    def assertPersonIsValid(self, original, data):
        for attribute in 'id', 'createdAt', 'updatedAt':
            self.assertIn(attribute, data)
        for attribute in original.keys():
            self.assertIn(attribute, data)
            self.assertEquals(original[attribute], data[attribute])

    def test_post_person(self):
        person = {'name': 'Raoul', 'age': 30}

        # Create the person
        response = self.client.post('/v6/person', data=json.dumps(person))
        self.assert_200(response)
        self.assertPersonIsValid(person, response.json)
        person_id = response.json['id']

        # Get the person by id
        response = self.client.get('/v6/person/' + person_id)
        self.assert_200(response)
        self.assertPersonIsValid(person, response.json)

    def test_post_bad_person(self):
        data = (
            {'age': 30},
            {'name': 'Raoul', 'age': 30, 'foo': 'bar'},
            {}, 42, 'foo'
        )
        for person in data:
            response = self.client.post('/v6/person', data=json.dumps(person))
            self.assert_400(response)

    def test_post_person_with_same_name(self):
        person = {'name': 'Raoul', 'age': 30}
        response = self.client.post('/v6/person', data=json.dumps(person))
        self.assert_200(response)
        response = self.client.post('/v6/person', data=json.dumps(person))
        self.assert_200(response)

    def test_update_person(self):
        person = {'name': 'Raoul', 'age': 30}

        # Create the person
        response = self.client.post('/v6/person', data=json.dumps(person))
        person_id = response.json['id']

        # Update person
        response = self.client.put('/v6/person/' + person_id,
                                   data=json.dumps({'age': 35}))
        self.assert_200(response)
        person['age'] = 35
        self.assertPersonIsValid(person, response.json)

    def test_update_person_bad_data(self):
        person = {'name': 'Raoul', 'age': 30}

        # Create the person
        response = self.client.post('/v6/person', data=json.dumps(person))
        person_id = response.json['id']

        # Update person
        data = (
            {'age': '30'},
            {'name': 'Raoul', 'age': 30, 'foo': 'bar'},
            42, 'foo', None
        )
        for person in data:
            response = self.client.put('/v6/person/' + person_id,
                                       data=json.dumps(person))
            print(person)
            self.assert_400(response)

    def test_add_one_year(self):
        person = {'name': 'Raoul', 'age': 30}
        response = self.client.post('/v6/person', data=json.dumps(person))
        self.assert_200(response)
        person_id = response.json['id']

        # Schedule an async task
        response = self.client.post('/v6/person/%s/getOlder' % person_id)
        self.assert_200(response)

        response = self.client.get('/v6/person/' + person_id)
        self.assert_200(response)
        person['age'] = 31
        self.assertPersonIsValid(person, response.json)

    def test_add_two_year(self):
        person = {'name': 'Raoul', 'age': 30}
        response = self.client.post('/v6/person', data=json.dumps(person))
        self.assert_200(response)
        person_id = response.json['id']

        # Schedule an async task
        response = self.client.post('/v6/person/%s/getOlder2' % person_id)
        self.assert_200(response)

        response = self.client.get('/v6/person/' + person_id)
        self.assert_200(response)
        person['age'] = 32
        self.assertPersonIsValid(person, response.json)
