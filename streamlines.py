import vtk
import os

os.chdir("vtk_data/synthetic")
# os.chdir("vtk_data/clean_dissection")

filename = "image_00.vti"
# filename = "metrics_00.vti"

grayscale = False;
black_body_radiation = False;
shadow_demo = True;

#read file
reader = vtk.vtkXMLImageDataReader()
reader.SetFileName(filename)
reader.Update()
output = reader.GetOutput()

# Get vectors
velocity_field = output.GetPointData().GetArray(0)
output.GetPointData().SetVectors(velocity_field);


if filename == "metrics_00.vti":
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

	if shadow_demo:
		streamTube = vtk.vtkTubeFilter()
		streamTube.SetInputConnection(streamtracer.GetOutputPort())
		streamTube.SetInputArrayToProcess(1, 0, 0, vtk.vtkDataObject.FIELD_ASSOCIATION_POINTS, "vectors")
		streamTube.SetRadius(0.2)
		streamTube.SetNumberOfSides(12)
		streamTube.SetVaryRadiusToVaryRadiusByVector()
		streamTube.Update()

		##streamtube mapper
		streamtracer_mapper = vtk.vtkPolyDataMapper()
		streamtracer_mapper.SetInputConnection(streamTube.GetOutputPort())

	else:
		#streamtracer mapper
		streamtracer_mapper = vtk.vtkPolyDataMapper()
		streamtracer_mapper.SetInputConnection(streamtracer.GetOutputPort())



else:
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

	if shadow_demo:
		streamTube = vtk.vtkTubeFilter()
		streamTube.SetInputConnection(streamline.GetOutputPort())
		streamTube.SetRadius(0.2)
		streamTube.SetNumberOfSides(12)
		streamTube.Update()

		##streamtube mapper
		streamtracer_mapper = vtk.vtkPolyDataMapper()
		streamtracer_mapper.SetInputConnection(streamTube.GetOutputPort())
		

	else:
		streamtracer_mapper = vtk.vtkPolyDataMapper()
		streamtracer_mapper.SetInputConnection(streamline.GetOutputPort())
	
streamtracer_mapper.ScalarVisibilityOn()
streamtracer_mapper.SetScalarRange(0, 1500)
streamtracer_mapper.SetScalarModeToUsePointFieldData()
streamtracer_mapper.ColorByArrayComponent("VelocityMagnitude", 0)

##LookupTable modification to get grayscale or black body radiaton
if grayscale:
	lut = vtk.vtkLookupTable()
	lut.SetHueRange(0.0, 0.0);
	lut.SetSaturationRange(0.0, 0.0);
	lut.SetValueRange(1.0, 0.0);
	streamtracer_mapper.SetLookupTable(lut)
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

	streamtracer_mapper.SetLookupTable(cmap)


##streamtube actor
stream_actor = vtk.vtkActor()
stream_actor.SetMapper(streamtracer_mapper)
stream_actor.GetProperty().BackfaceCullingOn()

##rendering
renderer = vtk.vtkRenderer()
renderer.AddActor(stream_actor)
renderer.ResetCamera()
renderer.SetBackground(0.5,.5, .9);
 
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
 
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
 
renderWindowInteractor.SetRenderWindow(renderWindow)
renderWindowInteractor.Initialize()
renderWindowInteractor.Start()