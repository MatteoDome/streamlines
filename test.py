import vtk
import os

#os.chdir("vtk_data\dissection")
#os.chdir("vtk_data\synthetic")
os.chdir("vtk_data\clean_dissection")

#filename = "metrics_07.vti"
#filename = "image_00.vti"
filename = "metrics_00.vti"

grayscale = False;
black_body_radiation = True;
dissection_data = True#False;

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

#streamtracer filter
streamtracer = vtk.vtkStreamTracer()
streamtracer.SetInput(output)
streamtracer.SetSource(seeds.GetOutput())
streamtracer.SetMaximumPropagation(200)
streamtracer.SetIntegrationDirectionToForward()
streamtracer.SetComputeVorticity(True)

#streamtracer mapper
streamtracer_mapper = vtk.vtkPolyDataMapper()
streamtracer_mapper.SetInputConnection(streamtracer.GetOutputPort())

#streamtracer actor
streamtracer_actor = vtk.vtkActor()
streamtracer_actor.SetMapper(streamtracer_mapper)
streamtracer_actor.VisibilityOn()
 
##rendering
renderer = vtk.vtkRenderer()

renderer.AddActor(streamtracer_actor)

#render the corners of the data set
corners = [[xmin,ymin,zmin], [xmin,ymin,zmax], [xmin,ymax,zmax], [xmin,ymax,zmin], [xmax,ymin,zmin], [xmax,ymin,zmax], [xmax,ymax,zmax], [xmax,ymax,zmin]]
for i in range(len(corners)):
	corner = corners[i]
	sphereSource = vtk.vtkSphereSource()
	sphereSource.SetCenter(corner[0], corner[1], corner[2])
	sphereSource.SetRadius(5.0)
	sphereMapper = vtk.vtkPolyDataMapper()
	sphereMapper.SetInputConnection(sphereSource.GetOutputPort())
	sphereActor = vtk.vtkActor()
	sphereActor.SetMapper(sphereMapper)
	renderer.AddActor(sphereActor)

#seed position	
sphereSource = vtk.vtkSphereSource()
sphereSource.SetCenter(seedPosition[0], seedPosition[1], seedPosition[2])
sphereSource.SetRadius(2.0)
sphereMapper = vtk.vtkPolyDataMapper()
sphereMapper.SetInputConnection(sphereSource.GetOutputPort())
sphereActor = vtk.vtkActor()
sphereActor.SetMapper(sphereMapper)
sphereActor.GetProperty().SetColor(1.0, 0.0, 0.0)
renderer.AddActor(sphereActor)

renderer.ResetCamera()
renderer.SetBackground(0.9,.7,1);
 
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
 
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
 
renderWindowInteractor.SetRenderWindow(renderWindow)
renderWindowInteractor.Initialize()
renderWindowInteractor.Start()