import datetime
import logging

from celery import group

from ..extensions import cel, db
from ..models.persons import Person
from ..logs import TaskLoggerAdapter

logger = TaskLoggerAdapter(logging.getLogger('celery.task'), dict())


@cel.task(bind=True, name='ADD_ONE_YEAR')
def add_one_year(self, person_id):
    logger.info('Adding one year to {}'.format(person_id), task=self)
    person = Person.query.with_lockmode('update').get(person_id)
    person.increase_age()
    db.session.add(person)
    db.session.commit()


@cel.task(bind=True, ignore_result=True, name='ADD_ONE_YEAR_TO_EVERYONE')
def add_one_year_to_everyone(self):
    logger.info('Scheduling tasks to add one year to everyone', task=self)
    persons = Person.query.all()
    group(
        add_one_year.s(person.id)
        for person in persons
    )()


cel.conf.CELERYBEAT_SCHEDULE.update({
    'add_one_year_to_everyone': {
        'task': 'ADD_ONE_YEAR_TO_EVERYONE',
        'schedule': datetime.timedelta(seconds=5),
        'args': ()
    }
})
