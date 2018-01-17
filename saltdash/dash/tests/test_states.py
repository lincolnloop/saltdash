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
