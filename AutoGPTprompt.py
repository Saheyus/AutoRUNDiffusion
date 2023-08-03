import argparse

import openai
import os
import time
import pandas as pd
import io
import textwrap
import yaml
import grpc
from concurrent import futures
import gpt_service_pb2
import gpt_service_pb2_grpc
import chardet

# IMPORT CONFIG
with open('config.yaml', 'r', encoding='utf-8') as file:
    try:
        config = yaml.safe_load(file)
        locals().update(config)
    except yaml.YAMLError as err:
        print(err)

        
# IMPORT PASSWORDS
with open('passwords.yaml', 'r', encoding='utf-8') as file:
    try:
        passwords = yaml.safe_load(file)
        locals().update(passwords)
    except yaml.YAMLError as err:
        print(err)

class Context:
    def __init__(self, inputs, localContext, localContextStatus, genericContext):
        self.inputs = inputs
        self.localContext = localContext
        self.localContextStatus = localContextStatus
        self.genericContext = genericContext
        self.df = pd.DataFrame()

# Set API key
openai.api_key = chatGPTKey

# Variables
max_retries = 3
start_paragraph = 0
genericContext = ""
df = pd.DataFrame()
context_path = ".\\output\\0_context.csv"

#GRPC SERVER
class GPTServiceServicer(gpt_service_pb2_grpc.GPTServiceServicer):
    def ProcessText(self, request, context):
        # Initialize context
        context = Context(inputs, "", True, "")

        # Split the request text into inputs and filter out empty ones
        inputs = [p for p in request.text.split('\n') if p.strip()]
        context.inputs = inputs

        textWithNumbers = add_paragraph_numbers(request.text)

        # Call main_menu function with context
        result = main_menu(context)

        return gpt_service_pb2.ProcessReply(result=result)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    gpt_service_pb2_grpc.add_GPTServiceServicer_to_server(GPTServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

def main():
    parser = argparse.ArgumentParser(description='Run the script in server mode or interactive mode.')
    parser.add_argument('--server', action='store_true', help='Run in server mode')

    args = parser.parse_args()

    if args.server:
        print('Running in server mode...')
        serve()
    else:
        print('Running in interactive mode...')
        textWithNumbers = add_paragraph_numbers(text)
        # Write input with paragraph numbers
        with open('inputWithNumbers.txt', 'w', encoding='utf-8') as f:
            f.write(textWithNumbers)

        print(f'Split text into {len(inputs)} inputs.')
        main_menu(context, textWithNumbers)

#ADDITIONAL FUNCTIONS
def add_paragraph_numbers(text):
    paragraphs = text.split('\n')
    numbered_paragraphs = []
    counter = 1
    for p in paragraphs:
        if p.strip() != '':  # ignore empty lines
            numbered_paragraphs.append(f'{counter}. {p}')
            counter += 1
    return '\n'.join(numbered_paragraphs)

def divide_text(text, max_token):
    words = text.split()
    token_count = 0
    divided_text = []
    current_text = ''

    for word in words:
        token_count += len(word.split(" "))
        if token_count > max_token:
            divided_text.append(current_text)
            current_text = word
            token_count = len(word.split(" "))
        else:
            current_text += ' ' + word
    divided_text.append(current_text)

    return divided_text

def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']

#MAIN FUNCTIONS
def main_menu(context, textWithNumbers):
    def start_processing(context):
        if (context.genericContext != ""):
            print("The generic context is:")
            print(context.genericContext)
        if context.localContextStatus :
            if os.path.exists(context_path):
                context.df = pd.read_csv(context_path, delimiter=';', header=None, names=['Beginning', 'End', 'Place', 'Time', 'Characters'])
                print("The current local context is:")
                print(context.df)
            else:
                local_context(context)

            # Ask the user for validation
            while True:
                print("\nMenu:")
                print("1. Validate the generated context")
                print("2. Regenerate the context")
                print("3. Edit the context manually")

                user_input = input("\nChoose an option:")

                if user_input == '1':
                    break  # Continue with the generated context
                elif user_input == '2':
                    local_context(context)  # Regenerate the context
                elif user_input == '3':
                    # Edit the context manually
                    print("Please edit the file .\\output\\0_context.csv manually.")
                    input("Press Enter once you've finished editing.")
                    context.df = pd.read_csv(context_path, delimiter=';', header=None, names=['Beginning', 'End', 'Place', 'Time', 'Characters'])
                    print("The current local context is:")
                    print(context.df)
                else:
                    print("Invalid choice. Please enter 1, 2, or 3.")


        # Create output directory if not exists
        output_dir = './output'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print('Output directory created.')

        for i, paragraph in enumerate(context.inputs):
            retries = 0
            # Ensure paragraph has content
            if i >= start_paragraph and paragraph.strip() != '':
                print(f'Processing paragraph {i + 1}...')
                print(paragraph)
                if context.localContextStatus:
                    pickedLocalContext = context.df[(context.df['Beginning'] <= i + 1) & (context.df['End'] >= i + 1)]
                    builtLocalContext = "Place: " + pickedLocalContext['Place'].values[0] + "\\nTime of day: " + pickedLocalContext['Time'].values[0] + "\\nCharacters: " + pickedLocalContext['Characters'].values[0]
                else:
                    builtLocalContext = ""
                    with open(f'output/0_context.csv', 'w', encoding='utf-8-sig') as output_file:
                        output_file.write("")
                while retries < max_retries:
                    try:
                        # Call GPT-4 API with the paragraph + appended text
                        response = openai.ChatCompletion.create(model="gpt-4", messages=[
                            {"role": "user",
                             "content": stableDiffusionRules + samplePrompts + "\\nPARAGRAPHS\\n" + paragraph + context.genericContext + builtLocalContext + finalInstruction}])
                        print(f'Response for paragraph {i + 1} received.')
                        # If successful, break the loop
                        break
                    except Exception as e:
                        print(f"Error: {e}. Retry {retries + 1} of {max_retries}.")
                        retries += 1
                        # Wait for 2 seconds before trying again
                        time.sleep(2)
                # Write response to a unique text file
                with open(f'{output_dir}/{i + 1}_prompt.txt', 'w', encoding='utf-8-sig') as output_file:
                    print(response.choices[0].message.content)
                    output_file.write(response.choices[0].message.content.strip('\"'))
                    print(f'Response for paragraph {i + 1} written to file.')
                with open(f'{output_dir}/{i + 1}_paragraphe.txt', 'w', encoding='utf-8-sig') as output_file:
                    output_file.write(paragraph)

        print('All inputs processed.')
        return context

    def start_from(context):
        while True:
            try:
                start_file_number = int(input("Please enter a number for 'start_file_number': "))
                # Filter out files whose starting number is less than the input number
                context.inputs = [f for f in context.inputs if int(f.split('_')[0]) >= start_file_number]
                # Sort the filtered files
                context.inputs = sorted(context.inputs, key=lambda x: int(x.split('_')[0]))
                print("The list of working files is now:")
                print(context.inputs)
                break
            except ValueError:
                print("That's not a valid number. Please try again.")
        return context

    def list_files(context):
        while True:
            numbers = input("Please enter a list of numbers, separated by commas (e.g., 1,2,5): ")
            try:
                include_list = [int(num.strip()) for num in numbers.split(',')]
                # Filter out files whose index is not in the include list
                context.inputs = [f for i, f in enumerate(context.inputs) if i + 1 in include_list]
                print("The list of working prompts is now:")
                for i, f in enumerate(context.inputs):
                    print(f"{i + 1}: {f}")
                break
                break
            except ValueError:
                print("That's not a valid list of numbers. Please try again.")
        return context

    def enter_genericContext(context):
        context.genericContext = input("Please enter the generic context: ")
        context.genericContext = "CONTEXTE GENERIQUE\\n\\n" + context.genericContext
        return context

    def local_context_onoff(context):
        context.localContextStatus = not context.localContextStatus
        return context

    def local_context(context):
        print(f'Asking for local contexts.')
        divided_texts = divide_text(textWithNumbers, 4000)
        for text in divided_texts:
            retries = 0
            while retries < max_retries:
                try:
                    # Call GPT-4 API with the instructions for context + input text
                    response = openai.ChatCompletion.create(model="gpt-4", messages=[
                        {"role": "user",
                         "content": "Here is a text divided in paragraphs:\n\n" + text + "\n\n" + contextRules}])
                    print(f'Response received.')
                    # If successful, break the loop
                    break
                except Exception as e:
                    print(f"Error: {e}. Retry {retries + 1} of {max_retries}.")
                    retries += 1
                    # Wait for 2 seconds before trying again
                    time.sleep(2)
            # Write response to a unique text file
            with open(f'output/0_context.csv', 'w') as output_file:
                output_file.write(response.choices[0].message.content.strip())
                print(f'Response written to file 0_context.')
        # Read the CSV file
        localContext = response.choices[0].message.content.strip()
        # Create a buffer from the string
        csv_buffer = io.StringIO(localContext)
        # Read the CSV data into a DataFrame
        context.df = pd.read_csv(csv_buffer, delimiter=';', header=None, names=['Beginning', 'End', 'Place', 'Time', 'Characters'])
        print("The current local context is:")
        print(context.df)
        return context.df

    def list_working_files(inputs, localContext):
        print("The list of working files is:")
        print(inputs)

    # Mapping des options du menu vers les fonctions
    menu_options = {
        '1': start_processing,
        '2': start_from,
        '3': list_files,
        '4': enter_genericContext,
        '5': local_context,
        '6': local_context_onoff,
        '7': list_working_files,
    }

    # Boucle infinie pour afficher le menu
    while True:
        print(f"""
        Menu:
        1. Start processing
        2. Start from a specific file number
        3. Provide a list of files you want to rework
        4. Enter a generic Context applied to all requests
        5. (Re)Generate the local context
        6. Enable/Disable local context
        7. List the file names to be processed
        """)

        choix = input("Veuillez choisir une option : ")

        # Exécutez la fonction correspondant au choix de l'utilisateur
        if choix in menu_options:
            result = menu_options[choix](context)
        else:
            print("Option inconnue. Veuillez essayer à nouveau.")

if __name__ == '__main__':
    print('Reading file...')
    # Read input file
    input_encoding = detect_encoding('.\\input.txt')
    with open('.\\input.txt', 'r', encoding=input_encoding) as f:
        text = f.read()

    # Split the text into inputs and filter out empty ones
    inputs = [p for p in text.split('\n') if p.strip()]
    context = Context(inputs, "", True, "")

    #Panda dataset config
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.width', None)
    main()