""".. _ref_example_07_td_043:

Contact Surface Wear Simulation
-------------------------------

Contact Surface Wear Simulation.
UNIT System: NMM.

Coverage:
Archard wear model
Wear on One Contact Surface (Asymmetric Contact)

Problem Description:
A hemispherical ring of copper with radius = 30 mm
rotates on a flat ring of steel with inner radius = 50 mm
and outer radius = 150 mm. The hemispherical ring touches
the flat ring at the center from the axis of rotation at
100 mm). The hemispherical ring is subjected to a pressure
load of 4000 N/mm2 and is rotating with a frequency of 100,000
revolutions/sec. Sliding of the hemispherical ring on the flat
ring causes wear in the rings.

Validation:
The total deformation and Normal stress in loading direction are
validated before wear and after wear and also Contact Pressure
before wear and after wear are validated.

"""

###############################################################################
# Import necessary libraries
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
import os

from ansys.mechanical.core import launch_mechanical
from ansys.mechanical.core.examples import download_file
from matplotlib import image as mpimg
from matplotlib import pyplot as plt

###############################################################################
# Launch Mechanical
# ~~~~~~~~~~~~~~~~~
# Launch a new Mechanical session in batch, setting the ``cleanup_on_exit``
# argument to ``False``. To close this Mechanical session when finished,
# this example must call  the ``mechanical.exit()`` method.

mechanical = launch_mechanical(batch=True, cleanup_on_exit=False)
print(mechanical)

###############################################################################
# Initialize variable for workflow
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Set the ``part_file_path`` variable on the server for later use.
# Make this variable compatible for Windows, Linux, and Docker containers.

project_directory = mechanical.project_directory
print(f"project directory = {project_directory}")

###############################################################################
# Download required Geometry file
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Download the required file. Print the file path for the geometry file.

geometry_path = download_file("example_07_td43_wear.agdb", "pymechanical", "00_basic")
print(f"Downloaded the geometry file to: {geometry_path}")

# Upload the file to the project directory.
mechanical.upload(file_name=geometry_path, file_location_destination=project_directory)

# Build the path relative to project directory.
base_name = os.path.basename(geometry_path)
combined_path = os.path.join(project_directory, base_name)
part_file_path = combined_path.replace("\\", "\\\\")
mechanical.run_python_script(f"part_file_path='{part_file_path}'")

###############################################################################
# Download required material files
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Download the required files. Print the file path for the material file.

mat_cop_path = download_file("example_07_Mat_Copper.xml", "pymechanical", "00_basic")
print(f"Downloaded the material file to: {mat_cop_path}")

# Upload the file to the project directory.
mechanical.upload(file_name=mat_cop_path, file_location_destination=project_directory)

# Build the path relative to project directory.
base_name = os.path.basename(mat_cop_path)
combined_path = os.path.join(project_directory, base_name)
mat_Copper_file_path = combined_path.replace("\\", "\\\\")
mechanical.run_python_script(f"mat_Copper_file_path='{mat_Copper_file_path}'")

mat_st_path = download_file("example_07_Mat_Steel.xml", "pymechanical", "00_basic")
print(f"Downloaded the material file to: {mat_st_path}")

# Upload the file to the project directory.
mechanical.upload(file_name=mat_st_path, file_location_destination=project_directory)

# Build the path relative to project directory.
base_name = os.path.basename(mat_st_path)
combined_path = os.path.join(project_directory, base_name)
mat_Steel_file_path = combined_path.replace("\\", "\\\\")
mechanical.run_python_script(f"mat_Steel_file_path='{mat_Steel_file_path}'")

# Verify the path.
result = mechanical.run_python_script("part_file_path")
print(f"part_file_path on server: {result}")

###################################################################################
# Run the script
# ~~~~~~~~~~~~~~
# Run the Mechanical script to attach the geometry, set up, and solve the
# analysis.

