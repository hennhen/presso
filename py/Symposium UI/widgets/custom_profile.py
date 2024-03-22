import sys
import matplotlib
matplotlib.use("Qt5Agg")
from PyQt5 import QtWidgets, QtGui

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# drag.py
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.lines import Line2D


class DraggablePoint:

    # http://stackoverflow.com/questions/21654008/matplotlib-drag-overlapping-points-interactively

    lock = None #  only one can be animated at a time

    def __init__(self, parent, x=30, y=12, size=0.1):

        self.parent = parent
        self.point = patches.Ellipse((x, y), size*2, size*1, fc='r', alpha=0.5, edgecolor='r')
        self.x = x
        self.y = y
        parent.fig.axes[0].add_patch(self.point)
        parent.fig.axes[0].set_xlim(0, 30)  # Set the x-axis range
        parent.fig.axes[0].set_ylim(0, 12)
        parent.fig.axes[0].set_ylabel('Pressure (bars)')
        parent.fig.axes[0].set_xlabel('Time (seconds)')
        self.press = None
        self.background = None
        self.connect()
        
        # if another point already exist we draw a line
        if self.parent.list_points:
            line_x = [self.parent.list_points[-1].x, self.x]
            line_y = [self.parent.list_points[-1].y, self.y]

            self.line = Line2D(line_x, line_y, color='r', alpha=0.5)
            parent.fig.axes[0].add_line(self.line)


    def connect(self):

        'connect to all the events we need'

        self.cidpress = self.point.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidrelease = self.point.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion = self.point.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)


    def on_press(self, event):

        if event.inaxes != self.point.axes: return
        if DraggablePoint.lock is not None: return
        contains, attrd = self.point.contains(event)
        if not contains: return
        self.press = (self.point.center), event.xdata, event.ydata
        DraggablePoint.lock = self

        # draw everything but the selected rectangle and store the pixel buffer
        canvas = self.point.figure.canvas
        axes = self.point.axes
        self.point.set_animated(True)
        
        # TODO also the line of some other points needs to be released
        point_number =  self.parent.list_points.index(self)
        
        if self == self.parent.list_points[0]:
            self.parent.list_points[1].line.set_animated(True)            
        elif self == self.parent.list_points[-1]:
            self.line.set_animated(True)            
        else:
            self.line.set_animated(True)            
            self.parent.list_points[point_number+1].line.set_animated(True)                
            
            
            
        
        canvas.draw()
        self.background = canvas.copy_from_bbox(self.point.axes.bbox)

        # now redraw just the rectangle
        axes.draw_artist(self.point)

        # and blit just the redrawn area
        canvas.blit(axes.bbox)


    def on_motion(self, event):

        if DraggablePoint.lock is not self:
            return
        if event.inaxes != self.point.axes: return
        self.point.center, xpress, ypress = self.press
        dx = event.xdata - xpress
        dy = event.ydata - ypress
        self.point.center = (self.point.center[0]+dx, self.point.center[1]+dy)

        canvas = self.point.figure.canvas
        axes = self.point.axes
        # restore the background region
        canvas.restore_region(self.background)

        # redraw just the current rectangle
        axes.draw_artist(self.point)
        
        point_number =  self.parent.list_points.index(self)
        self.x = self.point.center[0]
        self.y = self.point.center[1]
        
        # We check if the point is A or B        
        if self == self.parent.list_points[0]:
            # or we draw the other line of the point
            self.parent.list_points[1].line.set_animated(True)
            axes.draw_artist(self.parent.list_points[1].line)
        
        elif self == self.parent.list_points[-1]:
            # we draw the line of the point            
            axes.draw_artist(self.line)    

        else:
            # we draw the line of the point
            axes.draw_artist(self.line)
            #self.parent.list_points[point_number+1].line.set_animated(True)
            axes.draw_artist(self.parent.list_points[point_number+1].line)
            
                
        
        
        if self == self.parent.list_points[0]:
            # The first point is especial because it has no line
            line_x = [self.x, self.parent.list_points[1].x]
            line_y = [self.y, self.parent.list_points[1].y]      
            # this is were the line is updated
            self.parent.list_points[1].line.set_data(line_x, line_y)
            
        elif self == self.parent.list_points[-1]:
            line_x = [self.parent.list_points[-2].x, self.x]
            line_y = [self.parent.list_points[-2].y, self.y]
            self.line.set_data(line_x, line_y)        
        else:
            # The first point is especial because it has no line
            line_x = [self.x, self.parent.list_points[point_number+1].x]
            line_y = [self.y, self.parent.list_points[point_number+1].y]      
            # this is were the line is updated
            self.parent.list_points[point_number+1].line.set_data(line_x, line_y)
            
            line_x = [self.parent.list_points[point_number-1].x, self.x]
            line_y = [self.parent.list_points[point_number-1].y, self.y]
            self.line.set_data(line_x, line_y)        

        # blit just the redrawn area
        canvas.blit(axes.bbox)


    def on_release(self, event):

        'on release we reset the press data'
        if DraggablePoint.lock is not self:
            return

        self.press = None
        DraggablePoint.lock = None

        # turn off the rect animation property and reset the background
        self.point.set_animated(False)
        
        point_number =  self.parent.list_points.index(self)
        
        if self == self.parent.list_points[0]:
            self.parent.list_points[1].line.set_animated(False)            
        elif self == self.parent.list_points[-1]:
            self.line.set_animated(False)            
        else:
            self.line.set_animated(False)            
            self.parent.list_points[point_number+1].line.set_animated(False)       
            

        self.background = None

        # redraw the full figure
        self.point.figure.canvas.draw()

        self.x = self.point.center[0]
        self.y = self.point.center[1]

    def disconnect(self):

        'disconnect all the stored connection ids'

        self.point.figure.canvas.mpl_disconnect(self.cidpress)
        self.point.figure.canvas.mpl_disconnect(self.cidrelease)
        self.point.figure.canvas.mpl_disconnect(self.cidmotion)

