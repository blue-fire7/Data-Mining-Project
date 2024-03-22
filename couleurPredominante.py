import math
import numpy as np
from sklearn.cluster import MiniBatchKMeans
import os
import json
from PIL import Image
import webcolors

#renvoie un tableau de pixel RVG
def preprocess_image(image_path):
    imgfile = Image.open(image_path)
    # Réduire la taille de l'image
    imgfile = imgfile.resize((imgfile.width // 4, imgfile.height // 4))
    numarray = np.array(imgfile.getdata(), np.uint8)
    return numarray

def get_dominant_colors(pixels, k=3):
    clusters = MiniBatchKMeans(n_clusters=k, n_init=2)
    clusters.fit(pixels)
    colors_hex = []
    colors_names = []
    for i in range(k):
        color = (
            "#%02x%02x%02x"
            % (
                math.ceil(clusters.cluster_centers_[i][0]),
                math.ceil(clusters.cluster_centers_[i][1]),
                math.ceil(clusters.cluster_centers_[i][2]),
            )
        )
        color_name = get_colour_name(color)
        colors_hex.append(color)
        colors_names.append(color_name)
    return colors_hex, colors_names

def get_colour_name(hex_color):
    rgb_triplet = webcolors.hex_to_rgb(hex_color)
    min_colours = {}
    for key, name in webcolors.CSS21_HEX_TO_NAMES.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - rgb_triplet[0]) ** 2
        gd = (g_c - rgb_triplet[1]) ** 2
        bd = (b_c - rgb_triplet[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]

def get_image_info(image_path):
    # Ouvrir l'image avec PIL
    with Image.open(image_path) as img:
        # Récupérer les informations demandées
        image_info = {
            "taille": img.size,
            "format": img.format,
            "orientation": "paysage" if img.width > img.height else "portrait" if img.height > img.width else "carré"
        }

        exif_info = img._getexif()
        if exif_info:
            # Ajouter la date de création et le modèle d'appareil photo si disponibles
            image_info["date_creation"] = exif_info.get(36867)  # 36867 est le code EXIF pour la date de création
            image_info["modele_appareil"] = exif_info.get(272)   # 272 est le code EXIF pour le modèle d'appareil photo

    return image_info

def get_images_info(directory):
    # Liste des fichiers dans le répertoire
    image_files = os.listdir(directory)

    #nb couleur prédominante
    num_clusters = 2

    # Dictionnaire pour stocker les informations de chaque image
    images_info = {}
    
    i = 0
    
    # Parcourir chaque fichier image et récupérer les informations
    for image_file in image_files:
        image_path = os.path.join(directory, image_file)
        # Vérifier si le fichier est une image
        if os.path.isfile(image_path) and image_path.lower().endswith(('.jpg', '.jpeg', '.png', '.JPG', '.gif')):
            i = i + 1
            print("image : ", image_path)
            #Meta data
            images_info[image_file] = get_image_info(image_path)

            #couleurs dominante
            preprocessed_image = preprocess_image(image_path)
            dominant_colors_hex ,dominant_colors_name  = get_dominant_colors(preprocessed_image, k=num_clusters)
            images_info[image_file]["couleurs_predominante_hex"] = dominant_colors_hex
            images_info[image_file]["couleurs_predominante_name"] = dominant_colors_name

    return images_info


# Répertoire contenant les images
directory = "./Images"

# Récupérer les informations des images
images_info = get_images_info(directory)

# Enregistrer les informations dans un fichier JSON
output_json_file = 'image_info_2.json'
with open(output_json_file, 'w') as json_file:
    json.dump(images_info, json_file, indent=4)

print("Les informations des images ont été enregistrées dans le fichier:", output_json_file)