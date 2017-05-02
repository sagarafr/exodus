Python 2i starter
=================

This repository contains a template of 2i that helps starting a new project 
quickly. It features:

* Versioned REST APIs with Flask
* Database access through SQLAlchemy ORM
* Database version and migration with Alembic
* Asynchronous robots with Celery
* Non-blocking logs for Thot, stdout, syslog and local file
* Exception monitoring with Sentry
* Unit and functional tests
* Environments prod, dev and test
* Documentation generated in code
* Local commands
* Docker ready

Why use this starter instead of using home made code?

While bootstrapping a simple project with Flask is easy enough, things get 
trickier when multiple components (Flask, Celery, SQLAlchemy, Thot, Docker...)
have to work together. It took us a few iterations to get things right. With 
this starter you benefit from a decent base which encourages good practices to 
start your work.

How to start developing
-----------------------

To start developing you need:

* A Python 3 interpreter with pip and virtualenv
* Access to a redis
* Access to a Postgres

The project uses Python 3.5 but should be compatible with every Python 3. 
You are highly encouraged to compile the latest version of Python and use a 
virtualenv.

Install the dependencies in your virtualenv:

    $ pip install -r requirements/dev.txt

Create a configuration file `config-dev.yml` for your dev environment:

    ---
    SQLALCHEMY_DATABASE_URI: postgresql://user:pass@host/database
    CELERY_CONF:
        BROKER_URL: redis://localhost/1
        CELERY_RESULT_BACKEND: redis://localhost/2

Tell your shell you want to use the dev environment:

    $ export APP_ENV=dev
    $ export APP_CONFIG=config-dev.yml

Push the schema into the database using Alembic:

    $ python main.py db upgrade

Start the development server:

    $ python main.py runserver

Call the API:

    $ curl -X GET localhost:5000/v1/persons
    {
        "objects": [],
        "next": null,
        "prev": null
    }

Architecture
------------

The application uses a kind of MVC. When a request arrives it hits a 
view which deserializes user data. The view asks the controller to perform an 
action, the controller does it by querying models and pass the result back 
to the view. The view formats the output correctly according to API scheme 
and sent it serialized to the user.

    views <--> controllers <--> models

This abstraction allows to decouple each component from the others. For 
instance a version 2 of the API would reuse the controllers.

### Views

#### Blueprints

