""" .. _ref_example_05_td_026:

Nonlinear Analysis of a Rubber Boot Seal Model
----------------------------------------------

Nonlinear Analysis of a Rubber Boot Seal.

Coverage:3D analysis of Nonlinear Analysis of a Rubber Boot Seal.

Rigid-flexible Contact Pair between Rigid Shaft and Rubber Boot.

Ramped effects, Detection Method: On Gauss Point, update contact stiffness at each iteration
Self Contact Pairs at Inner and Outer Surfaces of Rubber Boot.

No Ramped effects, Detection Method: Nodal-Projected Normal From Contact,
update contact stiffness at each iteration

Validation:
Validated Equivalent Stress and Total Deformation results.

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

geometry_path = download_file(
    "example_05_td26_Rubber_Boot_Seal.agdb", "pymechanical", "00_basic"
)
print(f"Downloaded the geometry file to: {geometry_path}")

# Upload the file to the project directory.
mechanical.upload(file_name=geometry_path, file_location_destination=project_directory)

# Build the path relative to project directory.
base_name = os.path.basename(geometry_path)
combined_path = os.path.join(project_directory, base_name)
part_file_path = combined_path.replace("\\", "\\\\")
mechanical.run_python_script(f"part_file_path='{part_file_path}'")

###############################################################################
# Download required Material files
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Download the required files. Print the file path for the material file.

mat_path = download_file("example_05_Boot_Mat.xml", "pymechanical", "00_basic")
print(f"Downloaded the material file to: {mat_path}")

# Upload the file to the project directory.
mechanical.upload(file_name=mat_path, file_location_destination=project_directory)

# Build the path relative to project directory.
base_name = os.path.basename(mat_path)
combined_path = os.path.join(project_directory, base_name)
mat_part_file_path = combined_path.replace("\\", "\\\\")
mechanical.run_python_script(f"mat_part_file_path='{mat_part_file_path}'")

# Verify the path.
result = mechanical.run_python_script("part_file_path")
print(f"part_file_path on server: {result}")

###################################################################################
# Run the script
# ~~~~~~~~~~~~~~
# Run the Mechanical script to attach the geometry and set up and solve the
# analysis.

output = mechanical.run_python_script(
    """
import json
import os

# Section 1: Read geometry and material information from the JSON file.
geometry_import_group_11 = Model.GeometryImportGroup
geometry_import_12 = geometry_import_group_11.AddGeometryImport()
geometry_import_12_format = Ansys.Mechanical.DataModel.Enums.GeometryImportPreference. \
    Format.Automatic
geometry_import_12_preferences = Ansys.ACT.Mechanical.Utilities.GeometryImportPreferences()
geometry_import_12_preferences.ProcessNamedSelections = True
geometry_import_12_preferences.ProcessCoordinateSystems = True
geometry_import_12.Import(part_file_path, geometry_import_12_format,
                          geometry_import_12_preferences)

#materials = ExtAPI.DataModel.Project.Model.Materials
#materials.Import(mat_part_file_path)

# Section 2: Set up the unit system.
ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardNMM
ExtAPI.Application.ActiveAngleUnit = AngleUnitType.Radian
GEOM = Model.Geometry
PRT1 = [x for x in ExtAPI.DataModel.Tree.AllObjects if x.Name == 'Part'][0]
PRT2 = [x for x in ExtAPI.DataModel.Tree.AllObjects if x.Name == 'Solid'][1]
CS_GRP = Model.CoordinateSystems
GCS = CS_GRP.Children[0]

Model.AddStaticStructuralAnalysis()
STAT_STRUC = Model.Analyses[0]
ANA_SETTING = STAT_STRUC.Children[0]
STAT_STRUC_SOLN = STAT_STRUC.Solution
SOLN_INFO = STAT_STRUC_SOLN.SolutionInformation

# Section 3: Define named selection and coordinate system.
NS_GRP = ExtAPI.DataModel.Project.Model.NamedSelections
TOP_FACE = \
    [i for i in NS_GRP.GetChildren[Ansys.ACT.Automation.Mechanical.NamedSelection](True)
     if i.Name == 'Top_Face'][0]
