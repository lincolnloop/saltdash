from unittest import TestCase

from ..models import Result, _convert_state


class StateTestCase(TestCase):

    def test_requisite_state(self):
        key = "service_|-saltdash_uwsgi_|-saltdash_uwsgi_|-running"
        state_raw = {
                "result": False,
                "__sls__": "projects.saltdash",
                "changes": {},
                "comment": ("One or more requisite failed: "
                            "projects.saltdash.update saltdash .env, "
                            "projects.saltdash.saltdash_ready"),
                "__run_num__": 226,
        }
        state = _convert_state(key, state_raw)
        self.assertEqual(state['status'], 'requisite-failed')
        self.assertFalse(state['success'])

    def test_counts(self):
        states_raw = {
            "service_|-saltdash_uwsgi_|-saltdash_uwsgi_|-running": {
                "result": False,
                "__sls__": "projects.saltdash",
                "changes": {},
                "comment": ("One or more requisite failed: "
                            "projects.saltdash.update saltdash .env, "
                            "projects.saltdash.saltdash_ready"),
                "__run_num__": 226,
            }
        }
        result = Result(return_val=states_raw)
        self.assertEqual(len(result.states), 1)
        self.assertEqual(result.states_failed_requisite, 1)
        self.assertEqual(result.states_failed, 0)

    def test_state_ordering(self):
        states_raw = {
            "pkg_|-graphite_api_install_|-python-dev_|-installed": {
                "name": "python-dev",
                "__id__": "graphite_api_install",
                "result": True,
                "__sls__": "packages.graphite.api",
                "changes": {},
                "comment": "All specified packages are already installed",
                "duration": 12.633, "start_time": "07:20:17.316386",
                "__run_num__": 167
            },
            "service_|-saltdash_uwsgi_|-saltdash_uwsgi_|-running": {
                "result": False,
                "__sls__": "projects.saltdash", "changes": {},
                "comment": "One or more requisite failed: projects.saltdash.update saltdash .env, projects.saltdash.saltdash_ready",
                "__run_num__": 226
            },
            "file_|-/var/lib/sentry_|-/var/lib/sentry_|-directory": {
                "name": "/var/lib/sentry", "__id__": "/var/lib/sentry",
                "result": True,
                "__sls__": "docker.sentry",
                "changes": {},
                "comment": "Directory /var/lib/sentry is in the correct state\nDirectory /var/lib/sentry updated",
                "duration": 1.473,
                "pchanges": {},
                "start_time": "07:20:07.085770",
                "__run_num__": 137
            }
            ,
            "file_|-/var/log/backup_|-/var/log/backup_|-directory": {
                "name": "/var/log/backup", "__id__": "/var/log/backup",
                "result": True,
                "__sls__": "lincolnloop.backup_to_s3",
                "changes": {},
                "comment": "Directory /var/log/backup is in the correct state\nDirectory /var/log/backup updated",
                "duration": 2.237,
                "pchanges": {},
                "start_time": "07:19:53.316698",
                "__run_num__": 81
            }
        }
        result = Result(return_val=states_raw)
        self.assertListEqual([s['order'] for s in result.states],
                             [81, 137, 167, 226])
