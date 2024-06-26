"""
Module for managing logrotate.

.. versionadded:: 2017.7.0

"""

_DEFAULT_CONF = "/etc/logrotate.conf"

# Define the module's virtual name
__virtualname__ = "logrotate"

# Define a function alias in order not to shadow built-in's
__func_alias__ = {"set_": "set"}


def __virtual__():
    """
    Load only on minions that have the logrotate module.
    """
    if "logrotate.show_conf" in __salt__:
        return __virtualname__
    return (False, "logrotate module could not be loaded")


def _convert_if_int(value):
    """
    Convert to an int if necessary.

    :param str value: The value to check/convert.

    :return: The converted or passed value.
    :rtype: bool|int|str
    """
    try:
        value = int(str(value))
    except ValueError:
        pass
    return value


def set_(name, key, value, setting=None, conf_file=_DEFAULT_CONF):
    """
    Set a new value for a specific configuration line.

    :param str key: The command or block to configure.
    :param str value: The command value or command of the block specified by the key parameter.
    :param str setting: The command value for the command specified by the value parameter.
    :param str conf_file: The logrotate configuration file.

    Example of usage with only the required arguments:

    .. code-block:: yaml

        logrotate-rotate:
          logrotate.set:
            - key: rotate
            - value: 2

    Example of usage specifying all available arguments:

    .. code-block:: yaml

        logrotate-wtmp-rotate:
          logrotate.set:
            - key: /var/log/wtmp
            - value: rotate
            - setting: 2
            - conf_file: /etc/logrotate.conf
    """
    ret = {"name": name, "changes": dict(), "comment": "", "result": None}

    try:
        if setting is None:
            current_value = __salt__["logrotate.get"](key=key, conf_file=conf_file)
        else:
            current_value = __salt__["logrotate.get"](
                key=key, value=value, conf_file=conf_file
            )
    except (AttributeError, KeyError):
        current_value = False

    if setting is None:
        value = _convert_if_int(value)

        if current_value == value:
            ret["comment"] = f"Command '{key}' already has value: {value}"
            ret["result"] = True
        elif __opts__["test"]:
            ret["comment"] = f"Command '{key}' will be set to value: {value}"
            ret["changes"] = {"old": current_value, "new": value}
        else:
            ret["changes"] = {"old": current_value, "new": value}
            ret["result"] = __salt__["logrotate.set"](
                key=key, value=value, conf_file=conf_file
            )
            if ret["result"]:
                ret["comment"] = f"Set command '{key}' value: {value}"
            else:
                ret["comment"] = "Unable to set command '{}' value: {}".format(
                    key, value
                )
        return ret

    setting = _convert_if_int(setting)

    if current_value == setting:
        ret["comment"] = "Block '{}' command '{}' already has value: {}".format(
            key, value, setting
        )
        ret["result"] = True
    elif __opts__["test"]:
        ret["comment"] = "Block '{}' command '{}' will be set to value: {}".format(
            key, value, setting
        )
        ret["changes"] = {"old": current_value, "new": setting}
    else:
        ret["changes"] = {"old": current_value, "new": setting}
        ret["result"] = __salt__["logrotate.set"](
            key=key, value=value, setting=setting, conf_file=conf_file
        )
        if ret["result"]:
            ret["comment"] = "Set block '{}' command '{}' value: {}".format(
                key, value, setting
            )
        else:
            ret["comment"] = "Unable to set block '{}' command '{}' value: {}".format(
                key, value, setting
            )
    return ret
