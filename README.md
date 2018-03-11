![Salt Dash logo](https://cldup.com/pjjyyptW69.png)

# Salt Dash

Read-only web interface to read from Salt's [external job cache](https://docs.saltstack.com/en/latest/topics/jobs/external_cache.html) using the  [`pgjsonb`](https://docs.saltstack.com/en/latest/ref/returners/all/salt.returners.pgjsonb.html) returner.

![screenshot](https://cldup.com/8TTHBPfhyu.png)


## Running Locally

Install [Yarn](https://yarnpkg.com/lang/en/docs/install/) for building the front-end.

Install [Pipenv](https://docs.pipenv.org/) for the back-end.

```bash
(cd client; yarn)
pipenv --three install --dev
$EDITOR .env  # if necessary
pipenv shell
saltdash migrate
saltdash runserver
```

## Client-side Development

Currently using [parcel](https://parceljs.org/). To start a development environment with live reloading, run:

```bash
cd client
yarn run watch
```

## Running in Production

`saltdash runserver` is not suitable for production. We recommend using `uWSGI` in production, but any production-level WSGI server (`gunicorn`, `waitress`, etc.) should work fine. A sample `uwsgi.ini` is provided in the repo. If Docker is more your speed, there's a `Dockerfile` as well.

Your environment should include the following variables:

### Required

* `SECRET_KEY`: a long random string you keep secret ([docs](https://docs.djangoproject.com/en/2.0/ref/settings/#secret-key))
* `DATABASE_URL`: `postgres://USER:PASSWORD@HOST:PORT/NAME`


### Optional

* `DEBUG`: `True` (never in production)
* `ALLOWED_HOSTS`: a comma-separated list of hosts allowed to serve the site ([docs](https://docs.djangoproject.com/en/2.0/ref/settings/#allowed-hosts))
* `GITHUB_TEAM_ID`: ID from the list provided by the `curl` command below
* `GITHUB_CLIENT_ID`: OAuth Client ID
* `GITHUB_CLIENT_SECRET`: OAuth Client Secret
* `SENTRY_DSN`: For error reporting to [Sentry](https://sentry.io)

GitHub Team authentication is included by setting the relevant `GITHUB_*` variables.

You'll need to setup an OAuth App at `https://github.com/organizations/<org>/settings/applications` with a callback URL in the form: `https://your-site.example.com/auth/complete/github-team/`

To retrieve your team IDs:

1. Create [a token at GitHub](https://github.com/settings/tokens)
2. `curl -H "Authorization: token <token>" https://api.github.com/orgs/<org>/teams`



## Setting up Salt

Once you've setup a Postgresql database using `saltdash migrate`, connect Salt's external job cache to the database by adding the following lines to `/etc/salt/master.d/job_cache.conf`:

```ini
# Replace items in brackets with actual values
master_job_cache: pgjsonb
returner.pgjsonb.host: [db-host]
returner.pgjsonb.pass: [db-password]
returner.pgjsonb.db: [db-database-name]
returner.pgjsonb.port: [db-port]
returner.pgjsonb.user: [db-user]
```

Restart your `salt-master` and all future jobs should get stored in the database.

If you have *lots* of jobs, you'll probably want to purge the cache periodically. A helper command is provided to do just that, run:

```bash
saltdash purge_job_cache [days_older_than_to_purge]
```

If you want to automate this, use the `--no-input` flag to bypass the confirmation prompt.

## Attributions

Icon by [BornSymbols](https://thenounproject.com/term/salt/705369) used under `CCBY` license.
