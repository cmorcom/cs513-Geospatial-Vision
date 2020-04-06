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
    Using the point cloud and images, generate layered images:
        - isolated points pertaining to specified object (road boundaries)

Methodology:
    -- process all points and subtract the min value of the bounding box 