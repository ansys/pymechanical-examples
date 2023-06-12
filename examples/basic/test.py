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
MAT.Import(mat_file_path)

# Assign the material
ExtAPI.DataModel.Project.Model.Geometry.Children[0].Children[0].Material = "Bullet"

# Add Coordinate system

cs = Model.CoordinateSystems
lcs = cs.AddCoordinateSystem()
lcs.Origin = [10.0, 1.5, -10.0]
lcs.PrimaryAxis = CoordinateSystemAxisType.PositiveZAxis
lcs.PrimaryAxisDefineBy = CoordinateSystemAlignmentType.GlobalY
lcs.OriginDefineBy = CoordinateSystemAlignmentType.Fixed

solver = analysis.Solver

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
Graphics.ViewOptions.ResultPreference.DeformationScaling =\
        MechanicalEnums.Graphics.DeformationScaling.True
Graphics.ViewOptions.ResultPreference.DeformationScaleMultiplier = 1

# Export an animation
anim_file_path = os.path.join(project_directory, "taylor_bar.avi")
eps.ExportAnimation(anim_file_path,
                    GraphicsAnimationExportFormat.AVI,
                    Ansys.Mechanical.Graphics.AnimationExportSettings(2000.0, 1000.0))

dir_deformation_details = {
    "Minimum": str(eps_max),
    "Maximum": str(eps_min)
}

json.dumps(dir_deformation_details)
