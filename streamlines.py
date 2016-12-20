import vtk
import os

# os.chdir("vtk_data\dissection")
#os.chdir("vtk_data\synthetic")
os.chdir("vtk_data\clean_dissection")

#filename = "metrics_07.vti"
#filename = "image_00.vti"
filename = "metrics_00.vti"

grayscale = True;
black_body_radiation = False;
dissection_data = False#False;

#read file
reader = vtk.vtkXMLImageDataReader()
reader.SetFileName(filename)
reader.Update()
output = reader.GetOutput()

# Get vectors
velocity_field = output.GetPointData().GetArray(0)
output.GetPointData().SetVectors(velocity_field);

#get info from file
spacing = output.GetSpacing()

origin = output.GetOrigin()
origin_x = origin[0]
origin_y = origin[1]
origin_z = origin[2]

extent = output.GetExtent()
xmin = spacing[0]*extent[0]+origin_x
xmax = spacing[0]*extent[1]+origin_x
ymin = spacing[1]*extent[2]+origin_y
ymax = spacing[1]*extent[3]+origin_y
zmin = spacing[2]*extent[4]+origin_z
zmax = spacing[2]*extent[5]+origin_z

center_x = xmin + (xmax-xmin)/2
center_y = ymin + (ymax-ymin)/2
center_z = zmin + (zmax-zmin)/2

seedPosition = [103.0,158.0,127.0]

#seed definition
seeds = vtk.vtkPointSource()
seeds.SetRadius(10.0)
seeds.SetNumberOfPoints(20)
seeds.SetCenter(seedPosition[0], seedPosition[1], seedPosition[2])

#seed definition
seeds = vtk.vtkPointSource()
seeds.SetRadius(10.0)
seeds.SetNumberOfPoints(20)
seeds.SetCenter(seedPosition[0], seedPosition[1], seedPosition[2])

#streamtracer filter
streamtracer = vtk.vtkStreamTracer()
streamtracer.SetInput(output)
streamtracer.SetSource(seeds.GetOutput())
streamtracer.SetMaximumPropagation(200)
streamtracer.SetIntegrationDirectionToForward()
streamtracer.SetComputeVorticity(True)

# #streamtracer mapper
# streamtracer_mapper = vtk.vtkPolyDataMapper()
# streamtracer_mapper.SetInputConnection(streamtracer.GetOutputPort())

# #streamtracer actor
# streamtracer_actor = vtk.vtkActor()
# streamtracer_actor.SetMapper(streamtracer_mapper)
# streamtracer_actor.VisibilityOn()

#streamline filter
# streamline = vtk.vtkStreamLine()
# streamline.SetInput(output)
# streamline.SetSource(seeds.GetOutput())
# streamline.SetMaximumPropagationTime(200)
# streamline.SetIntegrationStepLength(.2)
# streamline.SetStepLength(0.001)
# streamline.SetNumberOfThreads(1)
# streamline.SetIntegrationDirectionToForward()
# streamline.VorticityOn()
# streamline.SpeedScalarsOn()
 
##streamTube from streamlines
streamTube = vtk.vtkTubeFilter()

##stripperFilter and cleanFilter are used to get rid of noise in dissection data
if dissection_data:
	stripperFilter = vtk.vtkStripper()
	stripperFilter.SetInputConnection(streamtracer.GetOutputPort());
	stripperFilter.Update();
	cleanFilter = vtk.vtkCleanPolyData()
	cleanFilter.SetInputConnection(stripperFilter.GetOutputPort())
	cleanFilter.Update()
	streamTube.SetInputConnection(cleanFilter.GetOutputPort())
else:
	streamTube.SetInputConnection(streamtracer.GetOutputPort())

streamTube.SetInputArrayToProcess(1, 0, 0, vtk.vtkDataObject.FIELD_ASSOCIATION_POINTS, "vectors")
streamTube.SetRadius(0.2)
streamTube.SetNumberOfSides(12)
streamTube.SetVaryRadiusToVaryRadiusByVector()
streamTube.Update()

##streamtube mapper
mapStreamTube = vtk.vtkPolyDataMapper()
mapStreamTube.SetInputConnection(streamTube.GetOutputPort())

##LookupTable modification to get grayscale or black body radiaton
if grayscale:
	lut = vtk.vtkLookupTable()
	lut.SetHueRange(0.0, 0.0);
	lut.SetSaturationRange(0.0, 0.0);
	lut.SetValueRange(1.0, 0.0);
	mapStreamTube.SetLookupTable(lut)
elif black_body_radiation:
	cmap = vtk.vtkDiscretizableColorTransferFunction()
	cmap.SetColorSpaceToRGB()
	cmap.AddRGBPoint(0.0, 0.0, 0.0, 0.0) # black
	cmap.AddRGBPoint(0.4, 1.0, 0.9, 0.0) # reddish
	cmap.AddRGBPoint(0.8, 0.9, 0.9, 0.0) # yellow
	cmap.AddRGBPoint(1.0, 1.0, 1.0, 1.0) # white

	scalarValues = vtk.vtkFloatArray()
	scalarValues.SetNumberOfComponents(1)
	scalarValues.SetNumberOfTuples(256)

	for i in xrange(256):
		scalarValues.SetTupleValue(i, [i / 255.0])

	cmap.MapScalars(scalarValues, 0, -1)

	mapStreamTube.SetLookupTable(cmap)

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