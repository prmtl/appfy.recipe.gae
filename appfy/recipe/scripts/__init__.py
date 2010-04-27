import ConfigParser
import os
import runpy
import sys


def parse_argv(argv):
    """A very simple argv parser. Returns a list of (opts, args) for options
    and arguments in the passed argv. It won't try to validate anything.
    """
    opts = []
    args = []
    for arg in argv:
        if arg.startswith('-'):
            parts = arg.split('=', 1)
            if len(parts) == 1:
                val = (parts[0], None)
            else:
                val = (parts[0], parts[1])

            opts.append(val)
        else:
            args.append(arg)

    return opts, args


def merge_opts(sys_opts, def_opts):
    """Merges options from sys.argv to default options: the first overrides
    the later.
    """
    res = []
    defined_opts = dict(def_opts)
    defined_keys = defined_opts.keys()

    for opt, optarg in sys_opts:
        if opt in defined_keys:
            defined_keys.remove(opt)

        if optarg is None:
            res.append(opt)
        else:
            res.append('%s=%s' % (opt, optarg))

    for opt in defined_keys:
        optarg = defined_opts[opt]

        if optarg is None:
            res.append(opt)
        else:
            res.append('%s=%s' % (opt, optarg))

    return res


def get_dev_appserver_argv(defaults):
    def_opts, def_args = parse_argv(defaults)
    sys_opts, sys_args = parse_argv(sys.argv[1:])

    app = None
    if sys_args:
        app = sys_args[0]
    elif def_args:
        app = def_args[0]

    res = [sys.argv[0]] + merge_opts(sys_opts, def_opts)
    if app:
        res.append(app)

    return res


def get_config(filename, section=None, key=None):
    try:
        config = ConfigParser.RawConfigParser()
        config.read(filename)
        if section is None:
            return config

        values = config.items(section)
        if key is None:
            return values

        return dict(values).get(key, None)
    except ConfigParser.NoSectionError:
        return None


def get_dev_appserver_config(config_file):
    config = get_config(config_file, 'dev_appserver', 'defaults')
    if config:
        # Accept single line or multi-line configuration.
        config = ' '.join([o for o in config.split('\n') if o.strip()])
        config = config.split()

    if not config:
        return None

    return config


def appcfg(base, gae_path):
    runpy.run_module('appcfg', run_name='__main__')


def dev_appserver(base, gae_path):
    config = get_dev_appserver_config(os.path.join(base, 'buildout.cfg'))
    if config:
        sys.argv = get_dev_appserver_argv(config)

    runpy.run_module('dev_appserver', run_name='__main__')
