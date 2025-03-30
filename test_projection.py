import vtk


class BoxMaskSurfaceInteractor:
    def __init__(self, surface_data=None):
        """
        Initialize with optional surface data (vtkPolyData)
        """
        # Setup surface data
        if surface_data is None:
            # Create a sample surface if none is provided
            self.surface_data = self.create_sample_surface()
        else:
            self.surface_data = surface_data

        # Set up renderer and window
        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(0.2, 0.2, 0.3)

        self.render_window = vtk.vtkRenderWindow()
        self.render_window.AddRenderer(self.renderer)
        self.render_window.SetSize(800, 600)

        self.interactor = vtk.vtkRenderWindowInteractor()
        self.interactor.SetRenderWindow(self.render_window)

        # Setup box widget for user selection
        self.setup_box_widget()

        # Setup original surface visualization
        # We won't show the original surface directly
        # Instead, we'll only show the masked version

        # Setup the clipper for masking
        self.setup_clipper()

        # Add axes for better orientation
        self.add_axes()

    def setup_box_widget(self):
        """Setup the box widget for masking"""
        self.box_widget = vtk.vtkBoxWidget()
        self.box_widget.SetInteractor(self.interactor)

        # Set initial position based on surface bounds
        bounds = self.surface_data.GetBounds()
        # Start with a box that's 1/3 the size of the model
        center = [
            (bounds[0] + bounds[1]) / 2,
            (bounds[2] + bounds[3]) / 2,
            (bounds[4] + bounds[5]) / 2,
        ]
        size = [
            0.33 * (bounds[1] - bounds[0]),
            0.33 * (bounds[3] - bounds[2]),
            0.33 * (bounds[5] - bounds[4]),
        ]

        box_bounds = [
            center[0] - size[0],
            center[0] + size[0],
            center[1] - size[1],
            center[1] + size[1],
            center[2] - size[2],
            center[2] + size[2],
        ]

        self.box_widget.PlaceWidget(box_bounds)

        # Make the box widget more visible
        self.box_widget.HandlesOn()
        self.box_widget.SetHandleSize(0.01)
        self.box_widget.OutlineCursorWiresOn()
        self.box_widget.SetPlaceFactor(1.0)

        # Register callback for interaction
        self.box_widget.AddObserver(vtk.vtkCommand.InteractionEvent, self.box_callback)

    def setup_clipper(self):
        """Setup the clipper to mask the surface"""
        # Get initial planes from the box widget
        planes = vtk.vtkPlanes()
        self.box_widget.GetPlanes(planes)

        # Create clipper for the masking effect
        self.clipper = vtk.vtkClipPolyData()
        self.clipper.SetInputData(self.surface_data)
        self.clipper.SetClipFunction(planes)
        # Keep what's INSIDE the box (this is key for masking)
        self.clipper.InsideOutOn()
        self.clipper.Update()

        # Create mapper and actor for the clipped (masked) surface
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(self.clipper.GetOutputPort())

        self.masked_actor = vtk.vtkActor()
        self.masked_actor.SetMapper(mapper)
        # Use original color for the masked part
        self.masked_actor.GetProperty().SetColor(0.8, 0.8, 0.9)

        # Add the masked actor to the renderer
        self.renderer.AddActor(self.masked_actor)

    def box_callback(self, obj, event):
        """Callback for when the box widget is interacted with"""
        # Get the planes from the box widget
        planes = vtk.vtkPlanes()
        self.box_widget.GetPlanes(planes)

        # Update the clipper with the new planes
        self.clipper.SetClipFunction(planes)
        self.clipper.Modified()
        self.clipper.Update()

        # Render the scene
        self.render_window.Render()

    def create_sample_surface(self):
        """Create a sample surface for testing"""
        # Create a more complex surface to better demonstrate masking
        source = vtk.vtkSuperquadricSource()
        source.SetCenter(0.0, 0.0, 0.0)
        source.SetScale(1.0, 1.0, 1.0)
        source.SetPhiRoundness(0.3)
        source.SetThetaRoundness(0.7)
        source.SetThetaResolution(64)
        source.SetPhiResolution(64)
        source.Update()

        # Add some noise to make it more interesting
        noise = vtk.vtkButterflySubdivisionFilter()
        noise.SetInputConnection(source.GetOutputPort())
        noise.SetNumberOfSubdivisions(3)
        noise.Update()

        return noise.GetOutput()

    def add_axes(self):
        """Add coordinate axes for better orientation"""
        axes = vtk.vtkAxesActor()
        axes.SetTotalLength(5, 5, 5)  # Set the size of the axes
        axes.SetShaftTypeToCylinder()
        axes.SetCylinderRadius(0.02)
        axes.SetConeRadius(0.2)

        # Create a transform to position the axes
        transform = vtk.vtkTransform()
        transform.Translate(-15, -15, -15)  # Position in lower left corner
        axes.SetUserTransform(transform)

        self.renderer.AddActor(axes)

        # Add labels
        axes_labels = vtk.vtkTextProperty()
        axes_labels.SetFontSize(10)
        axes_labels.SetBold(True)

        axes.GetXAxisCaptionActor2D().SetCaptionTextProperty(axes_labels)
        axes.GetYAxisCaptionActor2D().SetCaptionTextProperty(axes_labels)
        axes.GetZAxisCaptionActor2D().SetCaptionTextProperty(axes_labels)

    def start(self):
        """Start the interactor"""
        self.renderer.ResetCamera()
        self.interactor.Initialize()
        self.box_widget.On()
        self.render_window.Render()
        self.interactor.Start()


