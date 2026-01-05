# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

""".. _ref_example_02_run_python_script_scope:

Test variable and function scope
--------------------------------

This example calls the ``run_python_script`` method and checks the variable and
function scope between calls.

"""

# %%
# Launch mechanical
# ~~~~~~~~~~~~~~~~~
# Launch a new Mechanical session in batch, setting the ``cleanup_on_exit``
# argument to ``False``. To close this Mechanical session when finished,
# this example must call  the ``mechanical.exit()`` method.

from ansys.mechanical.core import launch_mechanical

mechanical = launch_mechanical(batch=True, cleanup_on_exit=False)
print(mechanical)

# %%
# Run script to set variable
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# Run the script to assign a value to a variable.

output = mechanical.run_python_script(
    """
x = 10
x
"""
)
print(f"x = {output}")

# %%
# Access the variable in the next call
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Run the script to change the variable value.

output = mechanical.run_python_script(
    """
x = x * 2
x
"""
)
print(f"x = {output}")

# %%
# Define function
# ~~~~~~~~~~~~~~~
# Run the script to define a function and access the variable defined in the
# previous call.

output = mechanical.run_python_script(
    """
def multiply_by_10():
    return x*10

multiply_by_10()
"""
)
print(f"output = {output}")

# %%
# Access the function
# ~~~~~~~~~~~~~~~~~~~
# Run the script to access the function defined in the previous call.

output = mechanical.run_python_script(
    """
multiply_by_10() * 2
"""
)
print(f"output = {output}")


# %%
# Close mechanical
# ~~~~~~~~~~~~~~~~
# Close the mechanical instance.

mechanical.exit()
