#######################################################################
# Init
import pyzed.sl as sl
import math

def zed_init(args):
    # Create a Camera object
    zed = sl.Camera()

    # Create a InitParameters object and set configuration parameters
    init_params = sl.InitParameters()
    if args.resolution == "HD720":
        init_params.camera_resolution = sl.RESOLUTION.HD720
        frame_width = 1280
        frame_length = 720
    elif args.resolution == "HD1080":
        init_params.camera_resolution = sl.RESOLUTION.HD1080
        frame_width = 1920
        frame_length = 1080
    elif args.resolution == "HD2K":
        init_params.camera_resolution = sl.RESOLUTION.HD2K
        frame_width = 2560
        frame_length = 1440
    init_params.camera_fps = args.fps  # Set fps based on input

    init_params.depth_mode = sl.DEPTH_MODE.ULTRA  # Use ULTRA depth mode
    init_params.coordinate_units = sl.UNIT.MILLIMETER  # Use meter units (for depth measurements)
    # Point cloud setting
    mirror_ref = sl.Transform()
    mirror_ref.set_translation(sl.Translation(2.75,4.0,0))

    # Open the camera
    status = zed.open(init_params)
    if status != sl.ERROR_CODE.SUCCESS: #Ensure the camera has opened succesfully
        print('Camera Open : '+repr(status)+'. Exit program.')
        exit()

    # Create and set RuntimeParameters after opening the camera
    image = sl.Mat()
    depth = sl.Mat()
    point_cloud = sl.Mat()
    runtime_parameters = sl.RuntimeParameters()

    # zed.set_camera_settings(sl.VIDEO_SETTINGS.EXPOSURE, -1)
    zed.set_camera_settings(sl.VIDEO_SETTINGS.EXPOSURE, 30)
    # zed.set_camera_settings(sl.VIDEO_SETTINGS.BRIGHTNESS, 50)
    # zed.set_camera_settings(sl.VIDEO_SETTINGS.CONTRAST, 30)
    # zed.set_camera_settings(sl.VIDEO_SETTINGS.HUE, 50)
    # zed.set_camera_settings(sl.VIDEO_SETTINGS.SATURATION, 30)
    zed.set_camera_settings(sl.VIDEO_SETTINGS.SHARPNESS, 60)

    # calibration_params = zed.get_camera_information().camera_configuration.calibration_parameters
    # print(calibration_params.left_cam.disto[0])

    return zed, image, depth, point_cloud, runtime_parameters, frame_width, frame_length

