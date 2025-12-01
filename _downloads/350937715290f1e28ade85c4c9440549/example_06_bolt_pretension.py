# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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

""".. _ref_example_06:

Bolt Pretension
---------------

This example demonstrates how to insert a Static Structural analysis
into a new Mechanical session and execute a sequence of
Python scripting commands that define and solve a bolt-pretension analysis.
Scripts then evaluate the following results: deformation,
equivalent stresses, contact, and bolt
"""

# %%
# Import necessary libraries
# ~~~~~~~~~~~~~~~~~~~~~~~~~~

import os

from ansys.mechanical.core import launch_mechanical
from ansys.mechanical.core.examples import download_file
from matplotlib import image as mpimg
from matplotlib import pyplot as plt

# %%
# Launch mechanical
# ~~~~~~~~~~~~~~~~~
# Launch a new Mechanical session in batch, setting the ``cleanup_on_exit``
# argument to ``False``. To close this Mechanical session when finished,
# this example must call  the ``mechanical.exit()`` method.

mechanical = launch_mechanical(batch=True, cleanup_on_exit=False)
print(mechanical)

# %%
# Initialize variable for workflow
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Set the ``part_file_path`` variable on the server for later use.
# Make this variable compatible for Windows, Linux, and Docker containers.

project_directory = mechanical.project_directory
print(f"project directory = {project_directory}")

# %%
# Download required geometry file
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Download the required file. Print the file path for the geometry file.

geometry_path = download_file(
    "example_06_bolt_pret_geom.agdb", "pymechanical", "00_basic"
)
print(f"Downloaded the geometry file to: {geometry_path}")

# %%
# Upload the file to the project directory

mechanical.upload(file_name=geometry_path, file_location_destination=project_directory)

# %%
# Build the path relative to project directory and verify

base_name = os.path.basename(geometry_path)
combined_path = os.path.join(project_directory, base_name)
part_file_path = combined_path.replace("\\", "\\\\")
mechanical.run_python_script(f"part_file_path='{part_file_path}'")
result = mechanical.run_python_script("part_file_path")
print(f"Geometry file on server: {result}")

# %%
# Download required material file
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Download the required file. Print the file path for the material file

mat_cop_path = download_file("example_06_Mat_Copper.xml", "pymechanical", "00_basic")
print(f"Downloaded the material file to: {mat_cop_path}")
mat_st_path = download_file("example_06_Mat_Steel.xml", "pymechanical", "00_basic")
print(f"Downloaded the material file to: {mat_st_path}")

# %%
# Upload the file to the project directory

mechanical.upload(file_name=mat_cop_path, file_location_destination=project_directory)
mechanical.upload(file_name=mat_st_path, file_location_destination=project_directory)

# %%
# Build the path relative to project directory and verify

base_name = os.path.basename(mat_cop_path)
combined_path = os.path.join(project_directory, base_name)
mat_Copper_file_path = combined_path.replace("\\", "\\\\")
mechanical.run_python_script(f"mat_Copper_file_path='{mat_Copper_file_path}'")

base_name = os.path.basename(mat_st_path)
combined_path = os.path.join(project_directory, base_name)
mat_Steel_file_path = combined_path.replace("\\", "\\\\")
mechanical.run_python_script(f"mat_Steel_file_path='{mat_Steel_file_path}'")

result = mechanical.run_python_script("mat_Copper_file_path")
print(f"mat_Copper_file_path on server: {result}")
result = mechanical.run_python_script("mat_Steel_file_path")
print(f"mat_Steel_file_path on server: {result}")

# %%
# Run the script
# ~~~~~~~~~~~~~~
# Run the Mechanical script to attach the geometry and set up and solve the
# analysis

