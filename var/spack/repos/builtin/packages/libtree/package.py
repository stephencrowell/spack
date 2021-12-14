# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.build_systems.cmake import CMakePackage


class Libtree(MakefilePackage):
    """ldd as a tree"""

    homepage = "https://github.com/haampie/libtree"
    git      = "https://github.com/haampie/libtree.git"
    url      = "https://github.com/haampie/libtree/archive/refs/tags/v2.0.0.tar.gz"
    maintainers = ['haampie']

    version('master', branch='master')
    version('3.0.0-rc9', sha256='6956c51d58a4f43a23fea0fe7fc5141034829058bfc434e089c9ef1d1848229a')
    version('2.0.0', sha256='099e85d8ba3c3d849ce05b8ba2791dd25cd042a813be947fb321b0676ef71883')
    version('1.2.3', sha256='4a912cf97109219fe931942a30579336b6ab9865395447bd157bbfa74bf4e8cf')
    version('1.2.2', sha256='4ccf09227609869b85a170550b636defcf0b0674ecb0785063b81785b1c29bdd')
    version('1.2.1', sha256='26791c0f418b93d502879db0e1fd2fd3081b885ad87326611d992a5f8977a9b0')
    version('1.2.0', sha256='3e74655f22b1dcc19e8a1b9e7796b8ad44bc37f29e9a99134119e8521e28be97')
    version('1.1.4', sha256='38648f67c8fa72c3a4a3af2bb254b5fd6989c0f1362387ab298176db5cbbcc4e')
    version('1.1.3', sha256='4c681d7b67ef3d62f95450fb7eb84e33ff10a3b9db1f7e195b965b2c3c58226b')
    version('1.1.2', sha256='31641c6bf6c2980ffa7b4c57392460434f97ba66fe51fe6346867430b33a0374')
    version('1.1.1', sha256='3e8543145a40a94e9e2ce9fed003d2bf68294e1fce9607028a286bc132e17dc4')
    version('1.1.0', sha256='6cf36fb9a4c8c3af01855527d4931110732bb2d1c19be9334c689f1fd1c78536')
    version('1.0.4', sha256='b15a54b6f388b8bd8636e288fcb581029f1e65353660387b0096a554ad8e9e45')
    version('1.0.3', sha256='67ce886c191d50959a5727246cdb04af38872cd811c9ed4e3822f77a8f40b20b')

    def url_for_version(self, version):
        if version < Version("2.0.0"):
            return "https://github.com/haampie/libtree/releases/download/v{0}/sources.tar.gz".format(version)

        return "https://github.com/haampie/libtree/archive/refs/tags/v{0}.tar.gz".format(version)

    # Version 3.x (Makefile)
    @when('@3:')
    def install(self, spec, prefix):
        make('install', 'PREFIX=' + prefix)

    # Version 2.x and earlier (CMake)
    with when('@:2'):
        variant('chrpath', default=False, description='Use chrpath for deployment')
        variant('strip', default=False, description='Use binutils strip for deployment')
        variant('build_type', default='RelWithDebInfo',
                description='CMake build type',
                values=('Debug', 'Release', 'RelWithDebInfo', 'MinSizeRel'))
        depends_on('googletest', type='test')
        depends_on('cmake@3:', type='build')
        depends_on('chrpath', when='+chrpath', type='run')
        depends_on('binutils', when='+strip', type='run')

    # header only dependencies
    depends_on('cpp-termcolor', when='@2.0.0:2', type='build')
    depends_on('cxxopts', when='@2.0.0:2', type='build')
    depends_on('elfio', when='@2.0.0:2', type='build')

    def cmake_args(self):
        tests_enabled = 'ON' if self.run_tests else 'OFF'
        if self.spec.satisfies('@2.0:'):
            tests_define = 'LIBTREE_BUILD_TESTS'
        else:
            tests_define = 'BUILD_TESTING'

        return [
            CMakePackage.define(tests_define, tests_enabled)
        ]

    @when('@:2')
    def edit(self, spec, prefix):
        options = CMakePackage._std_args(self) + self.cmake_args()
        options.append(self.stage.source_path)
        with working_dir(self.build_directory):
            cmake(*options)

    @when('@:2')
    def check(self):
        with working_dir(self.build_directory):
            ctest('--output-on-failure')
