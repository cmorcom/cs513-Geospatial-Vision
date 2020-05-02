Project Ideas:
    
    By using various clustering settings (farthest distance and filtering), we are able to identify the speed 
    and trajectory of the car and the objects around it based on a clustering analysis.

    Our Results are stored in './results'. You must open a web page to view them.
    We tested the data with various settings and filtered out some points as noise. 
    The filenames show which settings were changes in the DBSCAN clustering analysis.

    Depending on the filtering, we can omit features, but in the final version,
    we chose to show all of the objects we could identify.

    This implementation is purely based on pointcloud analysis and does not use the camera images at all.

    

Notes:
You can see results in the results folder:
    -- please enable webGL in "chrome://flags" to open the pointcloud.html
    -- RoadRecognition.html tries to cluster the pointcloud based on other parameters (earlier version but still relevant)

Input data:

Coordinate Range: 
    (N/S) Latitude:   45.90487933  to  45.90329572 
    (W/E) Longitude:  11.02701384  to  11.02965733
     (Z)  Altitude:   221.8044     to  234.5053

    (UTM) (E,N,Zone): (657224.13, 5085306.11, 32T) to 
                      (657433.61, 5085476.77, 32T)

*** CSV is preprocessed and sorted By lat, then lon, then alt, then intensity ***

final_project_point_cloud.fuse
    Point cloud data.
    Data format:
        [latitude] [longitude] [altitude] [intensity]

image/[front/back/left/right].jpg
    Images from camera. The Field of View (FOV) is 90 degree, and you can assume there is no distortion.

image/camera.config
    Camera information.
    Data format:
        [camera latitude], [camera longitude], [camera altitude], [camera quaternion S], [camera quaternion X], [camera quaternion Y], [camera quaternion Z]

Extra Data:

trajectory.fuse
    Trajectory of data capture vehicle.
    Data format:
        [latitude] [longitude] [altitude] [intensity]

Output:
    Using the point cloud and images, generate pointclouds of objects:
        - isolated points pertaining to all objects on road


Methodology:
    -- process all points and subtract the min value of the bounding box 