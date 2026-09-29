from nerfstudio.data.utils.colmap_parsing_utils import read_cameras_binary, read_images_binary, read_points3D_binary
print("Reading cameras...")
read_cameras_binary('/tmp/ns-test/cameras.bin')
print("Reading images...")
read_images_binary('/tmp/ns-test/images.bin')
print("Reading points...")
read_points3D_binary('/tmp/ns-test/points3D.bin')
print("Done!")
