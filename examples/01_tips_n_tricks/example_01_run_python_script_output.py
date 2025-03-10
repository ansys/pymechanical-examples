""".. _ref_example_01_run_python_script_output:

Output to different formats and handle an error
-----------------------------------------------

This example calls the ``run_python_script`` method and gets the output in string,
JSON, and CSV formats. It also handles an error scenario.

"""

# %%
# Launch mechanical
# ~~~~~~~~~~~~~~~~~
# Launch a new Mechanical session in batch, setting the ``cleanup_on_exit``
# argument to ``False``. To close this Mechanical session when finished,
# this example must call  the ``mechanical.exit()`` method.

import json

from ansys.mechanical.core import launch_mechanical
import grpc

mechanical = launch_mechanical(batch=True, backend="python", cleanup_on_exit=False)
print(mechanical)

# %%
# Get and output a simple string
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Run the script to get a simple string output.

output = mechanical.run_python_script(
    """
def return_string():
    return "hello world"

return_string()
"""
)
print(f"string output={output}")

# %%
# Output string as JSON
# ~~~~~~~~~~~~~~~~~~~~~
# Run the script to get the string output as JSON.

output = mechanical.run_python_script(
    """
def return_json():
    import json
    dict = {"value1": 100, "value2": 200}
    json_text = json.dumps(dict)
    return json_text

return_json()
"""
)
print(f"json output={output}")

my_dict = json.loads(output)
print(f"Parsed json: value1={my_dict['value1']}, value2={my_dict['value2']}")

# %%
# Output string as CSV
# ~~~~~~~~~~~~~~~~~~~~
# Run the script to get the string output as CSV.

output = mechanical.run_python_script(
    """
def return_csv():
    return "1,2,3"

return_csv()
"""
)
print(f"csv output={output}")
csv_values = output.split(sep=",")
print(f"Parsed csv: {';'.join(csv_values)}")

# %%
# Handle an error scenario
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Run the script and handle the error.
try:
    output = mechanical.run_python_script("hello_world()")
except grpc.RpcError as error:
    print(f"Error: {error.details()}")

# %%
# Close mechanical
# ~~~~~~~~~~~~~~~~
# Close the mechanical instance.

mechanical.exit()
