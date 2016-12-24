# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the repronim package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Functions to read and manipulate reprozip yaml files

"""
import datetime

import repronim
import yaml
import io


def read_reprozip_yaml(filename):
    """Parses a ReproZip YAML file into a configuration object

    Given the path to a ReproZip YAML file, it parses the file and
    stores the resulting environment configuration into an object.

    Parameters
    ----------
    filename : str
        Path to the ReproZip YAML file

    Return
    ------
    dict
        The environment configuration

    """
    with io.open(filename, encoding='utf-8') as fp:
        config = yaml.safe_load(fp)
        # TODO: Check version of ReproZip file and warn if unknown
        return config


def identify_packages(config):
    """Identifies packages in the current environment from a ReproZip config

    Given a ReproZip configuration, it analyzes the current environment to
    find details about the source packages, and places the results back into
    the configuration object.

    Parameters
    ----------
    config : dict
        ReproZip configuration (input/output)

    Return
    ------
    dict
        A reference to the input dict

    """
    # Immediately clone the configuration
    files = get_system_files(config)

    # clear out current package assignment
    config['packages'] = {}

    # TODO: Identify files here

    # set any files not identified
    config['other_files'] = list(files)
    config['other_files'].sort()

    return config


def write_config(os, config):
    """Writes an environment config to a stream

    Parameters
    ----------
    os
        Output Stream

    config : dict
        Environment configuration (input)

    """
    envconfig = dict(config)  # Shallow copy for destruction
    os.write(("# ReproNim Environment Configuration File\n" +
              "# This file was created by ReproNim {0} on {1}\n").format(
            repronim.__version__, datetime.datetime.now()))

    c = "\n# Runs: Commands and related environment variables\n\n"
    write_config_key(os, envconfig, "runs", c)

    c = "\n# Packages \n\n"
    write_config_key(os, envconfig, "packages", c)

    c = "\n# Non-Packaged Files \n\n"
    write_config_key(os, envconfig, "other_files", c)

    os.write("\n# Other ReproZip keys (not used by ReproNim) \n\n")
    os.write(yaml.safe_dump(envconfig,
                            encoding='utf-8',
                            allow_unicode=True))


def write_config_key(os, envconfig, key, intro_comment=""):
    """Writes the YAML representation of a single key

    This writes a single key of a dict to an output stream and then removes
    the key from the dict.

    Parameters
    ----------
    os
    envconfig
    key
    intro_comment

    """
    if key in envconfig:
        mini_config = dict()
        mini_config[key] = envconfig[key]
        del envconfig[key]
        os.write(intro_comment)
        os.write(yaml.safe_dump(mini_config,
                                encoding='utf-8',
                                allow_unicode=True))


def get_system_files(config):
    """Pulls the system files from a ReproZip configuration into a set

    Given a ReproZip configuration (read into a dictionary) it pulls
    the list of files from "packages" and "other files" sections into a
    set. It excludes files from "input_output".

    Parameters
    ----------
    config : dict
        ReproZip configuration

    Return
    ------
    set
        System fles from the configuration
    """

    files = set()

    if 'packages' in config:
        for package in config['packages']:
            if 'files' in package:
                files.update(package['files'])

    if 'other_files' in config:
        files.update(config["other_files"])

    return files
