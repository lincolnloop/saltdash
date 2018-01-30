from django.test import TestCase

from saltdash.dash.models import Job

class ModelTestCase(TestCase):

    def test_list_targets_not_list(self):
        # lxc.list returns non-list results of type 'list' :(
        job = Job(load={'tgt': 'minion', 'tgt_type': 'list'})
        self.assertListEqual(job.targets, ['minion'])

    def test_list_targets(self):
        job = Job(load={'tgt': ['minion1', 'minion2'], 'tgt_type': 'list'})
        self.assertListEqual(job.targets, ['minion1', 'minion2'])

    def test_glob_targets(self):
        job = Job(load={'tgt': 'minion*', 'tgt_type': 'glob'})
        self.assertListEqual(job.targets, ['minion*'])
