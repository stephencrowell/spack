# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import itertools
import sys
import os

from spack import *


class Mesa(MesonPackage):
    """Mesa is an open-source implementation of the OpenGL specification
     - a system for rendering interactive 3D graphics."""

    homepage = "https://www.mesa3d.org"
    maintainers = ['chuckatkins', 'v-dobrev']

    git = "https://gitlab.freedesktop.org/mesa/mesa.git"
    url = "https://archive.mesa3d.org/mesa-20.2.1.tar.xz"

    version('master', tag='master')
    version('21.2.1', sha256='2c65e6710b419b67456a48beefd0be827b32db416772e0e363d5f7d54dc01787')
    version('21.0.3', sha256='565c6f4bd2d5747b919454fc1d439963024fc78ca56fd05158c3b2cde2f6912b')
    version('21.0.0', sha256='e6204e98e6a8d77cf9dc5d34f99dd8e3ef7144f3601c808ca0dd26ba522e0d84')
    version('20.3.4', sha256='dc21a987ec1ff45b278fe4b1419b1719f1968debbb80221480e44180849b4084')
    version('20.2.1', sha256='d1a46d9a3f291bc0e0374600bdcb59844fa3eafaa50398e472a36fc65fd0244a')

    depends_on('meson@0.52:', type='build')

    depends_on('pkgconfig', type='build')
    depends_on('bison', type='build')
    depends_on('cmake', type='build')
    depends_on('flex', type='build')
    depends_on('gettext', type='build')
    depends_on('python@3:', type='build')
    depends_on('py-mako@0.8.0:', type='build')
    depends_on('expat')
    depends_on('zlib@1.2.3:')

    # Internal options
    variant('llvm', default=True, description="Enable LLVM.")
    variant('swr', default='auto',
            values=('auto', 'none', 'avx', 'avx2', 'knl', 'skx'),
            multi=True,
            description="Enable the SWR driver.")
    # conflicts('~llvm', when='~swr=none')

    # Front ends
    variant('osmesa', default=True, description="Enable the OSMesa frontend.")

    is_linux = sys.platform.startswith('linux')
    variant('glvnd', default=is_linux,
            description="Expose Graphics APIs through libglvnd")
    variant('glx', default=is_linux, description="Enable the GLX frontend.")

    # TODO: effectively deal with EGL.  The implications of this have not been
    # worked through yet
    variant('egl', default=False, description="Enable the EGL frontend.")

    # TODO: Effectively deal with hardware drivers
    # The implication of this is enabling DRI, among other things, and
    # needing to check which llvm targets were built (ptx or amdgpu, etc.)

    # Back ends
    variant('opengl', default=True, description="Enable full OpenGL support.")
    variant('opengles', default=False, description="Enable OpenGL ES support.")

    # Provides
    provides('gl@4.5',  when='+opengl ~glvnd')
    provides('glx@1.4', when='+glx ~glvnd')
    # This isn't possible b/c of conflict. Should remove?
    # provides('egl@1.5', when='+egl ~glvnd')

    provides('libglvnd-be-gl', when='+opengl +glvnd')
    provides('libglvnd-be-glx', when='+opengl +glvnd +glx')
    provides('libglvnd-be-egl', when='+opengl +glvnd +egl')
    provides('osmesa', when='+osmesa +glvnd')

    # Variant dependencies
    depends_on('llvm@6:', when='+llvm')
    depends_on('libx11',  when='+glx')
    depends_on('libxcb',  when='+glx')
    depends_on('libxext', when='+glx')
    depends_on('libxt',  when='+glx')
    depends_on('xrandr', when='+glx')
    depends_on('glproto@1.4.14:', when='+glx')

    depends_on('libglvnd', when='+glvnd')

    # Add the necessary dri dependencies
    for dependency, constraint in itertools.product(
            ('damageproto@1.1:',
             'dri2proto@2.8:',
             'fixesproto',
             'glproto@1.4.13:',
             'libdrm@2.4.75:',
             'libx11',
             'libxext',
             'libxcb@1.8.1:',
             'libxdamage@1.1:',
             'libxfixes',
             'libxshmfence',
             'libxxf86vm',
             'xf86vidmodeproto'), ('+egl', '+glvnd')):
        depends_on(dependency, when=constraint)

    # version specific issue
    # https://gcc.gnu.org/bugzilla/show_bug.cgi?id=96130
    conflicts('%gcc@10.1.0', msg='GCC 10.1.0 has a bug')

    # Require at least 1 front-end
    conflicts('~egl ~glx ~osmesa')

    # Require at least 1 back-end
    # TODO: Add vulkan to this conflict once made available
    conflicts('~opengl ~opengles')

    # OpenGL ES requires OpenGL
    conflicts('~opengl +opengles')

    # EGL and OpenGL are in separate libraries. libglvnd is needed to combine the two 
    conflicts('+egl +opengl ~glvnd')

    # requires native to be added to llvm_modules when using gallium swrast
    patch('https://cgit.freedesktop.org/mesa/mesa/patch/meson.build?id=054dd668a69acc70d47c73abe4646e96a1f23577', sha256='36096a178070e40217945e12d542dfe80016cb897284a01114d616656c577d73', when='@21.0.0:21.0.3')

    # 'auto' needed when shared llvm is built
    @when('^llvm~shared_libs')
    def patch(self):
        filter_file(
            r"_llvm_method = 'auto'",
            "_llvm_method = 'config-tool'",
            "meson.build")

    def meson_args(self):
        spec = self.spec
        args = ['-Dvulkan-drivers=',
                '-Dgallium-vdpau=disabled',
                '-Dgallium-xvmc=disabled',
                '-Dgallium-omx=disabled',
                '-Dgallium-va=disabled',
                '-Dgallium-xa=disabled',
                '-Dgallium-nine=false',
                '-Dgallium-opencl=disabled',
                '-Dbuild-tests=false']
        args_platforms = []
        args_gallium_drivers = ['swrast']
        args_dri_drivers = []

        opt_enable = lambda c, o: '-D%s=%sabled' % (o, 'en' if c else 'dis')
        opt_bool = lambda c, o: '-D%s=%s' % (o, str(c).lower())
        if spec.target.family == 'arm' or spec.target.family == 'aarch64':
            args.append('-Dlibunwind=disabled')

        num_frontends = 0

        use_dri = ('+egl' in spec) or ('+glvnd' in spec)
        args.append('-Ddri=true' if use_dri else '-Ddri=false')

        if '+glvnd' in spec:
            args.append('-Dglvnd=true')
        else:
            args.append('-Dglvnd=false')

        if spec.satisfies('@:20.3'):
            osmesa_enable, osmesa_disable = ('gallium', 'none')
        else:
            osmesa_enable, osmesa_disable = ('true', 'false')

        if '+osmesa' in spec:
            num_frontends += 1
            args.append('-Dosmesa={0}'.format(osmesa_enable))
        else:
            args.append('-Dosmesa={0}'.format(osmesa_disable))

        if '+glx' in spec:
            num_frontends += 1

            args.append('-Dglx=dri'
                        if use_dri else
                        '-Dglx=gallium-xlib')
            args_platforms.append('x11')
        else:
            args.append('-Dglx=disabled')
        
        print(spec)
        if '+egl' in spec:
            num_frontends += 1
            args.extend(['-Degl=enabled', '-Dgbm=enabled'])
            args.append('-Degl-native-platform=surfaceless')
        else:
            args.extend(
                ['-Degl=disabled', '-Dgbm=disabled'])

        args.append(opt_bool('+opengl' in spec, 'opengl'))
        args.append(opt_enable('+opengles' in spec, 'gles1'))
        args.append(opt_enable('+opengles' in spec, 'gles2'))

        args.append(opt_enable(num_frontends > 1 or (use_dri), 'shared-glapi'))

        if '+llvm' in spec:
            args.append('-Dllvm=enabled')
            args.append(opt_enable(
                '+link_dylib' in spec['llvm'], 'shared-llvm'))
        else:
            args.append('-Dllvm=disabled')

        args_swr_arches = []
        if 'swr=auto' in spec:
            if 'avx' in spec.target:
                args_swr_arches.append('avx')
            if 'avx2' in spec.target:
                args_swr_arches.append('avx2')
            if 'avx512f' in spec.target:
                if 'avx512er' in spec.target:
                    args_swr_arches.append('knl')
                if 'avx512bw' in spec.target:
                    args_swr_arches.append('skx')
        else:
            if 'swr=avx' in spec:
                args_swr_arches.append('avx')
            if 'swr=avx2' in spec:
                args_swr_arches.append('avx2')
            if 'swr=knl' in spec:
                args_swr_arches.append('knl')
            if 'swr=skx' in spec:
                args_swr_arches.append('skx')

        if args_swr_arches:
            if '+llvm' not in spec:
                raise SpecError('Variant swr requires +llvm')
            args_gallium_drivers.append('swr')
            args.append('-Dswr-arches=' + ','.join(args_swr_arches))

        # Add the remaining list args
        args.append('-Dplatforms=' + ','.join(args_platforms))
        args.append('-Dgallium-drivers=' + ','.join(args_gallium_drivers))
        args.append('-Ddri-drivers=' + ','.join(args_dri_drivers))

        return args

    # NOTE: Each of the following *libs properties return empty lists if
    # +glvnd, because there are no mesa libraries to be linked against.  When
    # acting as a glvnd dispatch target, libglvnd will find mesa's shared
    # objects via environment variables, dynamically load them, and dispatch
    # calls to them at run time.

    @property
    def libs(self):
        spec = self.spec
        libs_to_seek = set()

        if '~glvnd' in spec:
            if '+osmesa' in spec:
                libs_to_seek.add('libOSMesa')

            if '+glx' in spec:
                libs_to_seek.add('libGL')

            if '+egl' in spec:
                libs_to_seek.add('libEGL')

            if '+opengl' in spec:
                libs_to_seek.add('libGL')

            if '+opengles' in spec:
                libs_to_seek.add('libGLES')
                libs_to_seek.add('libGLES2')

            if libs_to_seek:
                return find_libraries(list(libs_to_seek),
                                      root=self.spec.prefix,
                                      recursive=True)
        return LibraryList(())

    @property
    def osmesa_libs(self):
        if '+glvnd' in self.spec:
            return LibraryList(())

        return find_libraries('libOSMesa',
                              root=self.spec.prefix,
                              recursive=True)

    @property
    def glx_libs(self):
        if '+glvnd' in self.spec:
            return LibraryList(())

        return find_libraries('libGL',
                              root=self.spec.prefix,
                              recursive=True)

    @property
    def egl_libs(self):
        if '+glvnd' in self.spec:
            return LibraryList(())

        return find_libraries('libEGL',
                              root=self.spec.prefix,
                              recursive=True)

    @property
    def gl_libs(self):
        if '+glvnd' in self.spec:
            return LibraryList(())

        return find_libraries('libGL',
                              root=self.spec.prefix,
                              recursive=True)

    def setup_run_environment(self, env):
        if '+glx +glvnd' in self.spec:
            env.set('__GLX_VENDOR_LIBRARY_NAME', 'mesa')

        if '+egl +glvnd' in self.spec:
            env.set('__EGL_VENDOR_LIBRARY_FILENAMES', ''.join((
                os.path.join(self.spec.prefix, 'share', 'glvnd',
                             'egl_vendor.d', '50_mesa.json'))))
