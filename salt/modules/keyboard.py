"""
Module for managing keyboards on supported POSIX-like systems using
systemd, or such as Redhat, Debian and Gentoo.
"""

import logging

import salt.utils.path

log = logging.getLogger(__name__)


def __virtual__():
    """
    Only works with systemd or on supported POSIX-like systems
    """
    if salt.utils.path.which("localectl") or __grains__["os_family"] in (
        "RedHat",
        "Debian",
        "Gentoo",
    ):
        return True
    return (
        False,
        "The keyboard exeuction module cannot be loaded: "
        "only works on Redhat, Debian or Gentoo systems or if localectl binary in"
        " path.",
    )


def get_sys():
    """
    Get current system keyboard setting

    CLI Example:

    .. code-block:: bash

        salt '*' keyboard.get_sys
    """
    cmd = ""
    if salt.utils.path.which("localectl"):
        cmd = 'localectl | grep Keymap | sed -e"s/: /=/" -e"s/^[ \t]*//"'
    elif "RedHat" in __grains__["os_family"]:
        cmd = 'grep LAYOUT /etc/sysconfig/keyboard | grep -vE "^#"'
    elif "Debian" in __grains__["os_family"]:
        cmd = 'grep XKBLAYOUT /etc/default/keyboard | grep -vE "^#"'
    elif "Gentoo" in __grains__["os_family"]:
        cmd = 'grep "^keymap" /etc/conf.d/keymaps | grep -vE "^#"'
    out = __salt__["cmd.run"](cmd, python_shell=True).split("=")
    ret = out[1].replace('"', "")
    return ret


def set_sys(layout):
    """
    Set current system keyboard setting

    CLI Example:

    .. code-block:: bash

        salt '*' keyboard.set_sys dvorak
    """
    if salt.utils.path.which("localectl"):
        __salt__["cmd.run"](f"localectl set-keymap {layout}")
    elif "RedHat" in __grains__["os_family"]:
        __salt__["file.sed"](
            "/etc/sysconfig/keyboard", "^LAYOUT=.*", f"LAYOUT={layout}"
        )
    elif "Debian" in __grains__["os_family"]:
        __salt__["file.sed"](
            "/etc/default/keyboard", "^XKBLAYOUT=.*", f"XKBLAYOUT={layout}"
        )
    elif "Gentoo" in __grains__["os_family"]:
        __salt__["file.sed"]("/etc/conf.d/keymaps", "^keymap=.*", f"keymap={layout}")
    return layout


def get_x():
    """
    Get current X keyboard setting

    CLI Example:

    .. code-block:: bash

        salt '*' keyboard.get_x
    """
    cmd = "setxkbmap -query | grep layout"
    out = __salt__["cmd.run"](cmd, python_shell=True).split(":")
    return out[1].strip()


def set_x(layout):
    """
    Set current X keyboard setting

    CLI Example:

    .. code-block:: bash

        salt '*' keyboard.set_x dvorak
    """
    cmd = f"setxkbmap {layout}"
    __salt__["cmd.run"](cmd)
    return layout
