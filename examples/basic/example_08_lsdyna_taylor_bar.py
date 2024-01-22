""".. _ref_example_08_lsdyna_taylor_bar_example:

LS-Dyna analysis
--------------------------

Using supplied files, this example shows how to insert an LS-Dyna analysis
into a new Mechanical session and execute a sequence of Python scripting
commands that define and solve the analysis. Deformation results are then reported
and plastic strain (EPS) animation is exported in the project directory.
"""

###############################################################################
# Download required files
# ~~~~~~~~~~~~~~~~~~~~~~~
# Download the required files. Print the file path for the geometry file.
import os

from PIL import Image
from ansys.mechanical.core import launch_mechanical
from ansys.mechanical.core.examples import download_file
from matplotlib import image as mpimg
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation

geometry_path = download_file("example_08_Taylor_Bar.agdb", "pymechanical", "00_basic")
print(f"Downloaded the geometry file to: {geometry_path}")

###############################################################################
# Launch Mechanical
# ~~~~~~~~~~~~~~~~~
# Launch a new Mechanical session in batch, setting ``cleanup_on_exit`` to
# ``False``. To close this Mechanical session when finished, this example
# must call  the ``mechanical.exit()`` method.

mechanical = launch_mechanical(batch=True, cleanup_on_exit=False)
print(mechanical)

###############################################################################
# Initialize variable for workflow
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Set the ``part_file_path`` variable on the server for later use.
# Make this variable compatible for Windows, Linux, and Docker containers.

project_directory = mechanical.project_directory
print(f"project directory = {project_directory}")
project_directory = project_directory.replace("\\", "\\\\")
mechanical.run_python_script(f"project_directory='{project_directory}'")

# Upload the file to the project directory.
mechanical.upload(file_name=geometry_path, file_location_destination=project_directory)

# Build the path relative to project directory.
base_name = os.path.basename(geometry_path)
combined_path = os.path.join(project_directory, base_name)
part_file_path = combined_path.replace("\\", "\\\\")
mechanical.run_python_script(f"part_file_path='{part_file_path}'")

###############################################################################
# Download required material files
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Download the required file. Print the file path for the material file.

mat_st_path = download_file("example_08_Taylor_Bar_Mat.xml", "pymechanical", "00_basic")
print(f"Downloaded the material file to: {mat_st_path}")

# Upload the file to the project directory.
mechanical.upload(file_name=mat_st_path, file_location_destination=project_directory)

# Build the path relative to project directory.
base_name = os.path.basename(mat_st_path)
combined_path = os.path.join(project_directory, base_name)
mat_file_path = combined_path.replace("\\", "\\\\")
mechanical.run_python_script(f"mat_file_path='{mat_file_path}'")

# Verify the path
result = mechanical.run_python_script("part_file_path")
print(f"part_file_path on server: {result}")

