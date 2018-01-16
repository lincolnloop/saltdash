import json

from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField
from django.urls import reverse
from django.utils.functional import cached_property


class Job(models.Model):
    jid = models.CharField(verbose_name="job id", max_length=50, primary_key=True)
    load = JSONField()

    class Meta:
        db_table = 'jids'
        ordering = ['-jid']

    @cached_property
    def target_count(self):
        return len(self.load['tgt'])

    @cached_property
    def user(self):
        return self.load.get('user', None)

    @cached_property
    def args(self):
        return [a for a in self.load['arg'] if isinstance(a, str)]

    @cached_property
    def kwargs(self):
        for a in self.load['arg']:
            if isinstance(a, dict) and a.get('__kwarg__'):
                del(a['__kwarg__'])
                return a

    @property
    def saltreturn_set(self):
        # Fake foreign key relation
        return Result.objects.filter(jid=self.jid)

    @cached_property
    def successes(self):
        return self.saltreturn_set.filter(success=True).count()

    @cached_property
    def failures(self):
        return self.saltreturn_set.filter(success=False).count()

    @cached_property
    def completed(self):
        try:
            return self.saltreturn_set.all().order_by('-completed')[0].completed
        except IndexError:
            return None

    def __str__(self):
        fun = self.load['fun']
        if self.load['tgt_type'] == 'list':
            if self.target_count > 10:
                targets = f'{self.target_count} targets'
            else:
                targets = ', '.join(self.load['tgt'])
        else:
            targets = self.load['tgt']
        val = f"{self.jid}: salt '{targets}' {fun}"
        if self.user:
            val += f" by {self.user}"
        return val


class Result(models.Model):
    auto_id = models.AutoField(primary_key=True)
    minion = models.CharField(max_length=100, db_index=True, db_column='id')
    # This can't be a foreign key due to the order Salt might insert data into
    # the tables.
    jid = models.CharField(verbose_name="job id", max_length=50, db_index=True)
    fun = models.CharField("function", max_length=100)
    fun_args = ArrayField(models.CharField(max_length=255),
                          verbose_name="function args",
                          null=True)
    completed = models.DateTimeField(db_column='alter_time')
    full_ret = JSONField("full result")
    return_val = JSONField("result", db_column='return')
    success = models.BooleanField()

    class Meta:
        db_table = 'salt_returns'
        ordering = ['-completed']

    def __str__(self):
        return f'{self.jid}: {self.fun} on {self.minion}'

    def get_absolute_url(self):
        return reverse('dash:return_detail', args=[self.pk])

    @cached_property
    def job(self):
        try:
            return Job.objects.get(jid=self.jid)
        except Job.DoesNotExist:
            return Job(jid=self.full_ret['jid'],
                       load={"arg": self.full_ret.get('fun_args', []),
                             "fun": self.full_ret['fun'],
                             "jid": self.full_ret['jid'],
                             "tgt": [self.full_ret['id']],
                             "user": self.full_ret['user'],
                             "tgt_type": "list"})

    @cached_property
    def return_val_as_json(self):
        return json.dumps(self.return_val, indent=2)

    @property
    def result_type(self):
        if isinstance(self.return_val, dict):
            try:
                __ = list(self.return_val.values())[0]['__sls__']
                return 'state'
            except (TypeError, IndexError, KeyError):
                return 'json'
        return 'text'

    @property
    def is_state(self):
        return self.result_type == 'state'

    def states_with_status(self, status):
        return len([s for s in self.states if s['status'] == status])

    @cached_property
    def states_changed(self):
        return self.states_with_status('changed')

    @cached_property
    def states_failed(self):
        return self.states_with_status('failed')

    @cached_property
    def states_failed_requisite(self):
        return self.states_with_status('failed-requisite')

    @cached_property
    def states_unchanged(self):
        return self.states_with_status('unchanged')

    @cached_property
    def states(self):
        if self.result_type != 'state':
            raise TypeError("Return must be for a state")
        return [_convert_state(*args) for args in self.return_val.items()]

    @cached_property
    def duration(self):
        return sum([s['duration'] for s in self.states])


def _convert_state(key, data):
    """Make state data more usable"""
    mod, id, name, fun = key.split('_|-')
    state = {
        'module': mod,
        'id': id,
        'function': fun,
        'name': name,
        'success': data['result'],
        'changed': bool(data['changes']),
        'sls': data['__sls__'],
        'changes': data['changes'],
        'duration': data.get('duration', 0),
        'start_time': data.get('start_time'),
        'comment': data.get('comment', ''),
    }
    if not state['success']:
        if state['comment'].startswith('One or more requisite failed:'):
            state['status'] = 'requisite-failed'
        else:
            state['status'] = 'failed'
    elif state['changed']:
        state['status'] = 'changed'
    else:
        state['status'] = 'unchanged'
    return state