BOTTOM_FACE = \
    [i for i in NS_GRP.GetChildren[Ansys.ACT.Automation.Mechanical.NamedSelection](True)
     if i.Name == 'Bottom_Face'][0]
SYMM_FACES30 = \
    [i for i in NS_GRP.GetChildren[Ansys.ACT.Automation.Mechanical.NamedSelection](True)
     if i.Name == 'Symm_Faces30'][0]
FACES2 = [i for i in NS_GRP.GetChildren[Ansys.ACT.Automation.Mechanical.NamedSelection](True)
          if i.Name == 'Faces2'][0]
CYL_FACES2 = \
    [i for i in NS_GRP.GetChildren[Ansys.ACT.Automation.Mechanical.NamedSelection](True)
     if i.Name == 'Cyl_Faces2'][0]
RUBBER_BODIES30 = \
    [i for i in NS_GRP.GetChildren[Ansys.ACT.Automation.Mechanical.NamedSelection](True)
     if i.Name == 'Rubber_Bodies30'][0]
INNER_FACES30 = \
    [i for i in NS_GRP.GetChildren[Ansys.ACT.Automation.Mechanical.NamedSelection](True)
     if i.Name == 'Inner_Faces30'][0]
OUTER_FACES30 = \
    [i for i in NS_GRP.GetChildren[Ansys.ACT.Automation.Mechanical.NamedSelection](True)
     if i.Name == 'Outer_Faces30'][0]
SHAFT_FACE = \
    [i for i in NS_GRP.GetChildren[Ansys.ACT.Automation.Mechanical.NamedSelection](True)
     if i.Name == 'Shaft_Face'][0]
SYMM_FACES15 = \
    [i for i in NS_GRP.GetChildren[Ansys.ACT.Automation.Mechanical.NamedSelection](True)
     if i.Name == 'Symm_Faces15'][0]

LCS1 = CS_GRP.AddCoordinateSystem()
LCS1.OriginY = Quantity('97[mm]')

# Section 4: Define material.
#PRT1.Material = 'Boot'
PRT2.StiffnessBehavior = StiffnessBehavior.Rigid

# Section 5: Define connections.
CONN_GRP = ExtAPI.DataModel.Project.Model.Connections
CONT_REG1 = CONN_GRP.AddContactRegion()
CONT_REG1.TargetLocation = SHAFT_FACE
CONT_REG1.SourceLocation = INNER_FACES30
CONT_REG1.ContactType = ContactType.Frictional
CONT_REG1.FrictionCoefficient = 0.2
CONT_REG1.Behavior = ContactBehavior.Asymmetric
CONT_REG1.SmallSliding = ContactSmallSlidingType.Off
CONT_REG1.DetectionMethod = ContactDetectionPoint.OnGaussPoint
CONT_REG1.UpdateStiffness = UpdateContactStiffness.EachIteration
CONT_REG1.InterfaceTreatment = ContactInitialEffect.AddOffsetRampedEffects
CONT_REG1.TargetGeometryCorrection = TargetCorrection.Smoothing
CONT_REG1.TargetOrientation = TargetOrientation.Cylinder
CONT_REG1.TargetStartingPoint = GCS
CONT_REG1.TargetEndingPoint = LCS1

CONTS = CONN_GRP.Children[0]
CONT_REG2 = CONTS.AddContactRegion()
CONT_REG2.SourceLocation = INNER_FACES30
CONT_REG2.TargetLocation = INNER_FACES30
CONT_REG2.ContactType = ContactType.Frictional
CONT_REG2.FrictionCoefficient = 0.2
CONT_REG2.Behavior = ContactBehavior.Asymmetric
CONT_REG2.SmallSliding = ContactSmallSlidingType.Off
CONT_REG2.DetectionMethod = ContactDetectionPoint.NodalProjectedNormalFromContact
CONT_REG2.UpdateStiffness = UpdateContactStiffness.EachIteration
CONT_REG2.NormalStiffnessValueType = ElementControlsNormalStiffnessType.Factor
CONT_REG2.NormalStiffnessFactor = 1

