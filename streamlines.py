import vtk
import os

os.chdir("vtk_data\diss1ection")
# os.chdir("vtk_data\synthetic")

filename = "metrics_07.vti"
# filename = "image_00.vti"

grayscale = False;
dissection_data = False;

#read file
reader = vtk.vtkXMLImageDataReader()
reader.SetFileName(filename)
reader.Update()
output = reader.GetOutput()

# Get vectors
velocity_field = output.GetPointData().GetArray(0)
output.GetPointData().SetVectors(velocity_field);

#get info from file
origin = output.GetOrigin()
origin_x = origin[0]
origin_y = origin[1]
origin_z = origin[2]

extent = output.GetExtent()
xmin = extent[0]+origin_x
xmax = extent[1]+origin_x
ymin = extent[2]+origin_y
ymax = extent[3]+origin_y
zmin = extent[4]+origin_z
zmax = extent[5]+origin_z

center_x = xmin + (xmax-xmin)/2
center_y = ymin + (ymax-ymin)/2
center_z = zmin + (zmax-zmin)/2

#seed definition
seeds = vtk.vtkPlaneSource()
seeds.SetXResolution(8)
seeds.SetYResolution(8)
seeds.SetOrigin(center_x, center_y, center_z)
seeds.SetPoint1(center_x+20, center_y, center_z)
seeds.SetPoint2(center_x, center_y+20, center_z)

#streamline filter
streamline = vtk.vtkStreamLine()
streamline.SetInput(output)
streamline.SetSource(seeds.GetOutput())
streamline.SetMaximumPropagationTime(200)
streamline.SetIntegrationStepLength(.2)
streamline.SetStepLength(0.001)
streamline.SetNumberOfThreads(1)
streamline.SetIntegrationDirectionToForward()
streamline.VorticityOn()
streamline.SpeedScalarsOn()
 
##streamTube from streamlines
streamTube = vtk.vtkTubeFilter()

##stripperFilter and cleanFilter are used to get rid of noise in dissection data
if dissection_data:
	stripperFilter = vtk.vtkStripper()
	stripperFilter.SetInputConnection(streamline.GetOutputPort());
	stripperFilter.Update( );
	cleanFilter = vtk.vtkCleanPolyData()
	cleanFilter.SetInputConnection(stripperFilter.GetOutputPort())
	cleanFilter.Update()
	streamTube.SetInputConnection(cleanFilter.GetOutputPort())
else:
	streamTube.SetInputConnection(streamline.GetOutputPort())

streamTube.SetInputArrayToProcess(1, 0, 0, vtk.vtkDataObject.FIELD_ASSOCIATION_POINTS, "vectors")
streamTube.SetRadius(0.2)
streamTube.SetNumberOfSides(12)
streamTube.SetVaryRadiusToVaryRadiusByVector()
streamTube.Update()

##streamtube mapper
mapStreamTube = vtk.vtkPolyDataMapper()
mapStreamTube.SetInputConnection(streamTube.GetOutputPort())

##LookupTable modification to get grayscale
if grayscale:
	lut = vtk.vtkLookupTable()
	lut.SetHueRange(0.0, 0.0);
	lut.SetSaturationRange(0.0, 0.0);
	lut.SetValueRange(1.0, 0.0);
	mapStreamTube.SetLookupTable(lut)

##streamtube actor
streamTubeActor = vtk.vtkActor()
streamTubeActor.SetMapper(mapStreamTube)
streamTubeActor.GetProperty().BackfaceCullingOn()

##rendering
renderer = vtk.vtkRenderer()

renderer.AddActor(streamTubeActor)
renderer.ResetCamera()
renderer.SetBackground(0.9,.7,1);
 
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
 
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
 
renderWindowInteractor.SetRenderWindow(renderWindow)
renderWindowInteractor.Initialize()
renderWindowInteractor.Start()