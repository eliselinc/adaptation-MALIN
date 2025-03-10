import sys
import os
from google import genai
from pdfminer.high_level import extract_text
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("gemini_key")

# Initialize Gemini API client
client = genai.Client(api_key=api_key)

# Function to extract text from a PDF and save it to a file
def extract_pdf_text(pdf_filename, output_filename):
    text = extract_text(pdf_filename)
    with open(output_filename, "w", encoding="utf-8") as file:
        file.write(text)

# Read the prompt and input files
def read_file(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return file.read()

# Check if the PDF filename is passed as an argument
if len(sys.argv) < 2:
    print("Please provide the PDF filename as an argument.")
    sys.exit(1)

# Get the PDF filename from the command-line arguments
pdf_filename = sys.argv[1]
input_filename = 'input.txt'

# Ensure the file exists in the same folder
if not os.path.isfile(pdf_filename):
    print(f"The file {pdf_filename} does not exist in the current directory.")
    sys.exit(1)

# Extract text from PDF and save it to input.txt
extract_pdf_text(pdf_filename, input_filename)

# Read the prompt and input text
prompt = read_file("prompt.txt")
input_text = read_file(input_filename)

# Combine the prompt and input text
full_prompt = f"{prompt}\n\n>>>>>>>>input:\n{input_text}"

# Send request to Gemini API
response = client.models.generate_content(
    model="gemini-2.0-flash", contents=full_prompt
)

# Print the extracted exercises as JSON
print(response.text)
