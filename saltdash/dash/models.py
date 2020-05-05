import fnmatch
import json

from django.conf import settings
from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.functional import cached_property


class Job(models.Model):
    jid = models.CharField(verbose_name="job id", max_length=50, primary_key=True)
    load = JSONField()

    class Meta:
        db_table = "jids"
        ordering = ["-jid"]

    @cached_property
    def user(self):
        return self.load.get("user", None)

    @cached_property
    def args(self):
        return [a for a in self.load["arg"] if isinstance(a, str)]

    @cached_property
    def kwargs(self):
        for a in self.load["arg"]:
            if isinstance(a, dict) and a.get("__kwarg__"):
                del (a["__kwarg__"])
                return a

    @property
    def saltreturn_set(self):
        # Fake foreign key relation
        return Result.objects.filter(jid=self.jid)

    @cached_property
    def successes(self):
        return self.saltreturn_set.successes().count()

    @cached_property
    def failures(self):
        return self.saltreturn_set.failures().count()

    @cached_property
    def completed(self):
        try:
            return self.saltreturn_set.all().order_by("-completed")[0].completed
        except IndexError:
            return None

    @property
    def targets(self) -> list:
        try:
            tgt = self.load["tgt"]
        except KeyError:
            tgt = self.load["id"]
        if "tgt_type" in self.load and self.load["tgt_type"] == "list" and not isinstance(tgt, str):
            return tgt
        return [tgt]

    def __str__(self) -> str:
        fun = self.load["fun"]
        target_count = len(self.targets)
        if target_count > 10:
            targets = "{} targets".format(target_count)
        else:
            targets = ", ".join(self.targets)
        val = "{}: salt '{}' {}".format(self.jid, targets, fun)
        if self.user:
            val += " by {}".format(self.user)
        return val


class ResultQuerySet(models.QuerySet):
    def successes(self):
        return self.filter(
            Q(full_ret__contains={"retcode": 0})
            | Q(return_val__contains={"success": True})
        )

    def failures(self):
        return self.exclude(
            Q(full_ret__contains={"retcode": 0})
            | Q(return_val__contains={"success": True})
        )


class Result(models.Model):
    auto_id = models.AutoField(primary_key=True)
    minion = models.CharField(max_length=100, db_index=True, db_column="id")
    # This can't be a foreign key due to the order Salt might insert data into
    # the tables.
    jid = models.CharField(verbose_name="job id", max_length=50, db_index=True)
    fun = models.CharField("function", max_length=100)
    fun_args = ArrayField(
        models.CharField(max_length=255), verbose_name="function args", null=True
    )
    completed = models.DateTimeField(db_column="alter_time")
    full_ret = JSONField("full result")
    return_val = JSONField("result", db_column="return")
    success = models.BooleanField()

    objects = ResultQuerySet.as_manager()

    class Meta:
        db_table = "salt_returns"
        ordering = ["-completed"]

    def __str__(self):
        return "{}: {} on {}".format(self.jid, self.fun, self.minion)

    def get_absolute_url(self):
        return reverse("dash:result_detail", args=[self.jid, self.minion])

    @property
    def was_success(self):
        if "retcode" in self.full_ret:
            return self.full_ret["retcode"] == 0
        # Master results don't use retcode
        try:
            return self.return_val.get("success", False)
        except AttributeError:
            return False

    @cached_property
    def job(self) -> Job:
        try:
            return Job.objects.get(jid=self.jid)
        except Job.DoesNotExist:
            return Job(
                jid=self.full_ret["jid"],
                load={
                    "arg": self.full_ret.get("fun_args", []),
                    "fun": self.full_ret["fun"],
                    "jid": self.full_ret["jid"],
                    "tgt": [self.full_ret["id"]],
                    "user": self.full_ret["user"],
                    "tgt_type": "list",
                },
            )

    @cached_property
    def return_val_as_json(self) -> str:
        return json.dumps(self.return_val, indent=2)

    @property
    def result_type(self) -> str:
        for hidden in settings.HIDE_OUTPUT:
            if fnmatch.fnmatch(self.full_ret.get("fun", ""), hidden):
                return "hidden"
        if isinstance(self.return_val, dict):
            if self.return_val.get("fun") == "runner.state.orchestrate":
                return "orchestrate"
            try:
                list(self.return_val.values())[0]["__run_num__"]
                return "state"
            except (TypeError, IndexError, KeyError):
                return "json"
        return "text"

    @property
    def has_states(self) -> bool:
        return self.result_type in ["state", "orchestrate"]

    def states_with_status(self, status: str) -> int:
        return len([s for s in self.states if s["status"] == status])

    @cached_property
    def states_changed(self) -> int:
        return self.states_with_status("changed")

    @cached_property
    def states_failed(self) -> int:
        return self.states_with_status("failed")

    @cached_property
    def states_failed_requisite(self) -> int:
        return self.states_with_status("requisite-failed")

    @cached_property
    def states_unchanged(self) -> int:
        return self.states_with_status("unchanged")

    @cached_property
    def states(self) -> list:
        if self.result_type == "state":
            state_dict = self.return_val
        elif self.result_type == "orchestrate":
            state_dict = list(self.return_val["return"]["data"].values())[0]
        else:
            raise TypeError("Return must be for a state")
        sorted_run = sorted(state_dict.items(), key=lambda s: s[1]["__run_num__"])
        return [_convert_state(*args) for args in sorted_run]

    @cached_property
    def duration(self) -> float:
        return sum([s["duration"] for s in self.states])


def _convert_state(key: str, data: dict) -> dict:
    """Make state data more usable"""
    mod, id, name, fun = key.split("_|-")
    state = {
        "module": mod,
        "id": id,
        "function": fun,
        "name": name,
        "success": data["result"],
        "changed": bool(data["changes"]),
        "sls": data.get("__sls__"),
        "changes": data["changes"],
        "duration": data.get("duration", 0),
        "start_time": data.get("start_time"),
        "comment": data.get("comment", ""),
        "order": data["__run_num__"],
        "jid": data.get("__jid__"),
    }
    if not state["success"]:
        if state["comment"].startswith("One or more requisite failed:"):
            state["status"] = "requisite-failed"
        else:
            state["status"] = "failed"
    elif state["changed"]:
        state["status"] = "changed"
    else:
        state["status"] = "unchanged"
    return state