# Version that provides additional visualization options
class EnhancedBoxMaskSurfaceInteractor:
    def __init__(self, surface_data=None):
        """
        Initialize with optional surface data (vtkPolyData)
        """
        # Setup surface data
        if surface_data is None:
            # Create a sample surface if none is provided
            self.surface_data = self.create_sample_surface()
        else:
            self.surface_data = surface_data

        # Set up renderer and window
        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(0.2, 0.2, 0.3)

        self.render_window = vtk.vtkRenderWindow()
        self.render_window.AddRenderer(self.renderer)
        self.render_window.SetSize(800, 600)

        self.interactor = vtk.vtkRenderWindowInteractor()
        self.interactor.SetRenderWindow(self.render_window)

        # Setup visualization mode flags
        self.show_original = True
        self.show_box_outline = True
        self.mask_mode = True  # True = show inside box, False = show outside box

        # Setup original surface visualization
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(self.surface_data)

        self.original_actor = vtk.vtkActor()
        self.original_actor.SetMapper(mapper)
        self.original_actor.GetProperty().SetColor(0.8, 0.8, 0.9)
        self.original_actor.GetProperty().SetOpacity(0.3)  # Semi-transparent
        self.renderer.AddActor(self.original_actor)

        # Setup box widget for user selection
        self.setup_box_widget()

        # Setup the clipper for masking
        self.setup_clipper()

        # Add key binding for toggling visualization modes
        self.setup_key_bindings()

        # Add axes for better orientation
        self.add_axes()

    def setup_box_widget(self):
        """Setup the box widget for masking"""
        self.box_widget = vtk.vtkBoxWidget()
        self.box_widget.SetInteractor(self.interactor)

        # Set initial position based on surface bounds
        bounds = self.surface_data.GetBounds()
        # Start with a box that's 1/3 the size of the model
        center = [
            (bounds[0] + bounds[1]) / 2,
            (bounds[2] + bounds[3]) / 2,
            (bounds[4] + bounds[5]) / 2,
        ]
        size = [
            0.33 * (bounds[1] - bounds[0]),
            0.33 * (bounds[3] - bounds[2]),
            0.33 * (bounds[5] - bounds[4]),
        ]

        box_bounds = [
            center[0] - size[0],
            center[0] + size[0],
            center[1] - size[1],
            center[1] + size[1],
            center[2] - size[2],
            center[2] + size[2],
        ]

        self.box_widget.PlaceWidget(box_bounds)

        # Make the box widget more visible
        self.box_widget.HandlesOn()
        self.box_widget.SetHandleSize(0.01)
        self.box_widget.OutlineCursorWiresOn()
        self.box_widget.SetPlaceFactor(1.0)

        # Register callback for interaction
        self.box_widget.AddObserver(vtk.vtkCommand.InteractionEvent, self.box_callback)

    def setup_clipper(self):
        """Setup the clipper to mask the surface"""
        # Get initial planes from the box widget
        planes = vtk.vtkPlanes()
        self.box_widget.GetPlanes(planes)

        # Create clipper for the masking effect
        self.clipper = vtk.vtkClipPolyData()
        self.clipper.SetInputData(self.surface_data)
        self.clipper.SetClipFunction(planes)
        # Initial state: Keep what's inside the box
        self.clipper.InsideOutOn()
        self.clipper.Update()

        # Create mapper and actor for the clipped (masked) surface
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(self.clipper.GetOutputPort())

        self.masked_actor = vtk.vtkActor()
        self.masked_actor.SetMapper(mapper)
        # Use a different color for the masked part
        self.masked_actor.GetProperty().SetColor(1.0, 0.5, 0.0)  # Orange

        # Add the masked actor to the renderer
        self.renderer.AddActor(self.masked_actor)

    def setup_key_bindings(self):
        """Setup key bindings for toggling visualization modes"""
        # Create callback functions for key presses

        def toggle_original(obj, event):
            self.show_original = not self.show_original
            self.original_actor.SetVisibility(self.show_original)
            self.render_window.Render()

        def toggle_box(obj, event):
            self.show_box_outline = not self.show_box_outline
            if self.show_box_outline:
                self.box_widget.On()
            else:
                self.box_widget.Off()
            self.render_window.Render()

        def toggle_mask_mode(obj, event):
            self.mask_mode = not self.mask_mode
            if self.mask_mode:
                self.clipper.InsideOutOn()  # Show inside box
                print("Showing inside box")
            else:
                self.clipper.InsideOutOff()  # Show outside box
                print("Showing outside box")
            self.clipper.Update()
            self.render_window.Render()

        # Create an observer for key presses
        kb_observer = self.interactor.CreateOneShotTimer

        # Register the callbacks with the observer
        self.interactor.AddObserver(
            "KeyPressEvent", lambda obj, event: self.key_press_callback(obj, event)
        )

    def key_press_callback(self, obj, event):
        """Handle key press events"""
        key = obj.GetKeySym().lower()

        if key == "o":
            # Toggle original surface visibility
            self.show_original = not self.show_original
            self.original_actor.SetVisibility(self.show_original)

        elif key == "b":
            # Toggle box widget visibility
            self.show_box_outline = not self.show_box_outline
            if self.show_box_outline:
                self.box_widget.On()
            else:
                self.box_widget.Off()

        elif key == "m":
            # Toggle between showing inside vs outside of box
            self.mask_mode = not self.mask_mode
            if self.mask_mode:
                self.clipper.InsideOutOn()  # Show inside box
                print("Showing inside box")
            else:
                self.clipper.InsideOutOff()  # Show outside box
                print("Showing outside box")
            self.clipper.Update()

        elif key == "c":
            # Cycle through different colors for the masked part
            colors = [
                [1.0, 0.5, 0.0],  # Orange
                [0.0, 1.0, 0.0],  # Green
                [0.0, 0.0, 1.0],  # Blue
                [1.0, 0.0, 1.0],  # Magenta
                [1.0, 1.0, 0.0],  # Yellow
            ]

            # Get current color
            current = self.masked_actor.GetProperty().GetColor()

            # Find the closest color in our list
            min_dist = float("inf")
            current_idx = 0
            for i, color in enumerate(colors):
                dist = sum([(c - cc) ** 2 for c, cc in zip(color, current)])
                if dist < min_dist:
                    min_dist = dist
                    current_idx = i

            # Set the next color
            next_idx = (current_idx + 1) % len(colors)
            self.masked_actor.GetProperty().SetColor(*colors[next_idx])

        # Render the scene with the changes
        self.render_window.Render()

    def box_callback(self, obj, event):
        """Callback for when the box widget is interacted with"""
        # Get the planes from the box widget
        planes = vtk.vtkPlanes()
        self.box_widget.GetPlanes(planes)

        # Update the clipper with the new planes
        self.clipper.SetClipFunction(planes)
        self.clipper.Modified()
        self.clipper.Update()

        # Render the scene
        self.render_window.Render()

    def create_sample_surface(self):
        """Create a sample surface for testing"""
        # Create a bunny or dragon model for better visualization
        source = vtk.vtkSphereSource()
        source.SetRadius(10.0)
        source.SetThetaResolution(30)
        source.SetPhiResolution(30)
        source.Update()

        # Let's add some more detail
        subdivide = vtk.vtkLinearSubdivisionFilter()
        subdivide.SetInputConnection(source.GetOutputPort())
        subdivide.SetNumberOfSubdivisions(2)
        subdivide.Update()

        return subdivide.GetOutput()

    def add_axes(self):
        """Add coordinate axes for better orientation"""
        axes = vtk.vtkAxesActor()
        axes.SetTotalLength(5, 5, 5)  # Set the size of the axes
        axes.SetShaftTypeToCylinder()
        axes.SetCylinderRadius(0.02)
        axes.SetConeRadius(0.2)

        # Create a transform to position the axes
        transform = vtk.vtkTransform()
        transform.Translate(-15, -15, -15)  # Position in lower left corner
        axes.SetUserTransform(transform)

        self.renderer.AddActor(axes)

    def start(self):
        """Start the interactor"""
        # Print usage instructions
        print("=== Box Mask Surface Interactor ===")
        print("Keyboard shortcuts:")
        print("  'o': Toggle original surface visibility")
        print("  'b': Toggle box widget visibility")
        print("  'm': Toggle between showing inside vs outside of box")
        print("  'c': Cycle through colors for the masked part")

        self.renderer.ResetCamera()
        self.interactor.Initialize()
        self.box_widget.On()
        self.render_window.Render()
        self.interactor.Start()


# Usage example
if __name__ == "__main__":
    # Choose which implementation to use
    use_enhanced = True

    # Example of loading an actual surface
    # reader = vtk.vtkSTLReader()  # or vtkOBJReader, vtkPLYReader, etc.
    # reader.SetFileName("your_surface.stl")
    # reader.Update()
    # surface_data = reader.GetOutput()

    # Use sample surface for demonstration
    if use_enhanced:
        app = EnhancedBoxMaskSurfaceInteractor()
    else:
        app = BoxMaskSurfaceInteractor()

    app.start()
