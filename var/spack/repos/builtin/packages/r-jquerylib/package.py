# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class RJquerylib(RPackage):
    """Obtain 'jQuery' as an HTML Dependency Object."""

    cran = "jquerylib"

    version('0.1.4', sha256='f0bcc11dcde3a6ff180277e45c24642d3da3c8690900e38f44495efbc9064411')

    depends_on('r-htmltools', type=('build', 'run'))
