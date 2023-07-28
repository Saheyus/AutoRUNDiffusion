import os
from PIL import Image, PngImagePlugin
import argparse
import shutil
import logging
import sys
sys.path.append('F:\\stable-diffusion-webui-docker\\data\\config\\auto\\extensions\\sd-extension-aesthetic-scorer')
import aesthetic_scorer_cli as aesthetic_scorer
from io import BytesIO
import io
import base64
import requests
import yaml


#-------------------------------------------------------------
# LOGGING
#-------------------------------------------------------------

logging.basicConfig(filename='warnings.log', filemode='w', format='%(levelname)s - %(message)s')

#-------------------------------------------------------------
# GLOBAL VARIABLES
#-------------------------------------------------------------

#Paths
backup_path = "./output/backup"
highscore_path = "./output/high_scores"
lowscore_path = "./output/low_scores"
output_dir = './output'

url = "http://127.0.0.1:7860"

start_file_number = 0
output_files = [f for f in os.listdir(output_dir) if f.endswith('.txt') and 'prompt' in f]
output_files = sorted(output_files, key=lambda x: int(x.split('_')[0]))

#-------------------------------------------------------------
# PREPARE
#-------------------------------------------------------------

# IMPORT CONFIG
with open('config.yaml', 'r', encoding='utf-8') as file:
    try:
        config = yaml.safe_load(file)
        locals().update(config)
    except yaml.YAMLError as err:
        print(err)

class Args:
    def __init__(self):
        self.model = 'sac_public_2022_06_29_vit_l_14_linear.pth'
        self.clip = 'ViT-L/14'
        self.exif = False
        self.save = None
        self.quality = 80
        self.input = ['input_image.png']

params = Args()

# Define argument parser
parser = argparse.ArgumentParser(description="Process output files starting from a specific number.")
parser.add_argument("--start", type=int, default=0, help="First file number to start processing from.")

# Parse arguments
args = parser.parse_args()

# Use the argument in your script
start_file_number = args.start

#-------------------------------------------------------------
#FUNCTIONS
#-------------------------------------------------------------

def main_menu():
    global output_files
    def start_processing(output_files):
        print("Cleaning backup folders...")
        clean_directory(backup_path)
        clean_directory(highscore_path)
        clean_directory(lowscore_path)
        print("Backup folders cleaned")
        print("The list of working files is:")
        print(output_files)

        for file in output_files:
            images_mergelist = []
            # Read the contents of the file
            with open(f'{output_dir}/{file}', 'r') as f:
                prompt = f.read()
            print(f"Processing file: {file}")
            print(f"File content (prompt): {prompt}")
            images_mergelist += exec_diffusion(512, 512, prompt, file)
            #image_scores = get_images_and_scores(images_mergelist)
            #image_path = manage_images_scores(image_scores, prompt)
            #upscale_diffusion(image_path, prompt)
        copier_fichiers_png_et_txt(output_dir)

    def start_from(output_files):
        while True:
            try:
                start_file_number = int(input("Please enter a number for 'start_file_number': "))
                # Filter out files whose starting number is less than the input number
                output_files = [f for f in output_files if int(f.split('_')[0]) >= start_file_number]
                # Sort the filtered files
                output_files = sorted(output_files, key=lambda x: int(x.split('_')[0]))
                print("The list of working files is now:")
                print(output_files)
                break
            except ValueError:
                print("That's not a valid number. Please try again.")
        return output_files

    def list_files(output_files):
        while True:
            numbers = input("Please enter a list of numbers, separated by commas (e.g., 1, 2, 5): ")
            try:
                include_list = [int(num.strip()) for num in numbers.split(',')]
                # Filter out files whose starting number is in the exclude list
                output_files = [f for f in output_files if int(f.split('_')[0]) in include_list]
                # Sort the filtered files
                output_files = sorted(output_files, key=lambda x: int(x.split('_')[0]))
                print("The list of working files is now:")
                print(output_files)
                break
            except ValueError:
                print("That's not a valid list of numbers. Please try again.")
        return output_files

    def enter_positive_prompt(output_files):
        pass  # implémentez le comportement ici

    def enter_negative_prompt(output_files):
        pass  # implémentez le comportement ici

    # Mapping des options du menu vers les fonctions
    menu_options = {
        '1': start_processing,
        '2': start_from,
        '3': list_files,
        '4': enter_positive_prompt,
        '5': enter_negative_prompt
    }

    # Boucle infinie pour afficher le menu
    while True:
        print("""
        Menu:
        1. Start processing
        2. Start from a specific file number
        3. Provide a list of files you want to rework
        4. Enter a positive prompt
        5. Enter a negative prompt
        """)

        choix = input("Veuillez choisir une option : ")

        # Exécutez la fonction correspondant au choix de l'utilisateur
        if choix in menu_options:
            result = menu_options[choix](output_files)
            if result is not None:
                output_files = result
        else:
            print("Option inconnue. Veuillez essayer à nouveau.")