mech_act_code = """
import os
import json

# Import Taylor bar geometry
geometry_import_group = Model.GeometryImportGroup
geometry_import = geometry_import_group.AddGeometryImport()

geometry_import_format = Ansys.Mechanical.DataModel.Enums.GeometryImportPreference.Format.Automatic
geometry_import.Import(part_file_path, geometry_import_format, None)

Model.AddLSDynaAnalysis()
analysis = Model.Analyses[0]

ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardNMMton
ExtAPI.Application.ActiveAngleUnit = AngleUnitType.Radian

MAT = ExtAPI.DataModel.Project.Model.Materials
#MAT.Import(mat_file_path)

# Assign the material
#ExtAPI.DataModel.Project.Model.Geometry.Children[0].Children[0].Material = "Bullet"

# Add Coordinate system

cs = Model.CoordinateSystems
lcs = cs.AddCoordinateSystem()
lcs.Origin = [10.0, 1.5, -10.0]
lcs.PrimaryAxis = CoordinateSystemAxisType.PositiveZAxis
lcs.PrimaryAxisDefineBy = CoordinateSystemAlignmentType.GlobalY
lcs.OriginDefineBy = CoordinateSystemAlignmentType.Fixed

solver  = analysis.Solver

solver.Properties['Step Controls/Endtime'].Value = 3.0E-5

analysis.Activate()

# Add Rigid Wall
rigid_wall = analysis.CreateLoadObject("Rigid Wall", "LSDYNA")
rigid_wall.Properties["Coordinate System"].Value = lcs.ObjectId
ExtAPI.DataModel.Tree.Refresh()

# Adding initial velocity
ic = ExtAPI.DataModel.GetObjectsByName("Initial Conditions")[0]
vel = ic.InsertVelocity()
selection = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
selection.Ids = [ExtAPI.DataModel.GeoData.Assemblies[0].Parts[0].Bodies[0].Id]
vel.Location = selection
vel.DefineBy = LoadDefineBy.Components
vel.YComponent = Quantity(-280000, ExtAPI.DataModel.CurrentUnitFromQuantityName("Velocity"))

# By default quadratic element order in Mechanical - LSDyna supports only Linear
mesh = ExtAPI.DataModel.GetObjectsByName("Mesh")[0]
mesh.ElementOrder = ElementOrder.Linear
mesh.ElementSize = Quantity(0.5, "mm")

# Solve
analysis.Solution.Solve()

# Post-processing
eps = analysis.Solution.AddUserDefinedResult()
eps.Expression = "EPS"
eps.EvaluateAllResults()
eps_max = eps.Maximum
eps_min = eps.Minimum
total_deformation = analysis.Solution.AddTotalDeformation()
total_deformation.EvaluateAllResults()
# Set Camera
Graphics.Camera.FocalPoint = Point([9.0521184381880495,
                                    2.9680547361873595,
                                    -11.52925245328758], 'mm')

Graphics.Camera.ViewVector = Vector3D(0.5358281613965048,
                                      -0.45245539014067604,
                                      0.71286204933850261)
Graphics.Camera.UpVector = Vector3D(-0.59927496479653264,
                                     0.39095266724498329,
                                     0.69858823962485084)

Graphics.Camera.SceneHeight = Quantity(14.66592829617538, 'mm')
Graphics.Camera.SceneWidth = Quantity(8.4673776497126063, 'mm')

# Set Scale factor
true_scale = MechanicalEnums.Graphics.DeformationScaling.True
Graphics.ViewOptions.ResultPreference.DeformationScaling = true_scale

Graphics.ViewOptions.ResultPreference.DeformationScaleMultiplier = 1



# Export an animation
mechdir = ExtAPI.DataModel.AnalysisList[0].WorkingDir
eps.Activate()
animation_export_format = GraphicsAnimationExportFormat.GIF
settings_720p = Ansys.Mechanical.Graphics.AnimationExportSettings()
settings_720p.Width = 1280
settings_720p.Height = 720
anim_file_path = os.path.join(mechdir, "taylor_bar.gif")
eps.ExportAnimation(
    anim_file_path, animation_export_format, settings_720p
)

# Set the isometric view and zoom to fit.
settings_720p = Ansys.Mechanical.Graphics.GraphicsImageExportSettings()
settings_720p.Resolution = (GraphicsResolutionType.EnhancedResolution)
settings_720p.Background = GraphicsBackgroundType.White
settings_720p.Width = 1280
settings_720p.Height = 720
settings_720p.CurrentGraphicsDisplay = False
Graphics.Camera.Pan(Quantity(7, 'mm'),Quantity(4, 'mm'))
total_deformation.Activate()
image_path = os.path.join(mechdir, "totaldeformation.png")
Graphics.ExportImage(image_path, GraphicsImageExportFormat.PNG, settings_720p)

dir_deformation_details = {
"Minimum": str(eps_max),
"Maximum": str(eps_min)
}

json.dumps(dir_deformation_details)
"""
output = mechanical.run_python_script(mech_act_code)
print(output)

# image_directory_modified = project_directory.replace("\\", "\\\\")
mechanical.run_python_script(f"image_dir=ExtAPI.DataModel.AnalysisList[0].WorkingDir")


# Verify the path for image directory.
result_image_dir_server = mechanical.run_python_script(f"image_dir")
print(f"Images are stored on the server at: {result_image_dir_server}")

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


print("Getting solve out path")
solve_out_path = get_solve_out_path(mechanical)
print(f"Solve out path (on remote machine): {solve_out_path}")


if solve_out_path != "":
    current_working_directory = os.getcwd()

    print(f"Performing download request...")
    mechanical.download(solve_out_path, target_dir=current_working_directory)
    solve_out_local_path = os.path.join(current_working_directory, "solve.out")
    print(f"File downloaded locally at {solve_out_local_path}")

    write_file_contents_to_console(solve_out_local_path)
    print("Printed output to console")
    os.remove(solve_out_local_path)

###############################################################################
# Get image and display
# ~~~~~~~~~~~~~~~~~~~~~~


def get_image_path(image_name):
    return os.path.join(result_image_dir_server, image_name)


def display_image(path):
    print(f"Printing {path} using matplotlib")
    image1 = mpimg.imread(path)
    plt.figure(figsize=(15, 15))
    plt.axis("off")
    plt.imshow(image1)
    plt.show()


image_name = "totaldeformation.png"
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
# Get gif and display
# ~~~~~~~~~~~~~~~~~~~

animation_name = "taylor_bar.gif"
animation_server = get_image_path(animation_name)


def update(frame):
    gif.seek(frame)
    img.set_array(gif.convert("RGBA"))
    return [img]


if image_path_server != "":
    current_working_directory = os.getcwd()

    local_file_path_list = mechanical.download(
        animation_server, target_dir=current_working_directory
    )
    image_local_path = local_file_path_list[0]
    print(f"Local image path : {image_local_path}")
    gif = Image.open(image_local_path)
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.axis("off")
    img = ax.imshow(gif.convert("RGBA"))
    ani = FuncAnimation(
        fig, update, frames=range(gif.n_frames), interval=100, repeat=True, blit=True
    )
    plt.show()

###########################################################
# Close Mechanical
# ~~~~~~~~~~~~~~~~
# Close the Mechanical instance.

print("Closing mechanical...")
mechanical.exit()
print("Mechanical closed!")
