import vtk
import os

#os.chdir("vtk_data\dissection")
#os.chdir("vtk_data\synthetic")
#os.chdir("vtk_data\clean_dissection")
os.chdir("vtk_data/test")

#filename = "metrics_07.vti"
#filename = "image_00.vti"
#filename = "metrics_00.vti"
filename = "density.vtk"

grayscale = True;
black_body_radiation = False;

#read file
reader = vtk.vtkStructuredGridReader()
reader.SetFileName(filename)
reader.Update()
output = reader.GetOutput()

# Get vector

#seed definition
seeds = vtk.vtkPointSource()
seeds.SetNumberOfPoints(100)
seeds.SetRadius(.20)
seeds.SetCenter(output.GetCenter())

#streamtracer filter
streamtracer = vtk.vtkStreamTracer()
streamtracer.SetInput(output)
streamtracer.SetSource(seeds.GetOutput())
streamtracer.SetMaximumPropagation(200)
streamtracer.SetIntegrationDirectionToForward()
streamtracer.SetComputeVorticity(True)

streamTube = vtk.vtkTubeFilter()
streamTube.SetInputConnection(streamtracer.GetOutputPort())
streamTube.SetRadius(0.01)
streamTube.SetNumberOfSides(12)
streamTube.Update()

##streamtube mapper
mapStreamTube = vtk.vtkPolyDataMapper()
mapStreamTube.SetInputConnection(streamTube.GetOutputPort())
mapStreamTube.ScalarVisibilityOn()
mapStreamTube.SetScalarRange(output.GetPointData().GetScalars().GetRange())
mapStreamTube.SetScalarModeToUsePointFieldData()

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
	cmap.AddRGBPoint(0.4, 1.0, 0.9, 0.1) # reddish
	cmap.AddRGBPoint(0.6, 0.9, 0.9, 0.0) # yellow
	cmap.AddRGBPoint(1.0, 1.0, 1.0, 1.0) # white

	scalarValues = vtk.vtkFloatArray()
	scalarValues.SetNumberOfComponents(1)
	scalarValues.SetNumberOfTuples(256)

	for i in xrange(256):
		scalarValues.SetTupleValue(i, [i / 255.0])

	cmap.MapScalars(scalarValues, 0, -1)

	mapStreamTube.SetLookupTable(cmap)

#streamtracer actor
streamTube_actor= vtk.vtkActor()
streamTube_actor.SetMapper(mapStreamTube)
streamTube_actor.VisibilityOn()
 
##rendering
renderer = vtk.vtkRenderer()
renderer.UseShadowsOff()

renderer.AddActor(streamTube_actor)

renderer.ResetCamera()
renderer.SetBackground(.5,.5,.5);
 
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
 
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
 
renderWindowInteractor.SetRenderWindow(renderWindow)
renderWindowInteractor.Initialize()
renderWindowInteractor.Start()