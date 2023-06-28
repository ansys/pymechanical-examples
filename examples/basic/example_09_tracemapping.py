""".. _ref_example_06:

Trace Mapping Example Demonstration
---------------------------------------------------------------------------------

Using supplied files, this example shows how to import tracemap data  into a
static structural analysis of  a new Mechanical session and execute a sequence of
Python scripting commands that mesh the model and export an image.

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

###############################################################################
# Download four required files :
# geometry file , def file , copper alloy material file, fr4 material file
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Download the required file. Print the file path for the geometry file.

all_input_files = {
    "geometry file name": "example_09_pcb.agdb",
    "def file": "example_09_edb.def",
    "copper alloy material file": "example_09_mat_copper_alloy.xml",
    "fr4 material  file": "example_09_mat_fr4.xml",
}

all_input_files = {
    "geometry_file_name": "example_01_geometry.agdb",
    "def_file": "example_04_bicycle_crank_231.mechpz",
    "copper_alloy_material_file": "example_06_Mat_Copper.xml",
    "fr4_material_file": "example_06_Mat_Steel.xml",
}


for file_type, file_name in all_input_files.items():
    file_path = download_file(file_name, "pymechanical", "00_basic")
    print(f"Downloaded the {file_type} to: {file_path}")
    # Upload the file to the project directory.
    mechanical.upload(file_name=file_path, file_location_destination=project_directory)
    # Build the path relative to project directory.
    base_name = os.path.basename(file_path)
    combined_path = os.path.join(project_directory, base_name)
    part_file_path = combined_path.replace("\\", "\\\\")
    mechanical.run_python_script(f"{file_type} = '{part_file_path}'")
    # ----------------------- Verify the path-------------------
    result = mechanical.run_python_script("'{file_type}'")
    print(f"path of {file_type} on server: {result}")

mechdat_final = "remote.mechdat"
mechanical.run_python_script(f"final_mechdat_filename='{mechdat_final}'")

png_image_name = "myplot.png"
mechanical.run_python_script(f"image_name='{png_image_name}'")

output = mechanical.run_python_script(
    """
import os

# mechdat_file_path = os.path.join(os.getcwd(), final_mechdat_filename).replace("\\", "//")
mechdat_file_path = os.path.join(os.getcwd(), final_mechdat_filename)

# Imports a geometry file into the active model.
geometry_import = Model.GeometryImportGroup.AddGeometryImport()
geometry_import_format = (
    Ansys.Mechanical.DataModel.Enums.GeometryImportPreference.Format.Automatic
)
geometry_import_preferences = Ansys.ACT.Mechanical.Utilities.GeometryImportPreferences()
geometry_import_preferences.ProcessNamedSelections = True
geometry_import_preferences.NamedSelectionKey = "NS"
geometry_import.Import(
    geometry_file_name, geometry_import_format, geometry_import_preferences
)


print("geometry import : Done ")

# Static Structural Analysis
analysis = Model.AddStaticStructuralAnalysis()
print(analysis)

ExtAPI.DataModel.Project.UnitSystem = UserUnitSystemType.StandardNMM


materials = ExtAPI.DataModel.Project.Model.Materials
materials.Import(copper_alloy_material_file)
materials.Import(fr4_material_file)

# ExtAPI.DataModel.Project.Save(mechdat_file_path)

board_bodyids = []
component_bodyids = []
geo = ExtAPI.DataModel.GeoData
mesh = ExtAPI.DataModel.Project.Model.Mesh
for asm in geo.Assemblies:
    for part in asm.Parts:
        for body in part.Bodies:
            if body.Name[:9] != "Component":
                board_bodyids.append(body.Id)
            else:
                component_bodyids.append(body.Id)


parts = ExtAPI.DataModel.Project.Model.Geometry.Children  # list of parts
for part in parts:
    for body in part.Children:
        body.Material = "Copper Alloy" if body.Name[:9] == "Component" else "FR-4"


def create_named_selection_from_id_list(ns_name, list_of_body_ids):
    selection_manager = ExtAPI.SelectionManager
    selection = ExtAPI.SelectionManager.CreateSelectionInfo(
        SelectionTypeEnum.GeometryEntities
    )
    selection.Ids = list_of_body_ids
    selection_manager.NewSelection(selection)

    model = ExtAPI.DataModel.Project.Model
    named_sel = model.AddNamedSelection()
    named_sel.Name = ns_name
    named_sel.Location = selection
    selection_manager.ClearSelection()


