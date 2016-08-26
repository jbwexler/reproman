# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the repronim package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
""" repronim exceptions
"""


class CommandError(RuntimeError):
    """Thrown if a command call fails.
    """

    def __init__(self, cmd="", msg="", code=None, stdout="", stderr=""):
        RuntimeError.__init__(self, msg)
        self.cmd = cmd
        self.msg = msg
        self.code = code
        self.stdout = stdout
        self.stderr = stderr

    def __str__(self):
        to_str = "%s: command '%s'" % (self.__class__.__name__, self.cmd)
        if self.code:
            to_str += " failed with exitcode %d" % self.code
        to_str += ".\n%s" % self.msg
        return to_str


class AnnexBatchCommandError(CommandError):
    """Thrown if a batched command to annex fails

    """
    pass


class CommandNotAvailableError(CommandError):
    """Thrown if a command is not available due to certain circumstances.
    """
    pass


class FileNotInAnnexError(CommandError, IOError):
    """Thrown if a file is not under control of git-annex.
    """
    def __init__(self, cmd="", msg="", code=None, filename=""):
        CommandError.__init__(self, cmd=cmd, msg=msg, code=code)
        IOError.__init__(self, code, "%s: %s" % (cmd, msg), filename)

    def __str__(self):
        return "%s\n%s" % (CommandError.__str__(self), IOError.__str__(self))


class FileInGitError(FileNotInAnnexError):
    """Thrown if a file is not under control of git-annex, but git itself.
    """
    pass


class FileNotInRepositoryError(FileNotInAnnexError):
    """Thrown if a file is not in the repository at all.
    """
    pass


class InsufficientArgumentsError(ValueError):
    """To be raise instead of `ValueError` when use help output is desired"""
    pass

#
# Downloaders
#

class DownloadError(Exception):
    pass


class IncompleteDownloadError(DownloadError):
    pass


class TargetFileAbsent(DownloadError):
    pass


class AccessDeniedError(DownloadError):
    pass


class AccessFailedError(DownloadError):
    pass


class UnhandledRedirectError(DownloadError):
    def __init__(self, msg=None, url=None, **kwargs):
        super(UnhandledRedirectError, self).__init__(msg, **kwargs)
        self.url = url

#
# Crawler
#

class CrawlerError(Exception):
    pass

class PipelineNotSpecifiedError(CrawlerError):
    pass