CONT_REG3 = CONTS.AddContactRegion()
CONT_REG3.SourceLocation = OUTER_FACES30
CONT_REG3.TargetLocation = OUTER_FACES30
CONT_REG3.ContactType = ContactType.Frictional
CONT_REG3.FrictionCoefficient = 0.2
CONT_REG3.Behavior = ContactBehavior.Asymmetric
CONT_REG3.SmallSliding = ContactSmallSlidingType.Off
CONT_REG3.DetectionMethod = ContactDetectionPoint.NodalProjectedNormalFromContact
CONT_REG3.UpdateStiffness = UpdateContactStiffness.EachIteration
CONT_REG3.NormalStiffnessValueType = ElementControlsNormalStiffnessType.Factor
CONT_REG3.NormalStiffnessFactor = 1

# Section 6: Define mesh controls.
MSH = Model.Mesh
FACE_MSH = MSH.AddFaceMeshing()
FACE_MSH.Location = SHAFT_FACE
FACE_MSH.InternalNumberOfDivisions = 1

MSH_SIZE = MSH.AddSizing()
MSH_SIZE.Location = SYMM_FACES15
MSH_SIZE.ElementSize = Quantity('2 [mm]')

MSH.ElementOrder = ElementOrder.Linear
MSH.Resolution = 2
MSH.GenerateMesh()

# Section 7: Define remote points' rigid behaviors and scope them
# to the top and bottom faces of rigid shaft.
RMPT01 = Model.AddRemotePoint()
RMPT01.Location = BOTTOM_FACE
RMPT01.Behavior = LoadBehavior.Rigid

RMPT02 = Model.AddRemotePoint()
RMPT02.Location = TOP_FACE
RMPT02.Behavior = LoadBehavior.Rigid

# Section 8: Define analysis settings and set up loads and supports.
ANA_SETTING.Activate()
ANA_SETTING.LargeDeflection = True
ANA_SETTING.Stabilization = StabilizationType.Off

#ANA_SETTING.NumberOfSteps = 3
ANA_SETTING.NumberOfSteps = 2
ANA_SETTING.CurrentStepNumber = 1
ANA_SETTING.AutomaticTimeStepping = AutomaticTimeStepping.On
ANA_SETTING.DefineBy = TimeStepDefineByType.Substeps
ANA_SETTING.InitialSubsteps = 5
ANA_SETTING.MinimumSubsteps = 5
ANA_SETTING.MaximumSubsteps = 1000
ANA_SETTING.StoreResultsAt = TimePointsOptions.EquallySpacedPoints
ANA_SETTING.StoreResulsAtValue = 5

ANA_SETTING.CurrentStepNumber = 2
ANA_SETTING.AutomaticTimeStepping = AutomaticTimeStepping.On
ANA_SETTING.DefineBy = TimeStepDefineByType.Substeps
ANA_SETTING.InitialSubsteps = 10
ANA_SETTING.MinimumSubsteps = 10
ANA_SETTING.MaximumSubsteps = 1000
ANA_SETTING.StoreResultsAt = TimePointsOptions.EquallySpacedPoints
ANA_SETTING.StoreResulsAtValue = 10

ANA_SETTING.CurrentStepNumber = 3
ANA_SETTING.AutomaticTimeStepping = AutomaticTimeStepping.On
ANA_SETTING.DefineBy = TimeStepDefineByType.Substeps
ANA_SETTING.InitialSubsteps = 30
ANA_SETTING.MinimumSubsteps = 30
ANA_SETTING.MaximumSubsteps = 1000
ANA_SETTING.StoreResultsAt = TimePointsOptions.EquallySpacedPoints
ANA_SETTING.StoreResulsAtValue = 20

SOLN_INFO.NewtonRaphsonResiduals = 4

REM_DISP = STAT_STRUC.AddRemoteDisplacement()
REM_DISP.Location = RMPT01
REM_DISP.XComponent.Inputs[0].DiscreteValues = [Quantity("0 [s]"), Quantity("1 [s]"),
                                                Quantity("2 [s]"), Quantity("3 [s]")]
REM_DISP.XComponent.Output.DiscreteValues = [Quantity("0 [mm]"), Quantity("0 [mm]"),
                                             Quantity("0 [mm]"), Quantity("0 [mm]")]
REM_DISP.YComponent.Inputs[0].DiscreteValues = [Quantity("0 [s]"), Quantity("1 [s]"),
                                                Quantity("2 [s]"), Quantity("3 [s]")]
