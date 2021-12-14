# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class PyFs(PythonPackage):
    """Python's filesystem abstraction layer"""

    homepage = "https://github.com/PyFilesystem/pyfilesystem2"
    pypi     = "fs/fs-2.4.14.tar.gz"

    version('2.4.14', sha256='9555dc2bc58c58cac03478ac7e9f622d29fe2d20a4384c24c90ab50de2c7b36c')

    depends_on('py-setuptools@38.3.0:', type='build')
    depends_on('py-appdirs@1.4.3:1.4',  type=('build', 'run'))
    depends_on('py-pytz',  type=('build', 'run'))
    depends_on('py-six@1.10:1', type=('build', 'run'))
    depends_on('py-enum34@1.1.6:1.1', type=('build', 'run'), when='^python@:3.3')
    depends_on('py-typing@3.6:3', type=('build', 'run'), when='^python@:3.5')
    depends_on('py-backports-os@0.1:0', type=('build', 'run'), when='^python@:2')
