# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the repronim package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##

from repronim.container import Container
from repronim.distribution import Distribution
from repronim.provenance import Provenance

import logging
from mock import patch, call

from repronim.utils import swallow_logs
from repronim.tests.utils import assert_in
from repronim.tests.test_constants import REPROZIP_OUTPUT


def test_installing_packages_to_docker(tmpdir):
    """
    Test installing 2 Debian packages in a Docker instance.
    """

    # Create the provenance file.
    provenance_file = tmpdir.join("reprozip.yml")
    provenance_file.write(REPROZIP_OUTPUT)

    provenance = Provenance.factory(provenance_file.strpath, 'reprozip')
    distribution = Distribution.factory('debian', provenance)

    with patch('docker.Client') as MockClient, \
            swallow_logs(new_level=logging.DEBUG) as log:

        # Set up return values for mocked docker.Client methods.
        client = MockClient.return_value
        client.build.return_value = ['{"stream": "Successfully built 9a754690460d\\n"}']
        client.create_container.return_value = {u'Id': u'd4cb4ee', u'Warnings': None}
        client.start.return_value = None
        client.logs.return_value = 'container standard output'
        client.exec_create.return_value = {u'Id': u'b3245cd55'}
        client.exec_start.return_value = ['stdout', 'from', 'container']

        # Section of code being tested.
        container_config = {
            'engine_url': 'tcp://127.0.0.1:2375'
        }
        container = Container.factory('dockerengine', distribution, container_config)
        image_id, container_id = container.create()
        container.install_packages(container_id)

        # Verify code output.
        assert image_id == u'9a754690460d'
        assert container_id == u'd4cb4ee'
        assert client.build.called
        calls = [call(image=u'9a754690460d', stdin_open=True)]
        client.create_container.assert_has_calls(calls)
        calls = [call({u'Id': u'd4cb4ee', u'Warnings': None})]
        client.start.assert_has_calls(calls)
        calls = [
            call(cmd=['apt-get', 'update'], container=u'd4cb4ee'),
            call(cmd=['apt-get', 'install', '-y', 'base-files'], container=u'd4cb4ee'),
            call(cmd=['apt-get', 'install', '-y', 'bc'], container=u'd4cb4ee')
        ]
        client.exec_create.assert_has_calls(calls)
        assert client.exec_start.call_count == 3
        calls = [call(exec_id=u'b3245cd55', stream=True)]
        client.exec_start.assert_has_calls(calls)
        assert_in("container standard output", log.lines)
        assert_in("Generating command for package: base-files", log.lines)
        assert_in("Generating command for package: bc", log.lines)
