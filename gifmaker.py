import os
import imageio

png_dir = 'generations1'
images = []
for file_name in os.listdir(png_dir):
    if file_name.endswith('.bmp'):
        file_path = os.path.join(png_dir, file_name)
        images.append(imageio.imread(file_path))
imageio.mimsave('final.gif', images, fps=55)