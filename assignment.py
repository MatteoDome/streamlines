import vtk

reader = vtk.vtkXMLImageDataReader() # You need to use the directory where you saved the data 
reader.SetFileName("D:\Downloads\aneurysm\aneurysm.vti")
# reader.SetFileName("C:\Users\Matteo\Documents\University\MedVis\streamlines\vtk_data\synthetic\image_00.vti") 
reader.Update() 
data = reader.GetOutput()
dataMapper = vtk.vtkPolyDataMapper() 

imageDataGeometryFilter = vtk.vtkImageDataGeometryFilter()
imageDataGeometryFilter.SetInputConnection(data)
imageDataGeometryFilter.Update()

# dataMapper.SetInputConnection(dataSource.GetOutputPort()) 
dataActor = vtk.vtkActor() 
dataActor.GetProperty().SetColor(1.0 , 0.0 , 0.0) 
dataActor.SetMapper(dataMapper)

renderer = vtk.vtkRenderer()
renderer.AddActor(actor)
renderer.SetBackground(1,1,1)
renderer.ResetCamera()
 
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
 
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
 
renderWindowInteractor.SetRenderWindow(renderWindow)
renderWindowInteractor.Initialize()
renderWindowInteractor.Start()