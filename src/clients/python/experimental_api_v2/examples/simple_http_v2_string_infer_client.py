#!/usr/bin/env python
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

import argparse
import numpy as np
import sys

import tritonhttpclient


def TestIdentityInference(np_array, binary_data):
    model_name = "savedmodel_zero_1_object"
    inputs = []
    outputs = []

    inputs.append(tritonhttpclient.InferInput('INPUT0', np_array.shape, "BYTES"))
    inputs[0].set_data_from_numpy(np_array, binary_data=binary_data)

    outputs.append(
        tritonhttpclient.InferRequestedOutput('OUTPUT0', binary_data=binary_data))

    results = triton_client.infer(model_name=model_name,
                                  inputs=inputs,
                                  outputs=outputs)
    if (np_array.dtype == np.object):
        if binary_data:
            if not np.array_equal(np_array,
                        np.char.decode(results.as_numpy('OUTPUT0'))):
                print(results.as_numpy('OUTPUT0'))
                sys.exit(1)
        else:
            if not np.array_equal(np_array, results.as_numpy('OUTPUT0')):
                print(results.as_numpy('OUTPUT0'))
                sys.exit(1)
    else:
        encoded_results = np.char.encode(
            results.as_numpy('OUTPUT0').astype(str)
            )
        if not np.array_equal(np_array, encoded_results):
            print(encoded_results)
            sys.exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v',
                        '--verbose',
                        action="store_true",
                        required=False,
                        default=False,
                        help='Enable verbose output')
    parser.add_argument('-u',
                        '--url',
                        type=str,
                        required=False,
                        default='localhost:8000',
                        help='Inference server URL. Default is localhost:8000.')

    FLAGS = parser.parse_args()
    try:
        triton_client = tritonhttpclient.InferenceServerClient(url=FLAGS.url,
                                                         verbose=FLAGS.verbose)
    except Exception as e:
        print("context creation failed: " + str(e))
        sys.exit()

    model_name = 'simple_string'

    inputs = []
    outputs = []
    inputs.append(tritonhttpclient.InferInput('INPUT0', [1, 16], "BYTES"))
    inputs.append(tritonhttpclient.InferInput('INPUT1', [1, 16], "BYTES"))

    # Create the data for the two input tensors. Initialize the first
    # to unique integers and the second to all ones.
    in0 = np.arange(start=0, stop=16, dtype=np.int32)
    in0 = np.expand_dims(in0, axis=0)
    in1 = np.ones(shape=(1, 16), dtype=np.int32)
    expected_sum = np.add(in0, in1)
    expected_diff = np.subtract(in0, in1)

    in0n = np.array([str(x) for x in in0.reshape(in0.size)], dtype=object)
    input0_data = in0n.reshape(in0.shape)
    in1n = np.array([str(x) for x in in1.reshape(in1.size)], dtype=object)
    input1_data = in1n.reshape(in1.shape)

    # Initialize the data
    inputs[0].set_data_from_numpy(input0_data, binary_data=True)
    inputs[1].set_data_from_numpy(input1_data, binary_data=False)

    outputs.append(tritonhttpclient.InferRequestedOutput('OUTPUT0', binary_data=True))
    outputs.append(tritonhttpclient.InferRequestedOutput('OUTPUT1',
                                                   binary_data=False))

    results = triton_client.infer(model_name=model_name,
                                  inputs=inputs,
                                  outputs=outputs)

    # Get the output arrays from the results
    output0_data = results.as_numpy('OUTPUT0')
    output1_data = results.as_numpy('OUTPUT1')

    for i in range(16):
        print(str(input0_data[0][i]) + " + " + str(input1_data[0][i]) + " = " +
              str(output0_data[0][i]))
        print(str(input0_data[0][i]) + " - " + str(input1_data[0][i]) + " = " +
              str(output1_data[0][i]))

        # Convert result from string to int to check result
        r0 = int(output0_data[0][i])
        r1 = int(output1_data[0][i])
        if expected_sum[0][i] != r0:
            print("error: incorrect sum")
            sys.exit(1)
        if expected_diff[0][i] != r1:
            print("error: incorrect difference")
            sys.exit(1)

    # Test with null character
    null_chars_array = np.array(["he\x00llo" for i in range(16)], dtype=object)
    null_char_data = null_chars_array.reshape([1, 16])
    TestIdentityInference(null_char_data, True)  # Using binary data
    TestIdentityInference(null_char_data, False)  # Using JSON data

    # Test with byte arrays
    bytes_data = [b'1' for i in range(16)]
    np_bytes_data = np.array(bytes_data, dtype=bytes)
    np_bytes_data = np_bytes_data.reshape([1, 16])
    TestIdentityInference(np_bytes_data, True)  # Using binary data
    TestIdentityInference(np_bytes_data, False)  # Using JSON data

    print('PASS: string')
