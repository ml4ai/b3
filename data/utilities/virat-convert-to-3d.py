import numpy
import matplotlib.pyplot as plt

plt.ion()

# -----------------------------------------------------------------------------
# Convert VIRAT object track files from 2d image to 3d using homography matrix
# NTOE: Assumes convert_virat_obj_file_to_3d is called from the 
#       VIRAT-2.0/homographies/ directory
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Format of VIRAT object files

# Object File Columns
# 1: Object id        (a unique identifier of an object track. Unique within a file.)
# 2: Object duration  (duration of the object track)
# 3: Currnet frame    (corresponding frame number)
# 4: bbox lefttop x   (horizontal x coord of the left top of bbox, origin is lefttop of the frame)
# 5: bbox lefttop y   (vertical y coordinate of the left top of bbox, origin is lefttop of the frame)
# 6: bbox width       (horizontal width of the bbox)
# 7: bbox height      (vertical height of the bbox)
# 8: Objct Type       (object type)

# Object Type ID (for column 8 above for object files)
# 1: person
# 2: car              (usually passenger vehicles such as sedan, truck)
# 3: vehicles         (vehicles other than usual passenger cars. 
#                      Examples include construction vehicles)
# 4: object           (neither car or person, usually carried objects)
# 5: bike, bicylces   (may include engine-powered auto-bikes)

# -----------------------------------------------------------------------------

# Would be better if this was determined directly from image/video
image_x_max = 1920 # 1080
image_y_max = 1080 # 720

# -----------------------------------------------------------------------------

# NOTE: the following two VIRAT object files use the SAME homography 
#       (poorly labeled!)
vdata1_file = '../data/VIRAT_S_000001.viratdata.objects.txt'
vdata2_file = '../data/VIRAT_S_000002.viratdata.objects.txt'
vdata1_homography = 'VIRAT_0000_homography_img2world.txt'

# -----------------------------------------------------------------------------

def read_homography_matrix_from_file(homography_file):
    H = []
    with open(homography_file) as hom_fp:
        for sline in hom_fp:
            H.append(map(lambda v: float(v), 
                         sline.strip('\n').split(',')))
    return numpy.asmatrix(H)

# -----------------------------------------------------------------------------

def apply_homography_transform(H,x1,y1):
    '''
    Uses homography matrix H to convert x1,y1 to x2,y2
    Note: this is generic: H or it's inverse can be used to convert back and forth.
    '''
    d1_point = numpy.asmatrix([[x1],[y1],[1]])
    d2_point = H.dot(d1_point)
    x2 = d2_point[0,0] / d2_point[2,0]
    y2 = d2_point[1,0] / d2_point[2,0]
    return [x2, y2]

# -----------------------------------------------------------------------------

def get_image_corners():
    '''
    NOTE: Would be better if image_x_max and image_y_max were determined 
          directly from image/video
    returns: corners starting with upper_left and going clockwise:
             upper_left, upper_right, lower_right, lower_left
    '''
    return [[0,0], [image_x_max,0], [image_x_max,image_y_max], [0,image_y_max]]

def convert_image_corners_to_3d(H):
    '''
    Converts image corners to 3d homography-transformed coordinates
    '''
    return map(lambda xy: apply_homography_transform(H,xy[0],xy[1]),
               get_image_corners())

def convert_corners_from_3d_to_2d(H, d3_corners):
    '''
    Converts 3d corners to 2d image coordinates by using the inverse homography matrix
    '''
    d2_corners = []
    H_inv = numpy.linalg.inv(H)
    for (x,y) in d3_corners:
        d2_corners.append(apply_homography_transform(H_inv,x,y))
    return d2_corners

def plot_corners(corners,
                 xl='3d x axis', yl='3d y axis', title='tracks in 3d, top-down plane',
                 exchange_x_with_y=False,
                 adjust_border=False):
    '''
    Plots corners.
    exchange_x_with_y exchanges the x and y axes.
        Used to correct 3d homography-transformed points for, e.g., VIRAT_S_000001 and 2 
    '''
    
    ax = plt.gca()
    corners.append(corners[0]) # complete the 'square'
    x = map(lambda v: v[0], corners)
    y = map(lambda v: v[1], corners)

    if exchange_x_with_y:
        t = x
        x = y
        y = t
        tl = xl
        xl = yl
        yl = tl
    
    plt.plot(x,y)
    ax.text(x[0],y[0],'upper_left',fontsize=12)
    ax.text(x[1],y[1],'upper_right',fontsize=12)
    ax.text(x[2],y[2],'lower_right',fontsize=12)
    ax.text(x[3],y[3],'lower_left',fontsize=12)
    plt.xlabel(xl)
    plt.ylabel(yl)
    plt.title(title)

    if adjust_border:
        xpad = abs(plt.xlim()[1] - plt.xlim()[0])*0.05
        plt.xlim([plt.xlim()[0]-xpad,plt.xlim()[1]+xpad])
        #ypad = abs(plt.ylim()[1] - plt.ylim()[0])*0.05
        #plt.ylim([plt.ylim()[0]-ypad,plt.ylim()[1]+ypad])

# -----------------------------------------------------------------------------

def plot_track(track,xind=3,yind=4,exchange_x_with_y=False):
    '''
    Plots track.
    exchange_x_with_y exchanges the x and y axes.  
        Used to correct 3d homography-transformed points for, e.g., VIRAT_S_000001 and 2 
    '''
    
    x = map(lambda v: v[xind], track)
    y = map(lambda v: v[yind], track)

    if exchange_x_with_y:
        t = x
        x = y
        y = t
    
    plt.plot(x,y)

