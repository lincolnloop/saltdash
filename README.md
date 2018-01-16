# Salt Dash

(aka, A Dash of Salt)

Read-only web interface to read from Salt's [external job cache]() using the  [`pgjsonb`]() returner.


## Running Locally

Install [Yarn](https://yarnpkg.com/lang/en/docs/install/) for building the front-end.

Install [Pipenv](https://docs.pipenv.org/) for the back-end.

```bash
(cd client; yarn)
pipenv --three install --dev
cp saltdash/settings/local.py.example saltdash/settings/local.py
pipenv shell
saltdash migrate
saltdash runserver
```

## Client-side Development

Currently using [parcel](https://parceljs.org/). To start a development environment with live reloading, run:

```bash
cd client
npm run watch:css
# in another shell
npm run watch:js
```

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