def exec_diffusion(x,y, prompt, file):
    images_list=[]
    # Use the content of the file as the prompt
    payload = {
        "prompt": prompt + positivePrompt,
        "steps": steps,
        "width": x,
        "height": y,
        "negative_prompt": negativePrompt,
        "cfg_scale": cfgScale,
		"save_images": False,
		"batch_size": batchSize,
		"sampler_name": "DPM++ 2M Karras",
        "enable_hr": True,
        "hr_scale": 2,
        "denoising_strength": denoisingStrength,
        "hr_upscaler": "4x_fatal_Anime_500000_G",
        "hr_second_pass_steps": highresSteps,
        "hr_sampler_name": "DPM++ 2M Karras",
        "hr_prompt": prompt + positivePrompt,
        "hr_negative_prompt": negativePrompt,
		"restore_faces": False
    }
    print(f"Sending request in {x},{y} for file: {file}")
    response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
    r = response.json()
    filename = os.path.splitext(file)[0]
    #print(r)
    for i, img in enumerate(r['images']):
        image = Image.open(io.BytesIO(base64.b64decode(img.split(",",1)[0])))
        png_payload = {
        	"image": "data:image/png;base64," + img
        }
        response2 = requests.post(url=f'{url}/sdapi/v1/png-info', json=png_payload)
        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("parameters", response2.json().get("info"))
        image.save(f"./output/{filename}_{i}.png", pnginfo=pnginfo)
        images_list.append(f"./output/{filename}_{i}.png")
        print(f"Image saved as: {filename}_{i}.png")
    return images_list

def pil_to_base64(pil_image):
    with BytesIO() as stream:
        pil_image.save(stream, "PNG", pnginfo=None)
        base64_str = str(base64.b64encode(stream.getvalue()), "utf-8")
        return "data:image/png;base64," + base64_str
def upscale_diffusion(image_path, prompt):
    try:
        pil_image = Image.open(image_path)
    except Exception as e:
        print(f"Error openin image with null path: {str(e)}")
        return
    payload = {
        "init_images": [pil_to_base64(pil_image)],
        "denoising_strength": 0.5,
        "prompt": prompt + positivePrompt,
        "negative_prompt": negativePrompt,
        "steps": 40,
        "cfg_scale": cfgScale,
        "width": 1024,
        "height": 1024,
        "restore_faces": False,
        "sampler_name": "DPM++ 2M Karras",
        "script_name": "SD upscale",
        "save_images": False,
    }
    response = requests.post(url=f'{url}/sdapi/v1/img2img', json=payload)
    data = response.json()
    #print(data)  # Ajoutez cette ligne pour voir ce qui est réellement renvoyé.
    img_data = base64.b64decode(data["images"][0])
    img = Image.open(io.BytesIO(img_data))
    img.save(image_path)
    print("image saved on path: " + image_path)

def get_images_and_scores(image_paths):
    image_scores = []  # Liste pour stocker les tuples (image, score)
    scorer_path = r"F:\stable-diffusion-webui-docker\data\config\auto1\extensions\sd-extension-aesthetic-scorer\aesthetic-scorer-cli.py"
    
    for image_path in image_paths:
        # Ouvrir l'image
        img = Image.open(image_path)

        # Récupérer le score
        score = aesthetic_scorer.aesthetic_score(image_path, params)

        if score is not None:  # Add this check
            image_scores.append((image_path, score))  # Ajouter le tuple (image, score) à la liste

    return image_scores

def manage_images_scores(image_scores, prompt):
    if image_scores:  # Vérifiez si image_scores n'est pas vide
        # Trouver le score maximal dans la liste des tuples
        max_score = max(image_scores, key=lambda x: x[1])[1]

        # Parcourir la liste des tuples
        for image_path, score in image_scores:
            if score == max_score:
                if (score >= 8.2):
                    logging.warning("High score detected!")
                    logging.warning("The image " + image_path + " score is " + str(score))
                    shutil.copy(image_path, highscore_path)
                elif (score <= 6.8):
                    logging.warning("Low score detected!")
                    logging.warning("The selected image " + image_path + " score is only " + str(score))
                    shutil.copy(image_path, lowscore_path)
                print("Upscaling " + image_path)
                upscale_diffusion(image_path, prompt)
            else:
                print("Moving in backup " + image_path)
                shutil.move(image_path, backup_path)
    else:
        print("No images found with a 'score' in their metadata.")

def clean_directory(path):
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

def copier_fichiers_png_et_txt(source):
    # Vérifier si le dossier source existe
    if not os.path.exists(source):
        print("Le dossier source n'existe pas.")
        return

    # Demander confirmation avant de copier les fichiers
    reponse = input(f"Voulez-vous copier les fichiers du dossier output vers la gallerie ? (Oui/Non): ")
    if reponse.lower() != "oui":
        print("Opération annulée.")
        return
    folderName = input(f"Saisissez un nom de dossier :")
    # Créer le dossier destination avec le sous-dossier correspondant
    dossier_destination = os.path.join("F:/Projets/AutoDiffusion/AutoDiffusion/wwwroot/galleries", folderName)
    os.makedirs(dossier_destination, exist_ok=True)

    # Parcourir les fichiers du dossier source
    for fichier in os.listdir(source):
        chemin_fichier_source = os.path.join(source, fichier)

        # Copier uniquement les fichiers .png et .txt
        if os.path.isfile(chemin_fichier_source) and fichier.endswith(('.png', '.txt', '.csv')):
            chemin_fichier_destination = os.path.join(dossier_destination, fichier)
            shutil.copy(chemin_fichier_source, chemin_fichier_destination)
            print(f"Le fichier {fichier} a été copié avec succès.")

    print("La copie des fichiers est terminée.")

#-------------------------------------------------------------
# MAIN CODE
#-------------------------------------------------------------

# Appeler la fonction main_menu lors du démarrage de l'application
if __name__ == "__main__":
    main_menu()

