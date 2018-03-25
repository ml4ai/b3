import sys
import numpy
import matplotlib.pyplot as plt
import pandas as pd

plt.ion()

#-------------------------------------------------------------------------------------
# Notes
# () Probably best to make sql database-backed data store

#-------------------------------------------------------------------------------------
# path to patterns of life data - assuming in /b3/utilities/

DATA_PATH = '../../data/pol.txt'

#-------------------------------------------------------------------------------------

'''
raw frame: [1, 0, 450, 42, 540, 4844, 1, 0, 1, 'Person']
   1   Track ID. All rows with the same ID belong to the same path.
   2   xmin. The top left x-coordinate of the bounding box.
   3   ymin. The top left y-coordinate of the bounding box.
   4   xmax. The bottom right x-coordinate of the bounding box.
   5   ymax. The bottom right y-coordinate of the bounding box.
   6   frame. The frame that this annotation represents.
   7   lost. If 1, the annotation is outside of the view screen.
   8   occluded. If 1, the annotation is occluded.
   9   generated. If 1, the annotation was automatically interpolated.
   10  label. The label for this annotation, enclosed in quotation marks.
augmented frame: [1, 0, 450, 42, 540, 4844, 1, 0, 1, 'Person', (x, y)]
'''

RAW_FRAME_DTYPE = [('xmin', 'f4'), ('ymin', 'f4'), ('xmax', 'f4'), ('ymax', 'f4'), 
                   ('frame', 'i8'), 
                   ('lost', 'b'), ('occluded', 'b'), ('generated', 'b'),
                   ('label', 'S10')]

#-------------------------------------------------------------------------------------

def select_frames_from_file(filepath, start, end):
    """
    """
    frames_dict = {}
        
    with open(filepath) as f:
        for line in f:
            datum = line.split()
            frame = int(datum[5])
            if start <= frame <= end:
                datum = tuple( map(lambda v: int(v), datum[:-1]) + [datum[-1][1:-1]] )
                track_id = datum[0]
                datum = datum[1:] # remove track_id from datum
                if track_id in frames_dict:
                    frames_dict[track_id].append(datum)
                else:
                    frames_dict[track_id] = [datum]

    panel_dict = {}
    for k in frames_dict.keys():
        a = numpy.asarray(frames_dict[k], dtype=RAW_FRAME_DTYPE)
        panel_dict[k] = pd.DataFrame.from_records(a, index='frame')
    
    return pd.Panel(panel_dict)

'''
# Example reading data from file
select_frames_from_file(DATA_PATH, 4843, 5348)

# get index of items (DataFrames) in panel
panel.items 
'''

#-------------------------------------------------------------------------------------

def calculate_frame_bbox_extrema(track_panel):
    """
    Find the extrema of bounding box values of track_panel (e.g., useful for display)
    
    Return (xmin, ymin, xmax, ymax)
    as overall max and min of all bounding boxes of track_panel
    """
    xmin = sys.maxint
    ymin = sys.maxint
    xmax = - sys.maxint
    ymax = - sys.maxint
    for track_id, track in track_panel.iteritems():
        xn = min(track['xmin'])
        if xmin > xn: xmin = xn
        yn = min(track['ymin'])
        if ymin > yn: ymin = yn
        xx = max(track['xmax'])
        if xmax < xx: xmax = xx
        yx = max(track['ymax'])
        if ymax < yx: ymax = yx
    return (xmin, ymin, xmax, ymax)

def calculate_all_bbox_centroids(track_panel):
    """
    Calculate bounding box centroids and ADD x_centroid and y_centroid Series to each track.
    """
    for track_id, track in track_panel.iteritems():
        track['x_centroid'] = pd.Series(track['xmin'] + (track['xmax'] - track['xmin'])/2.0, 
                                        index=track.index)
        track['y_centroid'] = pd.Series(track['ymin'] + (track['ymax'] - track['ymin'])/2.0, 
                                        index=track.index)

#-------------------------------------------------------------------------------------

def plot_tracks(track_panel, ranges = None, new_fig = True, legend = False):
    """ Plot each track as a separate set of points """
    if new_fig:
        plt.figure()
    tick_start = sys.maxint
    tick_end = - sys.maxint
    if ranges:
        xmin, ymin, xmax, ymax = ranges
    else:
        xmin, ymin, xmax, ymax = calculate_frame_bbox_extrema(track_panel)
    for track_id, track in track_panel.iteritems():
        tstart = min(track.index)
        if tstart < tick_start: tick_start = tstart
        tend = max(track.index)
        if tend > tick_end: tick_end = tend
        if 'x_centroid' in track.columns:
            x = track.x_centroid
        else:
            x = pd.Series(track['xmin'] + (track['xmax'] - track['xmin'])/2.0,
                          index=track.index)
        x = x[pd.notnull(x)]
        if 'y_centroid' in track.columns:
            y = track.y_centroid
        else:
            y = pd.Series(track['ymin'] + (track['ymax'] - track['ymin'])/2.0,
                          index=track.index)
        y = y[pd.notnull(y)]
        y = (-1 * y) + ymax # flip y
        plt.plot(x,y,label=r'{0}'.format(track_id))
    plt.title('Time [{0}, {1}]'.format(tick_start,tick_end))
    if legend: plt.legend(loc="upper right")
    if ranges:
        plt.xlim((xmin,xmax))
        plt.ylim((ymin,ymax))

# plot_tracks(panel)

#-------------------------------------------------------------------------------------