create_named_selection_from_id_list("board_layers", board_bodyids)
create_named_selection_from_id_list("components", component_bodyids)

selection_manager = ExtAPI.SelectionManager
selection = ExtAPI.SelectionManager.CreateSelectionInfo(
    SelectionTypeEnum.GeometryEntities
)
selection.Ids = board_bodyids
selection_manager.NewSelection(selection)

mesh = ExtAPI.DataModel.Project.Model.Mesh

mesh_method = mesh.AddAutomaticMethod()
mesh_method.Location = selection
mesh_method.Method = MethodType.Sweep
mesh_method.ElementOrder = ElementOrder.Linear
mesh_method.SweepNumberDivisions = 1

mesh_sizing = mesh.AddSizing()
mesh_sizing.ElementSize = Quantity("0.25 [mm]")
mesh.GenerateMesh()


external_data_files = Ansys.Mechanical.ExternalData.ExternalDataFileCollection()
external_data_files.SaveFilesWithProject = True
external_data_file = Ansys.Mechanical.ExternalData.ExternalDataFile()
external_data_files.Add(external_data_file)  # Single File
external_data_file.Identifier = "edb"
external_data_file.Description = ""
external_data_file.IsMainFile = False
external_data_file.FilePath = def_fileName
external_data_file.ImportSettings = (
    Ansys.Mechanical.ExternalData.ImportSettingsFactory.GetSettingsForFormat(
        Ansys.Mechanical.DataModel.MechanicalEnums.ExternalData.ImportFormat.ECAD
    )
)
import_settings = external_data_file.ImportSettings
import_settings.UseDummyNetData = False
imported_trace_group = Model.Materials.AddImportedTraceExternalData()
imported_trace_group.ImportExternalDataFiles(external_data_files)

allImpTraces = ExtAPI.DataModel.GetObjectsByType(
    Ansys.Mechanical.DataModel.Enums.DataModelObjectCategory.ImportedTrace
)

imp_trace = [
    x for x in allImpTraces if x.Parent.ObjectId == imported_trace_group.ObjectId
][0]
imp_trace.Activate()
imp_trace.InternalObject.GeometryDefineBy = 1

NSall = ExtAPI.DataModel.Project.Model.NamedSelections.GetChildren[
    Ansys.ACT.Automation.Mechanical.NamedSelection
](True)
ns_object = [i for i in NSall if i.Name == "board_layers"][0]
imp_trace.Location = ns_object
imp_trace.PropertyByName("PROPID_ExternalData").InternalValue = 1


layers = imp_trace.Layers
num_layers = layers.Count
for layer in layers:
    layer["Trace Material"] = "Copper Alloy"
vias = imp_trace.Vias
num_vias = vias.Count
for via in vias:
    via["Plating Material"] = "Copper Alloy"
imp_trace.Import()


# Image to file settings
set2d = Ansys.Mechanical.Graphics.GraphicsImageExportSettings()
set2d.CurrentGraphicsDisplay = False
mechdir = analysis.Children[0].SolverFilesDirectory
png_file_path = os.path.join(mechdir, image_name)
Graphics.ExportImage(png_file_path, GraphicsImageExportFormat.PNG, set2d)
# ExtAPI.DataModel.Project.Save(mechdat_file_path)

"""
)
print(output)

###################################################################################
# Initialize the variable needed for the image directory
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Set the ``image_dir`` for later use.
# Make the variable compatible for Windows, Linux, and Docker containers.

# image_directory_modified = project_directory.replace("\\", "\\\\")
mechanical.run_python_script(f"image_dir=ExtAPI.DataModel.AnalysisList[0].WorkingDir")


# Verify the path for image directory.
result_image_dir_server = mechanical.run_python_script(f"image_dir")
print(f"Images are stored on the server at: {result_image_dir_server}")

###############################################################################
# Download the image and plot
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

###############################################################################


# Close Mechanical
# ~~~~~~~~~~~~~~~~
# Close the Mechanical instance.

mechanical.exit()
