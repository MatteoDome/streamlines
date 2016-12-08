import vtk
import os
#os.chdir("vtk_data\dissection")
os.chdir("vtk_data\synthetic")

#filename = "metrics_07.vti"
filename = "image_04.vti"
 
#read file
reader = vtk.vtkXMLImageDataReader()
reader.SetFileName(filename)
reader.Update()
output = reader.GetOutput()

# Get vectors
velocity_field = output.GetPointData().GetArray(0)
output.GetPointData().SetVectors(velocity_field);
print("Number of velocity vector components: "+str(velocity_field.GetNumberOfComponents()))

lut = vtk.vtkLookupTable()
lut.SetHueRange(0.0, 0.0);
lut.SetSaturationRange(0.0, 0.0);
lut.SetValueRange(1.0, 0.0);

#get additional info from the file
origin = output.GetOrigin()
print(origin)
origin_x = origin[0]
origin_y = origin[1]
origin_z = origin[2]

extent = output.GetExtent()
print(extent)
xmin = extent[0]+origin_x
xmax = extent[1]+origin_x
ymin = extent[2]+origin_y
ymax = extent[3]+origin_y
zmin = extent[4]+origin_z
zmax = extent[5]+origin_z

center_x = xmin + (xmax-xmin)/2
center_y = ymin + (ymax-ymin)/2
center_z = zmin + (zmax-zmin)/2

#"seeds" defines points where the streamlines are seeded:
seeds = vtk.vtkPlaneSource()
seeds.SetXResolution(8)
seeds.SetYResolution(8)
seeds.SetOrigin(center_x, center_y, center_z)
seeds.SetPoint1(center_x+20, center_y, center_z)
seeds.SetPoint2(center_x, center_y+20, center_z)
 
#basic vtk stream line filter
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

streamTube = vtk.vtkTubeFilter()
streamTube.SetInputConnection(streamline.GetOutputPort())
streamTube.SetInputArrayToProcess(1, 0, 0, vtk.vtkDataObject.FIELD_ASSOCIATION_POINTS, "vectors")
streamTube.SetRadius(0.2)
streamTube.SetNumberOfSides(12)
streamTube.SetVaryRadiusToVaryRadiusByVector()

##streamtube mapper
mapStreamTube = vtk.vtkPolyDataMapper()
mapStreamTube.SetInputConnection(streamTube.GetOutputPort())
mapStreamTube.SetLookupTable(lut)

##streamtube actor
streamTubeActor = vtk.vtkActor()
streamTubeActor.SetMapper(mapStreamTube)
streamTubeActor.GetProperty().BackfaceCullingOn()

# Setup rendering
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