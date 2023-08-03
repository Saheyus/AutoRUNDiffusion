# AutoGPTprompt

AutoGPTprompt is a Python script that utilizes the GPT-4 model from OpenAI for various text processing tasks. It can be run in server mode, where it listens for incoming gRPC requests, or in interactive mode, where it processes input text from a file.

## Features

1. **gRPC Server**: The program runs a gRPC server that receives and processes text input, returning processed text as output.

2. **Context Management**: The script handles a 'context' throughout the text processing, which includes the input text, local context, a flag for local context status, and a generic context.

3. **Text Processing**: The main text processing function (`main_menu`) presents the user with a menu of options, allowing them to control the processing.

4. **Text Splitting and Numbering**: The program includes functions to split and number paragraphs in the text.

5. **Calling GPT-4 API**: The program calls the OpenAI GPT-4 model to generate text based on the input and the context.

6. **Local Context Generation**: The program includes a function to generate a local context by calling the GPT-4 API with instructions for context and the input text.

7. **Writing to Output Files**: The program writes the generated responses and context to output files.

## Usage

To run the program in server mode:

```bash
python AutoGPTprompt.py --server
To run the program in interactive mode:

```bash
python AutoGPTprompt.py

In interactive mode, the program will present you with a menu of options. You can choose to:

Start processing: Begins the text processing based on the current context and input.
Start from a specific file number: You can specify a file number, and the program will only process files starting from that number.
Provide a list of files you want to rework: You can provide a list of file numbers, and the program will only process those files.
Enter a generic Context applied to all requests: You can enter a generic context that will be applied to all requests.
(Re)Generate the local context: The program will regenerate the local context based on the input text.
Enable/Disable local context: You can choose to enable or disable the use of local context in processing.
List the file names to be processed: The program will list all the file names that are going to be processed.
Configurations
The program reads configurations from a config.yaml file. Make sure this file exists and contains all the necessary configurations.

##Dependencies
This program requires the openai, os, time, pandas, io, textwrap, yaml, and grpc libraries.

# AutoDiffusion

AutoDiffusion is a Python script that utilizes the Stable Diffusion model for various image processing tasks. It can generate and upscale images based on textual prompts and rank them using an aesthetic scorer model.

## Features

1. **Interactive Menu**: The program presents the user with a menu of options, allowing them to control the processing.

2. **Image Generation**: The program generates images based on textual prompts using the Stable Diffusion model.

3. **Image Upscaling**: The program upscales generated images.

4. **Image Scoring**: The program ranks images based on their aesthetics using an aesthetic scorer model.

5. **File Management**: The program manages images based on their scores, moving them to different folders.

## Usage

To run the program:

```bash
python AutoDiffusion.py

In the interactive menu, you can choose to:

Start processing: Begins the image processing.
Start from a specific file number: You can specify a file number, and the program will only process files starting from that number.
Provide a list of files you want to rework: You can provide a list of file numbers, and the program will only process those files.
Enter a positive prompt: You can enter a positive prompt that will be used in the image generation.
Enter a negative prompt: You can enter a negative prompt that will be used in the image generation.
Configurations
The program reads configurations from a config.yaml file. Make sure this file exists and contains all the necessary configurations. The configurations include API keys and other settings.

##Dependencies
This program requires the following Python libraries:

os
PIL
argparse
shutil
logging
sys
aesthetic_scorer_cli (custom module)
io
base64
requests
yaml

To install these dependencies, you can use pip:

pip install os Pillow argparse shutil logging io base64 requests PyYAML