REM_DISP.YComponent.Output.DiscreteValues = [Quantity("0 [mm]"), Quantity("0 [mm]"),
                                             Quantity("-10 [mm]"), Quantity("-10 [mm]")]
REM_DISP.ZComponent.Inputs[0].DiscreteValues = [Quantity("0 [s]"), Quantity("1 [s]"),
                                                Quantity("2 [s]"), Quantity("3 [s]")]
REM_DISP.ZComponent.Output.DiscreteValues = [Quantity("0 [mm]"), Quantity("0 [mm]"),
                                             Quantity("0 [mm]"), Quantity("0 [mm]")]

REM_DISP.RotationX.Inputs[0].DiscreteValues = [Quantity("0 [s]"), Quantity("1 [s]"),
                                               Quantity("2 [s]"), Quantity("3 [s]")]
REM_DISP.RotationX.Output.DiscreteValues = [Quantity("0 [rad]"), Quantity("0 [rad]"),
                                            Quantity("0 [rad]"), Quantity("0 [rad]")]
REM_DISP.RotationY.Inputs[0].DiscreteValues = [Quantity("0 [s]"), Quantity("1 [s]"),
                                               Quantity("2 [s]"), Quantity("3 [s]")]
REM_DISP.RotationY.Output.DiscreteValues = [Quantity("0 [rad]"), Quantity("0 [rad]"),
                                            Quantity("0 [rad]"), Quantity("0 [rad]")]
REM_DISP.RotationZ.Inputs[0].DiscreteValues = [Quantity("0 [s]"), Quantity("1 [s]"),
                                               Quantity("2 [s]"), Quantity("3 [s]")]
REM_DISP.RotationZ.Output.DiscreteValues = [Quantity("0 [rad]"), Quantity("0 [rad]"),
                                            Quantity("0 [rad]"), Quantity("0.55 [rad]")]

FRIC_SUP01 = STAT_STRUC.AddFrictionlessSupport()
FRIC_SUP01.Location = SYMM_FACES30
FRIC_SUP01.Name = "Symmetry_BC"
FRIC_SUP02 = STAT_STRUC.AddFrictionlessSupport()
FRIC_SUP02.Location = FACES2
FRIC_SUP02.Name = "Boot_Bottom_BC"
FRIC_SUP03 = STAT_STRUC.AddFrictionlessSupport()
FRIC_SUP03.Location = CYL_FACES2
FRIC_SUP03.Name = "Boot_Radial_BC"

# Section 9: Add total deformation and equivalent stress.
TOT_DEF = STAT_STRUC.Solution.AddTotalDeformation()
TOT_DEF.Location = RUBBER_BODIES30

EQV_STRS = STAT_STRUC.Solution.AddEquivalentStress()
EQV_STRS.Location = RUBBER_BODIES30

# Section 10: Set the number of processors to 6 using DANSYS.
#testval2 = STAT_STRUC.SolveConfiguration.SolveProcessSettings.MaxNumberOfCores
#STAT_STRUC.SolveConfiguration.SolveProcessSettings.MaxNumberOfCores = 6

# Section 11: Solve for the normal stiffness value set to 1 for self contacts.
# between flexible rubber boot
STAT_STRUC.Solution.Solve(True)

# Section 12: Set isometric view and zoom to fit.
cam = Graphics.Camera
cam.SetSpecificViewOrientation(ViewOrientationType.Iso)
cam.SetFit()

# Section 13: Store post-processing images.
mechdir = STAT_STRUC.Children[0].SolverFilesDirectory
export_path = os.path.join(mechdir, "total_deformation.png")
TOT_DEF.Activate()
Graphics.ExportImage(export_path, GraphicsImageExportFormat.PNG)

export_path2 = os.path.join(mechdir, "equivalent_stress.png")
EQV_STRS.Activate()
Graphics.ExportImage(export_path2, GraphicsImageExportFormat.PNG)

my_results_details = {
    "Equivalent_Stress": str(EQV_STRS.Maximum),
    "Total_Deformation": str(TOT_DEF.Maximum),
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


image_names = ["total_deformation.png", "equivalent_stress.png"]
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
