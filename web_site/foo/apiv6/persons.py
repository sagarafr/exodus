from . import api, single_object, get_payload
from ..controllers import PersonController
import json

VISIBLE = ['name', 'age', 'createdAt', 'updatedAt', 'id']

# You might notice that there is no 'GET /person' route here,
# the reason is that the APIv6 will generate this route for you
# (basically mapping a user to a list of services).


@api.route('/person/<id>', methods=['GET'])
def get_person(id):
    """Retrieve information about a person"""
    person = PersonController.get(id)
    print(person)
    print(single_object(person, VISIBLE))
    return single_object(person, VISIBLE)


@api.route('/list', methods=['GET'])
def get_list():
    person = PersonController.list(None)
    person = {str(cpt): single_object(person[cpt], VISIBLE)[0] for cpt in range(0, len(person))}
    return json.dumps(person), 200, {'Content-Type': 'application/json'}


@api.route('/person', methods=['POST'])
def post_person():
    """Create a new person"""
    payload = get_payload()
    print("here create")
    print("playload", payload)
    person = PersonController.create(payload)
    print("person", person)
    return single_object(person, VISIBLE, status_code=200)


@api.route('/person/<id>', methods=['PUT'],
           request_schema=('v6_person', 'person'),
           response_schema=('v6_person', 'person'))
def put_person(id):
    """Update a person"""
    payload = get_payload()
    print("here put_person")
    person = PersonController.update(id, payload)
    return single_object(person, VISIBLE, status_code=200)


@api.route('/person/<id>/getOlder', methods=['POST'])
def let_person_be_older(id):
    """Create a task to add one year to a person"""
    person, _ = PersonController.async_add_one_year(id)
    return ''


@api.route('/person/<id>/getOlder2', methods=['POST'])
def let_person_be_older2(id):
    """Create a task to add two year to a person"""
    person, _ = PersonController.async_add_two_year(id)
    return ''
