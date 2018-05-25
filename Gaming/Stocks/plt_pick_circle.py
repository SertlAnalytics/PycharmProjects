import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


class Disk:


    def __init__(self, center, radius, myid = None, figure=None, axes_object=None):
        """
        @ARGS
        CENTER : Tuple of floats
        RADIUS : Float
        """
        self.center = center
        self.radius = radius
        self.fig    = figure
        self.ax     = axes_object
        self.myid   = myid
        self.mypatch = None


    def mpl_patch(self, diskcolor= 'orange' ):
        """ Return a Matplotlib patch of the object
        """
        self.mypatch = mpl.patches.Circle( self.center, self.radius, facecolor = diskcolor, picker=1 )

        #if self.fig != None:
            #self.fig.canvas.mpl_connect('pick_event', self.onpick) # Activate the object's method

        return self.mypatch

def on_pick(disks, patches):
    def pick_event(event):
        for i, artist in enumerate(patches):
            if event.artist == artist:
                artist.set_facecolor('grey')
                print('color={}'.format(artist.get_facecolor()))
                event.canvas.draw()
                disk = disks[i]
                print( "You picked the disk {}".format(disk.center))
    return pick_event


def main():

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_title('click on disks to print out a message')

    disk_list = []
    patches = []

    disk_list.append( Disk( (0,0), 1.0, 1, fig, ax   )   )
    patches.append(disk_list[-1].mpl_patch())
    ax.add_patch(patches[-1])

    disk_list.append( Disk( (3,3), 0.5, 2, fig, ax   )   )
    patches.append(disk_list[-1].mpl_patch())
    ax.add_patch(patches[-1])

    disk_list.append( Disk( (4,9), 2.5, 3, fig, ax   )   )
    patches.append(disk_list[-1].mpl_patch())
    ax.add_patch(patches[-1])

    pick_handler = on_pick(disk_list, patches)

    fig.canvas.mpl_connect('pick_event', pick_handler) # Activate the object's method

    ax.set_ylim(-2, 10);
    ax.set_xlim(-2, 10);

    plt.show()


if __name__ == "__main__":
    main()