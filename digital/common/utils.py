import contextlib
import os
import random
import shutil
import tempfile

from oslo_concurrency import processutils
from oslo_log import log as logging
import six

from digital import conf

CONF = conf.CONF
LOG = logging.getLogger(__name__)

MEMORY_UNITS = {
    'Ki': 2 ** 10,
    'Mi': 2 ** 20,
    'Gi': 2 ** 30,
    'Ti': 2 ** 40,
    'Pi': 2 ** 50,
    'Ei': 2 ** 60,
    'm': 10 ** -3,
    'k': 10 ** 3,
    'M': 10 ** 6,
    'G': 10 ** 9,
    'T': 10 ** 12,
    'p': 10 ** 15,
    'E': 10 ** 18,
    '': 1
}

DOCKER_MEMORY_UNITS = {
    'b': 1,
    'k': 2 ** 10,
    'm': 2 ** 20,
    'g': 2 ** 30,
}


def _get_root_helper():
    return 'sudo digital-rootwrap %s' % CONF.rootwrap_config


def execute(*cmd, **kwargs):
    """Convenience wrapper around oslo's execute() method.

    :param cmd: Passed to processutils.execute.
    :param use_standard_locale: True | False. Defaults to False. If set to
                                True, execute command with standard locale
                                added to environment variables.
    :returns: (stdout, stderr) from process execution
    :raises: UnknownArgumentError
    :raises: ProcessExecutionError
    """

    use_standard_locale = kwargs.pop('use_standard_locale', False)
    if use_standard_locale:
        env = kwargs.pop('env_variables', os.environ.copy())
        env['LC_ALL'] = 'C'
        kwargs['env_variables'] = env
    if kwargs.get('run_as_root') and 'root_helper' not in kwargs:
        kwargs['root_helper'] = _get_root_helper()
    result = processutils.execute(*cmd, **kwargs)
    LOG.debug('Execution completed, command line is "%s"',
              ' '.join(map(str, cmd)))
    LOG.debug('Command stdout is: "%s"', result[0])
    LOG.debug('Command stderr is: "%s"', result[1])
    return result


def trycmd(*args, **kwargs):
    """Convenience wrapper around oslo's trycmd() method."""
    if kwargs.get('run_as_root') and 'root_helper' not in kwargs:
        kwargs['root_helper'] = _get_root_helper()
    return processutils.trycmd(*args, **kwargs)


@contextlib.contextmanager
def tempdir(**kwargs):
    tempfile.tempdir = CONF.tempdir
    tmpdir = tempfile.mkdtemp(**kwargs)
    try:
        yield tmpdir
    finally:
        try:
            shutil.rmtree(tmpdir)
        except OSError as e:
            LOG.error('Could not remove tmpdir: %s', e)


def rmtree_without_raise(path):
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
    except OSError as e:
        LOG.warning("Failed to remove dir %(path)s, error: %(e)s",
                    {'path': path, 'e': e})


def safe_rstrip(value, chars=None):
    """Removes trailing characters from a string if that does not make it empty

    :param value: A string value that will be stripped.
    :param chars: Characters to remove.
    :return: Stripped value.

    """
    if not isinstance(value, six.string_types):
        LOG.warning("Failed to remove trailing character. "
                    "Returning original object. "
                    "Supplied object is not a string: %s,", value)
        return value

    return value.rstrip(chars) or value


def is_name_safe(name):
    """Checks whether the name is valid or not.

    :param name: name of the resource.
    :returns: True, when name is valid
              False, otherwise.
    """
    # TODO(madhuri): There should be some validation of name.
    # Leaving it now as there is no validation
    # while resource creation.
    # https://bugs.launchpad.net/digital/+bug/1430617
    if not name:
        return False
    return True


def generate_password(length, symbolgroups=None):
    """Generate a random password from the supplied symbol groups.

    At least one symbol from each group will be included. Unpredictable
    results if length is less than the number of symbol groups.

    Believed to be reasonably secure (with a reasonable password length!)

    """

    if symbolgroups is None:
        symbolgroups = CONF.password_symbols

    r = random.SystemRandom()

    # NOTE(jerdfelt): Some password policies require at least one character
    # from each group of symbols, so start off with one random character
    # from each symbol group
    password = [r.choice(s) for s in symbolgroups]
    # If length < len(symbolgroups), the leading characters will only
    # be from the first length groups. Try our best to not be predictable
    # by shuffling and then truncating.
    r.shuffle(password)
    password = password[:length]
    length -= len(password)

    # then fill with random characters from all symbol groups
    symbols = ''.join(symbolgroups)
    password.extend([r.choice(symbols) for _i in range(length)])

    # finally shuffle to ensure first x characters aren't from a
    # predictable group
    r.shuffle(password)

    return ''.join(password)


def get_openstack_ca():
    openstack_ca_file = CONF.drivers.openstack_ca_file

    if openstack_ca_file:
        with open(openstack_ca_file) as fd:
            return fd.read()
    else:
        return ''