The API is versioned with [Flask blueprints](http://flask.pocoo.org/docs/0.10/blueprints/)
. This simple example contains three blueprints:

* `foo/main` attached to `/`. It contains the common error routes.
* `foo/apiv1` attached to `/v1/`. It contains the routes of the API v1.
* `foo/doc` attached to `/doc/`. It contains the HTML documentation.

These blueprints are registered in `create_app` in `foo/__init__.py`.

The API v1 follows the REST conventions described in [REST API Guidelines]
(https://interne.ovh.net/confluence/display/services/REST+API+guidelines).

#### Routes

Some example of [Flask API routes](http://flask.pocoo.org/docs/0.10/quickstart/#routing)
are defined in `foo/apiv1/person.py`. Routes should be kept minimal, most 
of the logic should go in controllers as it eases a lot the testing process 
and leads to clearer code.

Basically routes should validate the user's input, format it (JSON to dict),
pass it to the controller and format it back (dict to JSON).

As routes are bound to a blueprint, they are defined in the blueprint 
object, here `api`, unlike most Flask example in the wild using `app`:

    @api.route('/persons')
    def get_persons():
        return jsonify(list_with_pagination('.get_persons', PersonController))

Routes can be deprecated using the `@deprecated` decorator. This will add a 
header `X-Deprecated` to every response on the route. Thanks to that users 
can be warned in advance that a route is about to be removed. Obviously this
is only useful if this feature is advertised properly in the documentation 
of the service and implemented in SDKs.

### Controllers

Controllers are defined in `foo/controllers`. They wrap as much logic as 
possible so they can be reused between multiple API versions.

### Models

Models handle the storage of the application. A model is represented by a 
class which inherits from `BaseModel`. This allows to register the model to the 
ORM.

The ORM used is SQLAlchemy ORM. We use it trough a thin wrapper called 
Flask-SQLAlchemy which handled connection pools and session in the request 
context. Helpful documentation:

* [Flask-SQLAlchemy](https://pythonhosted.org/Flask-SQLAlchemy)
* [SQLAlchemy ORM](http://docs.sqlalchemy.org/en/rel_1_0/orm/index.html)

#### Database migrations

During the lifetime of an application, its database schema often evolves. An
extension of SQLAlchemy called Alembic allows to handle upgrades and 
downgrades of databases schemes seamlessly.

Migrations files are located in the `migrations/versions` directory.

After altering models, you can create a new revision with:

    $ python main.py db migrate -m "Comment of the revision"

Carefully check the new migration file in `migrations/versions` as Alembic 
does not notice every change you make to models, see [Auto Generating 
Migrations](https://alembic.readthedocs.org/en/latest/autogenerate.html).

After checking and adapting the revision you can upgrade your database:

    $ python main.py db upgrade

Migrations should be included in git and reviewed like any other code.

### Tasks

Asynchronous tasks using Celery allow to separate long running jobs from the
normal flow of API requests. Tasks are usually scheduled by either:

* An API request (usually POST/PUT/DELETE)
* A cron-like called Celery beat
* Another task

The most common way to schedule a task is to call the `delay` method on it:

    from ..tasks.persons import add_one_year
    add_one_year.delay(person.name)

This will add a task in the broker, here redis, and notify a Celery worker 
that a task is pending. A frequent pattern is to give an argument to the 
task, for instance the id of a object in the database. When the task is 
launched, it fetches this object from the database, starts a long running job
on it and saves the result back into the database. Tasks are located at 
`foo/tasks`.
 
Controllers have two methods to launch tasks. `schedule_task` and 
`schedule_chain`, they wrap the calls to `task.delay()` and save in database 
information about the task(s) so the user can query the API for their progress.

Celery has many ways to define complex [interactions between tasks]
(http://celery.readthedocs.org/en/latest/userguide/canvas.html).

As a rule of thumbs, if your API has to call other APIs, you should probably
wrap this call into a tasks. You will be able to retry the call in case 
of network problem and your API reactivity will be highly improved. 

#### Retrying tasks

If an exception is raised while processing a task, the task will be retried 
automatically up to three times by default.

If you need to retry more you can pass an argument to the celery decorator:

    @cel.task(bind=True, name='WAIT_FOR_SERVERS', max_retries=20)
    def wait_for_servers(self, cluster_id):
        pass

Retries follow a backoff algorithm. The more a task is retried, the longer 
the delay between each subsequent retry is.

Sometimes you are sure that a task should not be retried because the error 
is unrecoverable. You can then raise the exception `UnrecoverableError` 
defined in `foo.tasks` to definitely stop the task.

You can read [Celery best
practices](https://blog.balthazar-rouberol.com/celery-best-practices) for 
hints on how to write maintainable and error resistant tasks.

#### Launching Celery

Tasks are not processed by the same Python interpreter as the API. You must 
launch another service called `celery worker`.

Run Celery worker with:

    APP_ENV=dev APP_CONFIG=config-dev.yml celery worker -A celery_launch.cel

To get cron-like support for Celery you must also launch a **unique** 
instance of `celery beat`.

Run Celery beat with:

    APP_ENV=dev APP_CONFIG=config-dev.yml celery beat -A celery_launch.cel

### Logs

When Flask runs in debug mode (in dev and testing environments) logs are 
simply printed to stdout.

In the production environment logger is configured with information from the
config file. Available log handlers are:

* stdout
* file
* syslog
* Thot

By default, Python handlers are blocking. This can slow down your 
application if the log backend is not available. The `async` option allows 
to enable queueing of logs for a specific handler, removing the blocking issue.

A few examples of logger configuration are available in `config-example.yml`.
In production stdout and Thot are recommended.

Each response from the API comes with a header 'X-Request-Id' containing a 
unique id that is available in each log generated by the request. It can 
help the run team to trace a customer issue with the API.

### Tests

Tests are located in `foo/tests`. To run functional tests you need an instance
of Postgres (docker is a good fit for that). Tables will be 
automatically created and wiped between each test. Create a `config-test
.yml` file containing:

    ---
    SQLALCHEMY_DATABASE_URI: postgresql://user:pass@server/db

Run them with:

    $ APP_ENV=test APP_CONFIG=config-test.yml nosetests foo/tests/

#### Unit tests

Unit tests are located in `foo/tests/unit`. These tests work mostly on 
models and should test only a single feature at a time (thus unit).

Unit testing controllers can be done by mocking calls to models. See the 
documentation on [Python mock](https://docs.python.org/3/library/unittest.mock.html).

#### Functional tests

Functional tests are located in `foo/tests/functional`. These tests
act like an external user requesting through the API. Automation of this 
process is done with Flask-Testing.

Functional tests allow to test the application as a whole, testing API, 
models and tasks at the same time. 

Tasks tested with functional tests run in [EAGER
mode](http://docs.celeryproject.org/en/latest/configuration.html#celery-always-eager) which is the 
synchronous mode of Celery where the API and Celery worker share the same 
Python interpreter. Because of that a minor differences exist between the 
testing setup and the normal one, mainly related to SQLALchemy sessions and 
Celery signals, but this should not be a problem.

#### Monitoring

The `/mon/ping` route is exposed to enable external systems to check if the API is up and running.
You can add more monitoring routes to the `foo/main/monitoring.py` file, to monitor your DB access,
data consistancy, etc.

### Documentation

Sphinx is used to provide helpful documentation to final users about the 
service.

Sphinx allows to embed documentation is the source code of the project. 
Routes from API are automatically detected and other static pages with 
general information can be added in `doc/source`.

Documentation can be generated as HTML using:

    $ make --directory=doc html
    # Generates the documentation in doc/build/html/
    $ rm -rf foo/doc/doc_files/
    $ cp -r doc/build/html/. foo/doc/doc_files/
    # Deploys the documentation, as this directory is the one served by /doc

HTML output is located in `doc/build/html/index.html`, then copied to
foo/doc/doc_files/ from where they will be served.

To always keep in sync published documentation and code running in 
production, documentation pages are served directly by the API server. When 
a user hits `http://domain/doc` he is shown the documentation of the service.

### Docker

A Dockerfile and an entrypoint script is provided. They allow to build a 
docker image for your application, keeping all the configuration outside of 
the image.

To achieve this a quite ugly hack is used: the content of the yaml config file
is placed as an environment variable. The entrypoint then converts this 
variable as a file in the working directory of the application in the 
container. Albeit ugly, this works very well for deploying to Sailabove.

Build the docker image:

    $ docker build --tag=foo .

Convert your config file as a one line environment variable:

    $ sed ':a;N;$!ba;s/\n/\\n/g' config.yml > config.env

Launch a Docker container acting as a Celery worker:

    $ docker run -ti --rm -e "CONF=`cat config.env`" foo celery_worker

Available commands are:

* `api` to run the API with Gunicorn
* `celery_worker` to run Celery worker
* `celery_beat` to run Celery beat
* `main` to run any command available through `python main.py`