output = mechanical.run_python_script(
    """
import json
import os
import context_menu

# Section 1: Read geometry and material information.
geometry_import_group_11 = Model.GeometryImportGroup
geometry_import_12 = geometry_import_group_11.AddGeometryImport()
geometry_import_12_format = Ansys.Mechanical.DataModel.Enums.GeometryImportPreference.\
    Format.Automatic
geometry_import_12_preferences = Ansys.ACT.Mechanical.Utilities.GeometryImportPreferences()
geometry_import_12_preferences.ProcessNamedSelections = True
geometry_import_12_preferences.ProcessCoordinateSystems = True
geometry_import_12.Import(part_file_path,geometry_import_12_format,geometry_import_12_preferences)

MAT = ExtAPI.DataModel.Project.Model.Materials
MAT.Import(mat_Copper_file_path)
MAT.Import(mat_Steel_file_path)

# Section 2: Set up the unit system.
ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardNMM

# Section 3: Store all main tree nodes as variables.
MODEL = ExtAPI.DataModel.Project.Model
GEOM = ExtAPI.DataModel.Project.Model.Geometry
CS_GRP = ExtAPI.DataModel.Project.Model.CoordinateSystems
CONN_GRP = ExtAPI.DataModel.Project.Model.Connections
MSH = ExtAPI.DataModel.Project.Model.Mesh
NS_GRP = ExtAPI.DataModel.Project.Model.NamedSelections

Model.AddStaticStructuralAnalysis()
STAT_STRUC = Model.Analyses[0]
STAT_STRUC_SOLN = STAT_STRUC.Solution
STAT_STRUC_ANA_SETTING = STAT_STRUC.Children[0]

# Section 4: Store name selection.
CURVE_NS = [x for x in ExtAPI.DataModel.Tree.AllObjects if x.Name == 'curve'][0]
DIA_NS = [x for x in ExtAPI.DataModel.Tree.AllObjects if x.Name == 'dia'][0]
VER_EDGE1 = [x for x in ExtAPI.DataModel.Tree.AllObjects if x.Name == 'v1'][0]
VER_EDGE2 = [x for x in ExtAPI.DataModel.Tree.AllObjects if x.Name == 'v2'][0]
HOR_EDGE1 = [x for x in ExtAPI.DataModel.Tree.AllObjects if x.Name == 'h1'][0]
HOR_EDGE2 = [x for x in ExtAPI.DataModel.Tree.AllObjects if x.Name == 'h2'][0]
ALL_BODIES_NS = [x for x in ExtAPI.DataModel.Tree.AllObjects if x.Name == 'all_bodies'][0]

# Section 5: Assign material to bodies and change behavior to axisymmetric.
GEOM.Model2DBehavior=Model2DBehavior.AxiSymmetric

SURFACE1=GEOM.Children[0].Children[0]
SURFACE1.Material="Steel"
SURFACE1.Dimension = ShellBodyDimension.Two_D

SURFACE2=GEOM.Children[1].Children[0]
SURFACE2.Material="Copper"
SURFACE2.Dimension = ShellBodyDimension.Two_D

# Section 6: Change contact settings and add a command snippet to use Archard Wear Model.
CONT_REG = CONN_GRP.AddContactRegion()
CONT_REG.SourceLocation = NS_GRP.Children[6]
CONT_REG.TargetLocation = NS_GRP.Children[3]
#CONT_REG.FlipContactTarget()
CONT_REG.ContactType=ContactType.Frictionless
CONT_REG.Behavior=ContactBehavior.Asymmetric
CONT_REG.ContactFormulation=ContactFormulation.AugmentedLagrange
CONT_REG.DetectionMethod=ContactDetectionPoint.NodalNormalToTarget
# Add missing contact keyopt and Archard Wear Model in workbench using command snippet.
AWM = '''keyo,cid,5,1
keyo,cid,10,2
pi=acos(-1)
slide_velocity=1e5
Uring_offset=100
kcopper=10e-13*slide_velocity*2*pi*Uring_offset
TB,WEAR,cid,,,ARCD
TBFIELD,TIME,0
TBDATA,1,0,1,1,0,0
TBFIELD,TIME,1
TBDATA,1,0,1,1,0,0
TBFIELD,TIME,1.01
TBDATA,1,kcopper,1,1,0,0
TBFIELD,TIME,4
TBDATA,1,kcopper,1,1,0,0'''
CMD1=CONT_REG.AddCommandSnippet()
CMD1.AppendText(AWM)

# Section 7: Insert remote point.
REM_PT=MODEL.AddRemotePoint()
REM_PT.Location=DIA_NS
REM_PT.Behavior=LoadBehavior.Rigid

# Section 8: Generate mesh.
MSH.ElementOrder=ElementOrder.Linear
MSH.ElementSize=Quantity('1 [mm]')

EDGE_SIZING1=MSH.AddSizing()
EDGE_SIZING1.Location=HOR_EDGE1
EDGE_SIZING1.Type=SizingType.NumberOfDivisions
EDGE_SIZING1.NumberOfDivisions=70

EDGE_SIZING2=MSH.AddSizing()
EDGE_SIZING2.Location=HOR_EDGE2
EDGE_SIZING2.Type=SizingType.NumberOfDivisions
EDGE_SIZING2.NumberOfDivisions=70

EDGE_SIZING3=MSH.AddSizing()
EDGE_SIZING3.Location=VER_EDGE1
EDGE_SIZING3.Type=SizingType.NumberOfDivisions
EDGE_SIZING3.NumberOfDivisions=35

EDGE_SIZING4=MSH.AddSizing()
EDGE_SIZING4.Location=VER_EDGE2
EDGE_SIZING4.Type=SizingType.NumberOfDivisions
EDGE_SIZING4.NumberOfDivisions=35

EDGE_SIZING5=MSH.AddSizing()
EDGE_SIZING5.Location=DIA_NS
EDGE_SIZING5.Type=SizingType.NumberOfDivisions
EDGE_SIZING5.NumberOfDivisions=40

EDGE_SIZING6=MSH.AddSizing()
EDGE_SIZING6.Location=CURVE_NS
EDGE_SIZING6.Type=SizingType.NumberOfDivisions
EDGE_SIZING6.NumberOfDivisions=60

MSH.GenerateMesh()

# Section 9: Set up analysis settings.
STAT_STRUC_ANA_SETTING.NumberOfSteps=2
STAT_STRUC_ANA_SETTING.CurrentStepNumber=1
STAT_STRUC_ANA_SETTING.AutomaticTimeStepping=AutomaticTimeStepping.On
STAT_STRUC_ANA_SETTING.DefineBy=TimeStepDefineByType.Time
STAT_STRUC_ANA_SETTING.InitialTimeStep=Quantity("0.1 [s]")
STAT_STRUC_ANA_SETTING.MinimumTimeStep=Quantity("0.0001 [s]")
STAT_STRUC_ANA_SETTING.MaximumTimeStep=Quantity("1 [s]")
STAT_STRUC_ANA_SETTING.CurrentStepNumber=2
STAT_STRUC_ANA_SETTING.Activate()
STAT_STRUC_ANA_SETTING.StepEndTime=Quantity("4 [s]")
STAT_STRUC_ANA_SETTING.AutomaticTimeStepping=AutomaticTimeStepping.On
STAT_STRUC_ANA_SETTING.DefineBy=TimeStepDefineByType.Time
STAT_STRUC_ANA_SETTING.InitialTimeStep=Quantity("0.01 [s]")
STAT_STRUC_ANA_SETTING.MinimumTimeStep=Quantity("0.000001 [s]")
STAT_STRUC_ANA_SETTING.MaximumTimeStep=Quantity("0.02 [s]")

STAT_STRUC_ANA_SETTING.LargeDeflection=True

# Section 10: Insert loading and BC.
FIX_SUP=STAT_STRUC.AddFixedSupport()
FIX_SUP.Location=HOR_EDGE1

REM_DISP=STAT_STRUC.AddRemoteDisplacement()
REM_DISP.Location=REM_PT
REM_DISP.XComponent.Output.DiscreteValues=[Quantity('0[mm]')]
REM_DISP.RotationZ.Output.DiscreteValues=[Quantity('0[deg]')]

REM_FRC=STAT_STRUC.AddRemoteForce()
REM_FRC.Location=REM_PT
REM_FRC.DefineBy=LoadDefineBy.Components
REM_FRC.YComponent.Output.DiscreteValues=[Quantity("-150796320 [N]")]

#Nonlinear Adaptivity does not support contact criterion yet hence command snippet used
NLAD = '''NLADAPTIVE,all,add,contact,wear,0.50
NLADAPTIVE,all,on,all,all,1,,4
NLADAPTIVE,all,list,all,all'''
CMD2=STAT_STRUC.AddCommandSnippet()
CMD2.AppendText(NLAD)
CMD2.StepSelectionMode=SequenceSelectionType.All

# Section 11: Insert results.
TOT_DEF=STAT_STRUC_SOLN.AddTotalDeformation()

NORM_STRS1=STAT_STRUC_SOLN.AddNormalStress()
NORM_STRS1.NormalOrientation=NormalOrientationType.YAxis
NORM_STRS1.DisplayTime=Quantity('1 [s]')
NORM_STRS1.DisplayOption=ResultAveragingType.Unaveraged

NORM_STRS2=STAT_STRUC_SOLN.AddNormalStress()
NORM_STRS2.NormalOrientation=NormalOrientationType.YAxis
NORM_STRS2.DisplayTime=Quantity('4 [s]')
NORM_STRS2.DisplayOption=ResultAveragingType.Unaveraged

CONT_TOOL=STAT_STRUC_SOLN.AddContactTool()
CONT_TOOL.ScopingMethod=GeometryDefineByType.Geometry
SEL1=ExtAPI.SelectionManager.AddSelection(ALL_BODIES_NS)
SEL2=ExtAPI.SelectionManager.CurrentSelection
CONT_TOOL.Location=SEL2
ExtAPI.SelectionManager.ClearSelection()
CONT_PRES1=CONT_TOOL.AddPressure()
CONT_PRES1.DisplayTime=Quantity('1 [s]')

CONT_PRES2=CONT_TOOL.AddPressure()
CONT_PRES2.DisplayTime=Quantity('4 [s]')

# Section 12: Set the number of processors to 6 using DANSYS.
#testval2 = STAT_STRUC.SolveConfiguration.SolveProcessSettings.MaxNumberOfCores
#STAT_STRUC.SolveConfiguration.SolveProcessSettings.MaxNumberOfCores = 6

# Section 13: Solve and validate the results.
STAT_STRUC_SOLN.Solve(True)
STAT_STRUC_SS=STAT_STRUC_SOLN.Status

# Section 14: Store post-processing images.

# Set front view and zoom to fit.
cam = Graphics.Camera
cam.SetSpecificViewOrientation(ViewOrientationType.Front)
cam.SetFit()

mechdir = STAT_STRUC.Children[0].SolverFilesDirectory
export_path = os.path.join(mechdir, "stress.png")
NORM_STRS2.Activate()
Graphics.ExportImage(export_path, GraphicsImageExportFormat.PNG)

export_path2 = os.path.join(mechdir, "contact_pres.png")
CONT_PRES2.Activate()
Graphics.ExportImage(export_path2, GraphicsImageExportFormat.PNG)

my_results_details = {
    "Normal_Stress1": str(NORM_STRS1.Minimum),
    "Normal_Stress2": str(NORM_STRS2.Minimum),
    "Contact_Pressure1": str(CONT_PRES1.Maximum),
    "Contact_Pressure2": str(CONT_PRES2.Maximum),
}

json.dumps(my_results_details)
"""
)
print(output)

###################################################################################
# Initialize the variable needed for the image directory
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Set the ``image_dir`` variable for later use.
# Make the variable compatible for Windows, Linux, and Docker containers.

# image_directory_modified = project_directory.replace("\\", "\\\\")
mechanical.run_python_script(f"image_dir=ExtAPI.DataModel.AnalysisList[0].WorkingDir")


# Verify the path for image directory.
result_image_dir_server = mechanical.run_python_script(f"image_dir")
print(f"Images are stored on the server at: {result_image_dir_server}")

###############################################################################
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


image_names = ["stress.png", "contact_pres.png"]
for image_name in image_names:
    image_path_server = get_image_path(image_name)

    if image_path_server != "":
        current_working_directory = os.getcwd()

        local_file_path_list = mechanical.download(
            image_path_server, target_dir=current_working_directory
        )
        image_local_path = local_file_path_list[0]
        print(f"Local image path : {image_local_path}")

        display_image(image_local_path)

###############################################################################
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

###########################################################
# Close Mechanical
# ~~~~~~~~~~~~~~~~
# Close the Mechanical instance.

mechanical.exit()