class ProfileMakerWidget(QtWidgets.QWidget):

    """A widget that includes a canvas for plotting draggable points and a button for adding new points."""

    def __init__(self, parent=None, width=10, height=8, dpi=100):
        super().__init__(parent)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.canvas = FigureCanvas(self.fig)
        self.axes = self.fig.add_subplot(111)
        self.axes.grid(True)

        self.canvas.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                  QtWidgets.QSizePolicy.Expanding)
        self.canvas.updateGeometry()

        self.list_points = []

        self.buttonBox = QtWidgets.QHBoxLayout()

        self.addButton = QtWidgets.QPushButton("Add Point")
        self.addButton.clicked.connect(self.addPoint)
        self.buttonBox.addWidget(self.addButton)

        self.printButton = QtWidgets.QPushButton("Print Points")
        self.printButton.clicked.connect(self.getPoints)
        self.buttonBox.addWidget(self.printButton)

        self.resetButton = QtWidgets.QPushButton("Reset Points")
        self.resetButton.clicked.connect(self.resetPoints)
        self.buttonBox.addWidget(self.resetButton)

        self.layout.addLayout(self.buttonBox)

        
        self.layout.addWidget(self.canvas)

        self.plotDraggablePoints()

    def addPoint(self):
        """Add a new draggable point connected to the last point."""
        if self.list_points:
            last_point = self.list_points[-1]
            new_x = last_point.x + 1
            new_y = last_point.y + 1
            size = 1
            new_point = DraggablePoint(self, new_x, new_y, size)
            self.list_points.append(new_point)
            self.updateFigure()

    def getPoints(self):
        """Return the list of points."""
        points = [(point.x, point.y) for point in self.list_points]
        print(points)
        return points
    
    def resetPoints(self):
        """Reset the list of points."""
        self.clearFigure()
        self.plotDraggablePoints()
        self.updateFigure()

    def plotDraggablePoints(self, size=1):
        """Plot and define the initial draggable points of the baseline."""
        self.list_points.append(DraggablePoint(self, 0.0, 0.0, size))
        self.list_points.append(DraggablePoint(self, 5, 4, size))
        self.updateFigure()

    def clearFigure(self):
        """Clear the graph."""
        self.axes.clear()
        self.axes.grid(True)
        del(self.list_points[:])
        self.updateFigure()

    def updateFigure(self):
        """Update the graph. Necessary to call after each plot."""
        self.canvas.draw()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main_window = QtWidgets.QMainWindow()  # Create the main window
    profile_maker_widget = ProfileMakerWidget(main_window)  # Use the ProfileMakerWidget
    main_window.setCentralWidget(profile_maker_widget)

    # Create a layout and add the button and ProfileMakerWidget to it
    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(profile_maker_widget)

    # Create a widget to hold the layout and set it as the central widget of the main window
    central_widget = QtWidgets.QWidget()
    central_widget.setLayout(layout)
    main_window.setCentralWidget(central_widget)

    main_window.show()  # Show the main window
    sys.exit(app.exec_())