output = mechanical.run_python_script(
    """
import json
import os

# Read geometry and material information.
geometry_import_group = Model.GeometryImportGroup
geometry_import = geometry_import_group.AddGeometryImport()
geometry_import_format = Ansys.Mechanical.DataModel.Enums.GeometryImportPreference.\
    Format.Automatic
geometry_import_preferences = Ansys.ACT.Mechanical.Utilities.GeometryImportPreferences()
geometry_import_preferences.ProcessNamedSelections = True
geometry_import_preferences.ProcessCoordinateSystems = True
geometry_import.Import(part_file_path,geometry_import_format,geometry_import_preferences)

# Import materials.
MAT = ExtAPI.DataModel.Project.Model.Materials
MAT.Import(mat_Copper_file_path)
MAT.Import(mat_Steel_file_path)

Model.AddStaticStructuralAnalysis()
STAT_STRUC = Model.Analyses[0]
STAT_STRUC_SOLN = STAT_STRUC.Solution
STAT_STRUC_ANA_SETTING = STAT_STRUC.Children[0]

# Set up the unit system.
ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardNMM

# Store all main tree nodes as variables.
MODEL = ExtAPI.DataModel.Project.Model
GEOM = ExtAPI.DataModel.Project.Model.Geometry
CONN_GRP = ExtAPI.DataModel.Project.Model.Connections
CS_GRP = ExtAPI.DataModel.Project.Model.CoordinateSystems
MSH = ExtAPI.DataModel.Project.Model.Mesh
NS_GRP = ExtAPI.DataModel.Project.Model.NamedSelections

# Store name selection.
block3_block2_cont_NS = [x for x in ExtAPI.DataModel.Tree.AllObjects
if x.Name == 'block3_block2_cont'][0]
block3_block2_targ_NS = [x for x in ExtAPI.DataModel.Tree.AllObjects
if x.Name == 'block3_block2_targ'][0]
shank_block3_targ_NS = [x for x in ExtAPI.DataModel.Tree.AllObjects
if x.Name == 'shank_block3_targ'][0]
shank_block3_cont_NS = [x for x in ExtAPI.DataModel.Tree.AllObjects
if x.Name == 'shank_block3_cont'][0]
block1_washer_cont_NS = [x for x in ExtAPI.DataModel.Tree.AllObjects
if x.Name == 'block1_washer_cont'][0]
block1_washer_targ_NS = [x for x in ExtAPI.DataModel.Tree.AllObjects
if x.Name == 'block1_washer_targ'][0]
washer_bolt_cont_NS = [x for x in ExtAPI.DataModel.Tree.AllObjects
if x.Name == 'washer_bolt_cont'][0]
washer_bolt_targ_NS = [x for x in ExtAPI.DataModel.Tree.AllObjects
if x.Name == 'washer_bolt_targ'][0]
shank_bolt_targ_NS = [x for x in ExtAPI.DataModel.Tree.AllObjects
if x.Name == 'shank_bolt_targ'][0]
shank_bolt_cont_NS = [x for x in ExtAPI.DataModel.Tree.AllObjects
if x.Name == 'shank_bolt_cont'][0]
block2_block1_cont_NS = [x for x in ExtAPI.DataModel.Tree.AllObjects
if x.Name == 'block2_block1_cont'][0]
block2_block1_targ_NS = [x for x in ExtAPI.DataModel.Tree.AllObjects
if x.Name == 'block2_block1_targ'][0]
all_bodies = [x for x in ExtAPI.DataModel.Tree.AllObjects
if x.Name == 'all_bodies'][0]
bodies_5 = [x for x in ExtAPI.DataModel.Tree.AllObjects
if x.Name == 'bodies_5'][0]
shank = [x for x in ExtAPI.DataModel.Tree.AllObjects
if x.Name == 'shank'][0]
shank_face = [x for x in ExtAPI.DataModel.Tree.AllObjects
if x.Name == 'shank_face'][0]
shank_face2 = [x for x in ExtAPI.DataModel.Tree.AllObjects
if x.Name == 'shank_face2'][0]
bottom_surface = [x for x in ExtAPI.DataModel.Tree.AllObjects
if x.Name == 'bottom_surface'][0]
block2_surface = [x for x in ExtAPI.DataModel.Tree.AllObjects
if x.Name == 'block2_surface'][0]
shank_surface = [x for x in ExtAPI.DataModel.Tree.AllObjects
if x.Name == 'shank_surface'][0]

# Assign material to bodies.
SURFACE1=GEOM.Children[0].Children[0]
SURFACE1.Material="Steel"

SURFACE2=GEOM.Children[1].Children[0]
SURFACE2.Material="Copper"

SURFACE3=GEOM.Children[2].Children[0]
SURFACE3.Material="Copper"

SURFACE4=GEOM.Children[3].Children[0]
SURFACE4.Material="Steel"

SURFACE5=GEOM.Children[4].Children[0]
SURFACE5.Material="Steel"

SURFACE6=GEOM.Children[5].Children[0]
SURFACE6.Material="Steel"

# Define coordinate system.
coordinate_systems_17 = Model.CoordinateSystems
coordinate_system_93 = coordinate_systems_17.AddCoordinateSystem()
coordinate_system_93.OriginDefineBy = CoordinateSystemAlignmentType.Fixed
coordinate_system_93.OriginX = Quantity(-195, "mm")
coordinate_system_93.OriginY = Quantity(100, "mm")
coordinate_system_93.OriginZ = Quantity(50, "mm")
coordinate_system_93.PrimaryAxis = CoordinateSystemAxisType.PositiveZAxis

# Change contact settings and add a command snippet to use the Archard Wear Model.
connections =  ExtAPI.DataModel.Project.Model.Connections

# Delete existing contacts.
for connection in connections.Children:
    if connection.DataModelObjectCategory==DataModelObjectCategory.ConnectionGroup:
        connection.Delete()

CONT_REG1 = CONN_GRP.AddContactRegion()
CONT_REG1.SourceLocation = NS_GRP.Children[0]
CONT_REG1.TargetLocation = NS_GRP.Children[1]
CONT_REG1.ContactType=ContactType.Frictional
CONT_REG1.FrictionCoefficient = 0.2
CONT_REG1.SmallSliding = ContactSmallSlidingType.Off
CONT_REG1.UpdateStiffness = UpdateContactStiffness.Never
CMD1=CONT_REG1.AddCommandSnippet()

# Add missing contact keyopt and Archard Wear Model in workbench using a command snippet.
AWM = '''keyopt,cid,9,5
rmodif,cid,10,0.00
rmodif,cid,23,0.001'''
CMD1.AppendText(AWM)

CONTS = CONN_GRP.Children[0]
CONT_REG2 = CONTS.AddContactRegion()
CONT_REG2.SourceLocation = NS_GRP.Children[3]
CONT_REG2.TargetLocation = NS_GRP.Children[2]
CONT_REG2.ContactType=ContactType.Bonded
CONT_REG2.ContactFormulation = ContactFormulation.MPC

CONT_REG3 = CONTS.AddContactRegion()
CONT_REG3.SourceLocation = NS_GRP.Children[4]
CONT_REG3.TargetLocation = NS_GRP.Children[5]
CONT_REG3.ContactType=ContactType.Frictional
CONT_REG3.FrictionCoefficient = 0.2
CONT_REG3.SmallSliding = ContactSmallSlidingType.Off
CONT_REG3.UpdateStiffness = UpdateContactStiffness.Never
CMD3=CONT_REG3.AddCommandSnippet()

# Add missing contact keyopt and Archard Wear Model in workbench using a command snippet.
AWM3 = '''keyopt,cid,9,5
rmodif,cid,10,0.00
rmodif,cid,23,0.001'''
CMD3.AppendText(AWM3)

CONT_REG4 = CONTS.AddContactRegion()
CONT_REG4.SourceLocation = NS_GRP.Children[6]
CONT_REG4.TargetLocation = NS_GRP.Children[7]
CONT_REG4.ContactType=ContactType.Bonded
CONT_REG4.ContactFormulation = ContactFormulation.MPC

CONT_REG5 = CONTS.AddContactRegion()
CONT_REG5.SourceLocation = NS_GRP.Children[9]
CONT_REG5.TargetLocation = NS_GRP.Children[8]
CONT_REG5.ContactType=ContactType.Bonded
CONT_REG5.ContactFormulation = ContactFormulation.MPC

CONT_REG6 = CONTS.AddContactRegion()
CONT_REG6.SourceLocation = NS_GRP.Children[10]
CONT_REG6.TargetLocation = NS_GRP.Children[11]
CONT_REG6.ContactType=ContactType.Frictional
CONT_REG6.FrictionCoefficient = 0.2
CONT_REG6.SmallSliding = ContactSmallSlidingType.Off
CONT_REG6.UpdateStiffness = UpdateContactStiffness.Never
CMD6=CONT_REG6.AddCommandSnippet()
# Add missing contact keyopt and Archard Wear Model in workbench using a command snippet.
AWM6 = '''keyopt,cid,9,5
rmodif,cid,10,0.00
rmodif,cid,23,0.001'''
CMD6.AppendText(AWM6)

# Add contact tool.
#CONT_TOOL = CONN_GRP.AddContactTool()
#CONT_TOOL.AddPenetration()
#CONT_TOOL.AddStatus()
#CONT_TOOL.GenerateInitialContactResults()

# Generate mesh.

Hex_Method = MSH.AddAutomaticMethod()
Hex_Method.Location = all_bodies
Hex_Method.Method = MethodType.HexDominant

BODY_SIZING1=MSH.AddSizing()
BODY_SIZING1.Location=bodies_5
BODY_SIZING1.ElementSize = Quantity(15, "mm")

BODY_SIZING2=MSH.AddSizing()
BODY_SIZING2.Location=shank
BODY_SIZING2.ElementSize = Quantity(7, "mm")

Face_Meshing = MSH.AddFaceMeshing()
Face_Meshing.Location = shank_face
Face_Meshing.MappedMesh = False

Sweep_Method = MSH.AddAutomaticMethod()
Sweep_Method.Location = shank
Sweep_Method.Method = MethodType.Sweep
Sweep_Method.SourceTargetSelection = 2
Sweep_Method.SourceLocation = shank_face
Sweep_Method.TargetLocation = shank_face2

MSH.GenerateMesh()

# Set up analysis settings.
STAT_STRUC_ANA_SETTING.NumberOfSteps = 4
step_index_list = [1]
with Transaction():
    for step_index in step_index_list:
        STAT_STRUC_ANA_SETTING.SetAutomaticTimeStepping(step_index, AutomaticTimeStepping.Off)
STAT_STRUC_ANA_SETTING.Activate()
step_index_list = [1]
with Transaction():
    for step_index in step_index_list:
        STAT_STRUC_ANA_SETTING.SetNumberOfSubSteps(step_index, 2)
STAT_STRUC_ANA_SETTING.Activate()
STAT_STRUC_ANA_SETTING.SolverType = SolverType.Direct
STAT_STRUC_ANA_SETTING.SolverPivotChecking = SolverPivotChecking.Off


# Insert loading and BC.
FIX_SUP=STAT_STRUC.AddFixedSupport()
FIX_SUP.Location=block2_surface

Tabular_Force = STAT_STRUC.AddForce()
Tabular_Force.Location = bottom_surface
Tabular_Force.DefineBy = LoadDefineBy.Components
Tabular_Force.XComponent.Inputs[0].DiscreteValues = [Quantity('0[s]'),Quantity('1[s]'), \
    Quantity('2[s]'),Quantity('3[s]'),Quantity('4[s]')]
Tabular_Force.XComponent.Output.DiscreteValues = [Quantity('0[N]'),Quantity('0[N]'), \
    Quantity('5.e+005[N]'),Quantity('0[N]'),Quantity('-5.e+005[N]')]

Bolt_Pretension = STAT_STRUC.AddBoltPretension()
Bolt_Pretension.Location = shank_surface
Bolt_Pretension.Preload.Inputs[0].DiscreteValues = [Quantity('1[s]'),Quantity('2[s]'), \
    Quantity('3[s]'),Quantity('4[s]')]
Bolt_Pretension.Preload.Output.DiscreteValues = [Quantity('6.1363e+005[N]'), \
    Quantity('0 [N]'),Quantity('0 [N]'),Quantity('0[N]')]
Bolt_Pretension.SetDefineBy(2,BoltLoadDefineBy.Lock)
Bolt_Pretension.SetDefineBy(3,BoltLoadDefineBy.Lock)
Bolt_Pretension.SetDefineBy(4,BoltLoadDefineBy.Lock)

# Insert results.
Post_Contact_Tool = STAT_STRUC_SOLN.AddContactTool()
Post_Contact_Tool.ScopingMethod = GeometryDefineByType.Worksheet

Bolt_Tool = STAT_STRUC_SOLN.AddBoltTool()
Bolt_Working_Load = Bolt_Tool.AddWorkingLoad()

Total_Deformation = STAT_STRUC_SOLN.AddTotalDeformation()
Equivalent_stress_1 = STAT_STRUC_SOLN.AddEquivalentStress()
Equivalent_stress_2 = STAT_STRUC_SOLN.AddEquivalentStress()
Equivalent_stress_2.Location = shank
Force_Reaction_1 = STAT_STRUC_SOLN.AddForceReaction()
Force_Reaction_1.BoundaryConditionSelection = FIX_SUP
Moment_Reaction_2 = STAT_STRUC_SOLN.AddMomentReaction()
Moment_Reaction_2.BoundaryConditionSelection = FIX_SUP

# Set number of processors to 6 using DANSYS. (Optional)
# Num_Cores = STAT_STRUC.SolveConfiguration.SolveProcessSettings.MaxNumberOfCores
# STAT_STRUC.SolveConfiguration.SolveProcessSettings.MaxNumberOfCores = 6

# Solve and validate the results.
STAT_STRUC_SOLN.Solve(True)
STAT_STRUC_SS=STAT_STRUC_SOLN.Status

# Set the isometric view and zoom to fit.
cam = Graphics.Camera
cam.SetSpecificViewOrientation(ViewOrientationType.Iso)
cam.SetFit()

mechdir = STAT_STRUC.Children[0].SolverFilesDirectory
export_path = os.path.join(mechdir, "contact_status.png")
Post_Contact_Tool.Children[0].Activate()
Graphics.ExportImage(export_path, GraphicsImageExportFormat.PNG)

my_results_details = {
    "Total_Deformation": str(Total_Deformation.Maximum),
    "Equivalent_Stress1": str(Equivalent_stress_1.Maximum),
    "Equivalent_Stress2": str(Equivalent_stress_2.Maximum),
}

json.dumps(my_results_details)
"""
)
print(output)

