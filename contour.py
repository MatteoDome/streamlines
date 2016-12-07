import vtk
import os
os.chdir("vtk_data\dissection")

filename = "metrics_07.vti"
 
#read file
reader = vtk.vtkXMLImageDataReader()
reader.SetFileName(filename)
reader.Update()
output = reader.GetOutput()
scalar_range = output.GetScalarRange()

#select contour
contours = vtk.vtkContourFilter()
contours.SetInputConnection(reader.GetOutputPort()) 
contours.GenerateValues(10, scalar_range) 

#mapper
contMapper = vtk.vtkPolyDataMapper() 
contMapper.SetInputConnection(contours.GetOutputPort()) 
# contMapper.SetScalarVisibility() 
contMapper.SetScalarRange(1000, 1500)
    
#Setup contour actor
contActor = vtk.vtkActor() 
contActor.SetMapper(contMapper) 
contActor.GetProperty().SetColor(0.2, 0.2, 0.2)
contActor.GetProperty().SetLineWidth(1)

# Check values
print(reader.GetOutput().GetScalarRange())

# Setup rendering
renderer = vtk.vtkRenderer()
renderer.AddActor(contActor)
renderer.ResetCamera()
 
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
 
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
 
renderWindowInteractor.SetRenderWindow(renderWindow)
renderWindowInteractor.Initialize()
renderWindowInteractor.Start()