"""
The logging module defines functions that are used for the logging of the
pipeline steps.
"""
import logging
import sys
from pprint import pformat

LOG = logging.getLogger(__name__)


# pylint: disable=unused-argument,keyword-arg-before-vararg
def logging_pipeline_step(level, log_message, **local_vars):
    """
    This function logs an info or error level message with the information of the pipeline step.
    If the logLevel setting is in DEBUG mode then it logs all the arguments passed to the step, if not
    it will only show the name of the step, user, backend name, redirect_uri and a custom message.

    For example:
        To set the verbosity level to DEBUG add the setting:

        "BACKEND_OPTIONS": { "logLevel":"DEBUG" }

    Arguments:
        - level: This is used to describe the severity of the message that the django logger will handle.
                If "error" is passed, then an ERROR level logging message will be displayed. Otherwise,
                an INFO log will be displayed.
        - log_message: Custom message to be shown in the log.
        - local_vars: local variables, this must always be passed as **locals().
    """
    extra_info = {}
    user = local_vars.get("user")
    backend = local_vars.get("backend")

    message = "PIPELINE-STEP:{step} - USER:{user} - BACKEND:{backend_name} - REDIRECT_URI:{uri} - MESSAGE:{msg}".format(
        step=sys._getframe(1).f_code.co_name,  # pylint: disable=protected-access
        user=user,
        backend_name=getattr(backend, "name", ""),
        uri=getattr(backend, "redirect_uri", ""),
        msg=log_message,
    )

    if backend and backend.setting("BACKEND_OPTIONS", {}).get("logLevel", "").lower() == "debug":
        details = local_vars.get("details")
        args = local_vars.get("args", [])
        kwargs = local_vars.get("kwargs", {})
        response = kwargs.pop("response", None)
        # We do not want to show the id_token in the logs
        if response:
            response.pop("id_token", None)

        extra_info["details"] = pformat(details)
        extra_info["pipeline_step_args"] = pformat(args)
        extra_info["request"] = pformat(kwargs.pop("request", None))
        extra_info["response"] = pformat(response)
        extra_info["kwargs"] = pformat(kwargs)

    if level.lower() == "error":
        LOG.exception(message, extra=extra_info)
    else:
        LOG.info(message, extra=extra_info)
