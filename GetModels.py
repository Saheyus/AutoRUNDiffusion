import openai

# Set your API key
openai.api_key = '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'

# Request the list of available engines
response = openai.Engine.list()

# Print the list of available engines
for engine in response['data']:
    print(engine['id'])