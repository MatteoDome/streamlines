import vtk
import os

os.chdir("vtk_data/test")
filename = "density.vtk"

grayscale = False;
black_body_radiation = False;
shadow_demo = True;

#read file
reader = vtk.vtkStructuredGridReader()
reader.SetFileName(filename)
reader.Update()
output = reader.GetOutput()

# Get vector

#seed definition
seeds = vtk.vtkPointSource()
seeds.SetNumberOfPoints(100)
seeds.SetRadius(3.0)
seeds.SetCenter(output.GetCenter())

#streamtracer filter
streamtracer = vtk.vtkStreamTracer()
streamtracer.SetInput(output)
streamtracer.SetSource(seeds.GetOutput())
streamtracer.SetMaximumPropagation(200)
streamtracer.SetIntegrationDirectionToForward()
streamtracer.SetComputeVorticity(True)

streamtracer_mapper = vtk.vtkPolyDataMapper()

if shadow_demo:
	streamTube = vtk.vtkTubeFilter()
	streamTube.SetInputConnection(streamtracer.GetOutputPort())
	streamTube.SetRadius(0.01)
	streamTube.SetNumberOfSides(12)
	streamTube.Update()

	streamtracer_mapper.SetInputConnection(streamTube.GetOutputPort())

else:
	streamtracer_mapper.SetInputConnection(streamtracer.GetOutputPort())

streamtracer_mapper.SetScalarRange(output.GetPointData().GetScalars().GetRange())

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
	cmap.AddRGBPoint(0.4, 1.0, 0.9, 0.1) # reddish
	cmap.AddRGBPoint(0.6, 0.9, 0.9, 0.0) # yellow
	cmap.AddRGBPoint(1.0, 1.0, 1.0, 1.0) # white

	scalarValues = vtk.vtkFloatArray()
	scalarValues.SetNumberOfComponents(1)
	scalarValues.SetNumberOfTuples(256)

	for i in xrange(256):
		scalarValues.SetTupleValue(i, [i / 255.0])

	cmap.MapScalars(scalarValues, 0, -1)

	streamtracer_mapper.SetLookupTable(cmap)

#streamtracer actor
streamtracer_actor = vtk.vtkActor()
streamtracer_actor.SetMapper(streamtracer_mapper)
streamtracer_actor.VisibilityOn()
 
##rendering
renderer = vtk.vtkRenderer()

renderer.AddActor(streamtracer_actor)

renderer.ResetCamera()
renderer.SetBackground(.5,.5,.5);

renderer.SetBackground(.5, .5, .9)
 
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
 
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
 
renderWindowInteractor.SetRenderWindow(renderWindow)
renderWindowInteractor.Initialize()
renderWindowInteractor.Start()