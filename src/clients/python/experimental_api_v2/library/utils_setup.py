# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#  * Neither the name of NVIDIA CORPORATION nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
from setuptools import find_packages
from setuptools import setup

if 'VERSION' not in os.environ:
    raise Exception('envvar VERSION must be specified')

VERSION = os.environ['VERSION']

REQUIRED = ['numpy']

try:
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel

    class bdist_wheel(_bdist_wheel):

        def finalize_options(self):
            _bdist_wheel.finalize_options(self)
            self.root_is_pure = False

        def get_tag(self):
            pyver, abi, plat = _bdist_wheel.get_tag(self)
            pyver, abi = 'py3', 'none'
            return pyver, abi, plat
except ImportError:
    bdist_wheel = None

if not os.name == 'nt':
    platform_package_data = ['libcshmv2.so']
    if bool(os.environ.get('CUDA_VERSION', 0)):
        platform_package_data += ['libccudashmv2.so']

    setup(
        name='tritonclientutils',
        version=VERSION,
        author='NVIDIA Inc.',
        author_email='tanmayv@nvidia.com',
        description=
        'Python utils library for creating and managing system and cuda shared memory regions',
        license='BSD',
        url='http://nvidia.com',
        keywords=
        'triton tensorrt inference server system memory cuda system client',
        packages=find_packages(),
        install_requires=REQUIRED,
        package_data={
            '': platform_package_data,
        },
        zip_safe=False,
        cmdclass={'bdist_wheel': bdist_wheel},
    )