# %%
# Initialize the variable needed for the image directory
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Set the ``image_dir`` variable for later use.
# Make the variable compatible for Windows, Linux, and Docker containers.

# image_directory_modified = project_directory.replace("\\", "\\\\")
mechanical.run_python_script(f"image_dir=ExtAPI.DataModel.AnalysisList[0].WorkingDir")


# Verify the path for image directory.
result_image_dir_server = mechanical.run_python_script(f"image_dir")
print(f"Images are stored on the server at: {result_image_dir_server}")

# %%
# Download the image and plot
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Download one image file from the server to the current working directory and plot
# using matplotlib.


def get_image_path(image_name):
    return os.path.join(result_image_dir_server, image_name)


def display_image(path):
    print(f"Printing {path} using matplotlib")
    image1 = mpimg.imread(path)
    plt.figure(figsize=(15, 15))
    plt.axis("off")
    plt.imshow(image1)
    plt.show()


image_name = "contact_status.png"
image_path_server = get_image_path(image_name)

if image_path_server != "":
    current_working_directory = os.getcwd()

    local_file_path_list = mechanical.download(
        image_path_server, target_dir=current_working_directory
    )
    image_local_path = local_file_path_list[0]
    print(f"Local image path : {image_local_path}")

    display_image(image_local_path)

# %%
# Download output file from solve and print contents
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Download the ``solve.out`` file from the server to the current working
# directory and print the contents. Remove the ``solve.out`` file.


def get_solve_out_path(mechanical):
    """Get the solve out path and return."""
    solve_out_path = ""
    for file_path in mechanical.list_files():
        if file_path.find("solve.out") != -1:
            solve_out_path = file_path
            break

    return solve_out_path


def write_file_contents_to_console(path):
    """Write file contents to console."""
    with open(path, "rt") as file:
        for line in file:
            print(line, end="")


solve_out_path = get_solve_out_path(mechanical)

if solve_out_path != "":
    current_working_directory = os.getcwd()

    mechanical.download(solve_out_path, target_dir=current_working_directory)
    solve_out_local_path = os.path.join(current_working_directory, "solve.out")

    write_file_contents_to_console(solve_out_local_path)

    os.remove(solve_out_local_path)

# %%
# Close mechanical
# ~~~~~~~~~~~~~~~~
# Close the mechanical instance.

mechanical.exit()
