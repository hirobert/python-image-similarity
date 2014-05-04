# -*- coding: utf-8 -*-

# http://stackoverflow.com/questions/14404731/pyhon-image-comparison-regardless-of-size
# http://www.guguncube.com/1656/python-image-similarity-comparison-using-several-techniques

import os
import errno
import itertools
import requests
from PIL import Image
from numpy import average, linalg, dot
 
 
def main():
    import tempfile
    import shutil

    base_directory = tempfile.mkdtemp()

    #array of image urls we want checked, they will each be compared with all other images in the list
    image_urls = ['http://assets-s3.usmagazine.com/uploads/assets/articles/69549-gisele-bundchen-rides-atv-in-bikini-with-13-month-old-daughter-vivian-forgoes-he/1389720163_gisele-bundchen-article.jpg',
                        'http://assets-s3.usmagazine.com/uploads/assets/photo_galleries/regular_galleries/1984-golden-globes-celebrity-pda/1389715650_golden-globes-pda-350.jpg',
                        'http://assets-s3.usmagazine.com/uploads/assets/article_photos/617e98a3ef19b29fc33a0312cdb2bd22a5ddef1e.jpg',
                        'http://assets-s3.usmagazine.com/uploads/assets/articles/69549-gisele-bundchen-rides-atv-in-bikini-with-13-month-old-daughter-vivian-forgoes-he/1389720163_gisele-bundchen-zoom.jpg',
                    ]

    print compare_similarity(image_urls, base_directory)

    #delete all files in directory when done
    shutil.rmtree(base_directory)

def compare_similarity(image_urls, download_base_directory):
    largest_similarity = 0.0
    matching_images = []

    image_comparison_dict = {
        'similarity': largest_similarity,
        'images': []
    }

    #create list of possible pairings
    url_pairs = list(itertools.combinations(image_urls, 2))

    for pair in url_pairs:
        filepath_url = []
        for url in pair:
            url = url.strip()
            filename = url.split('/')[-1]
            filepath = os.path.join(download_base_directory, filename)
            mkdir_p_filepath(filepath)
            if not os.path.exists(filepath):
                download_file(url, filepath)
            filepath_url.append((filepath, url))
        
        image_filepath1, url1 = filepath_url[0][0], filepath_url[0][1]
        image_filepath2, url2 = filepath_url[1][0], filepath_url[1][1]
 
        similarity = image_similarity_vectors_via_numpy(image_filepath1, image_filepath2)
         
        if similarity > largest_similarity:
            largest_similarity = similarity
            matching_images = [url1, url2]
            image_comparison_dict = {
                'similarity': largest_similarity,
                'images': matching_images
            }

    return image_comparison_dict

def image_similarity_vectors_via_numpy(filepath1, filepath2):

    image1 = Image.open(filepath1)
    image2 = Image.open(filepath2)
 
    image1 = get_thumbnail(image1)
    image2 = get_thumbnail(image2)
    
    images = [image1, image2]
    vectors = []
    norms = []
    for image in images:
        vector = []
        for pixel_tuple in image.getdata():
            vector.append(average(pixel_tuple))
        vectors.append(vector)
        norms.append(linalg.norm(vector, 2))
    a, b = vectors
    a_norm, b_norm = norms
    # If we did not resize the images to be equal, we would get an error here
    # ValueError: matrices are not aligned
    res = dot(a / a_norm, b / b_norm)
    return res
 
def get_thumbnail(image, size=(128,128), greyscale=False):
    #get a smaller version of the image - makes comparison much faster/easier
    image = image.resize(size, Image.ANTIALIAS)
    if greyscale:
        #convert image to greyscale
        image = image.convert('L')
    return image
 
def mkdir_p_filepath(path):
    dirpath = os.path.dirname(os.path.abspath(path))
    mkdir_p(dirpath)
 
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def download_file(url, filepath):
    _USER_AGENT = 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36'
    headers = { 'user-agent': _USER_AGENT }
    r = requests.get(url, headers=headers, timeout=60, stream=True)
    with open(filepath, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk:
                f.write(chunk)
                f.flush()
    return filepath
 
 
if __name__ == "__main__":
    main()