def plot_track_2d_image(track, H, xind=3, yind=4):
    H_inv = numpy.linalg.inv(H)
    x3d = map(lambda v: v[xind], track)
    y3d = map(lambda v: v[yind], track)
    d2_track = map(lambda xi,yi: apply_homography_transform(H_inv,xi,yi), x3d, y3d)
    x2d = map(lambda v: v[0], d2_track)
    y2d = map(lambda v: v[1], d2_track)
    plt.plot(x2d,y2d)

    return zip(x2d,y2d)

# -----------------------------------------------------------------------------

def convert_virat_obj_file_to_3d(virat_obj_file, 
                                 homography_file=vdata1_homography,
                                 output_file='test.txt',
                                 save_to_file=True,
                                 plot=True):

    '''
    Top-level fn to convert VIRAT object file from 2d image to 3d homography 
    coordinates.
    
    save_to_file := True: saves homography-transformed 3d points to output_file
    plot         := True: for testing...
                      plots image-boundary and all tracks for original, 3d, and 3d-to-2d

    output file format:
    <id> <duration> <frame> <3d x point> <3d y point> <obj_type>
    '''

    print '\nprocessing VIRAT file "{0}"'.format(virat_obj_file)
    print 'reading homography from "{0}"'.format(homography_file)
    print 'save_to_file = {0}'.format(save_to_file)
    if save_to_file:
        print '     "{0}"'.format(output_file)
    print 'plot = {0}'.format(plot)

    if plot:
        fig_orig_2d_image = plt.figure()
        fig_3d = plt.figure()
        fig_2d_from_3d = plt.figure()

    def extract_line(sline):
        return map(int, sline.strip('\n').strip('\r').split(' '))

    def process_lines(output_fp=None):

        if plot:
            # read first line of file to get first id
            with open(virat_obj_file) as obj_fp:
                (id, duration, frame, 
                 bb_left_top_x, bb_left_top_y, bb_width, bb_height, 
                 obj_type) = extract_line(obj_fp.next())
                cid = id
            print 'cid', cid
                
        # now read entire file and process...
        with open(virat_obj_file) as obj_fp:
            track_orig = []
            track_3d = []
            for sline in obj_fp:
                (id, duration, frame, 
                 bb_left_top_x, bb_left_top_y, bb_width, bb_height, 
                 obj_type) = extract_line(sline)
        
                # convert bbox upper-left corner to bbox bottom-center
                bb_bottom_center_x = bb_left_top_x + (bb_width/2.0)
                bb_bottom_center_y = bb_left_top_y + bb_height

                if plot:
                    track_orig.append((bb_bottom_center_x,bb_bottom_center_y))
                
                (x3d, y3d) = apply_homography_transform(H, bb_bottom_center_x, bb_bottom_center_y)

                if plot:
                    track_3d.append((x3d,y3d))
                
                if output_fp:
                    output_fp.write("{0} {1} {2} {3} {4} {5}\n"\
                                    .format(id, duration, frame, x3d, y3d, obj_type))

                if plot and id!=cid:
                    plt.figure(fig_orig_2d_image.number)
                    plot_track(track_orig,0,1)
                    
                    plt.figure(fig_3d.number)
                    plot_track(track_3d,0,1,exchange_x_with_y=True)

                    plt.figure(fig_2d_from_3d.number)
                    plot_track_2d_image(track_3d, H, 0, 1)

                    print 'id',id
                    cid = id

                    track_orig = []
                    track_3d = []
    
    H = read_homography_matrix_from_file(homography_file)

    # Plot the corners for each image
    if plot:
        corners_orig_2d_image = get_image_corners()
        plt.figure(fig_orig_2d_image.number)
        plt.gca().invert_yaxis()
        plot_corners(corners_orig_2d_image,
                     xl='x image',yl='y image',title='tracks in ORIGINAL 2d image',
                     adjust_border=True)
        
        corners_3d = convert_image_corners_to_3d(H)
        plt.figure(fig_3d.number)
        plt.gca().invert_yaxis()
        plot_corners(corners_3d, 
                     xl='3d x',yl='3d y',title='tracks in 3d coordinates',
                     exchange_x_with_y=True)

        corners_2d_from_3d = convert_corners_from_3d_to_2d(H,corners_3d)
        plt.figure(fig_2d_from_3d.number)
        plt.gca().invert_yaxis()
        plot_corners(corners_2d_from_3d, 
                     xl='x image',yl='y image',title='tracks converted from 3d back to 2d image',
                     adjust_border=True)

    if save_to_file:
        with open(output_file, 'w') as output_fp:
            process_lines(output_fp)
    else:
        process_lines(output_fp=None)

    print "DONE."


# -----------------------------------------------------------------------------
# Process files


convert_virat_obj_file_to_3d(vdata1_file, 
                             vdata1_homography, 
                             'VIRAT_S_000001.viratdata.objects.txt',
                             save_to_file=False, # True,
                             plot=True)

'''
convert_virat_obj_file_to_3d(vdata2_file, 
                             vdata1_homography, 
                             'VIRAT_S_000002.viratdata.objects.txt',
                             save_to_file=False, # True,
                             plot=True)
'''

