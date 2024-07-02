import PyPDF2
import openai
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define a glossary of standard terms for wood
GLOSSARY_WOOD = {
    "materials": ["wood"],
    "deterioration_mechanisms": [
        "fungal decay", "insect attack", "termite attack", "UV exposure", "mechanical wear",
        "impact of fluids", "moisture changes", "oxidation", "cracking", "delamination"
    ],
    "physical_changes": [
        "changes in structure geometry", "changes in material macro- & microstructure",
        "mechanical parameters", "discontinuity of material", "water & gas resistance",
        "chemical constitution", "density changes", "splitting", "warping", "cupping",
        "color changes", "surface roughness", "erosion", "swelling", "shrinkage"
    ],
    "ndt_methods": [
        "visual inspection", "moisture content measurement", "ultrasonic", "X-ray imaging",
        "thermal imaging", "acoustic emission", "deformation measurement", "stress wave testing",
        "hygrometer", "infrared thermography", "colorimetry", "surface roughness tester",
        "laser scanning", "drilling resistance", "neutron imaging", "computed tomography",
        "IR/NIR radiation", "electrical resistance", "modulus of elasticity measurements",
        "sound transmission measurements", "video image correlation", 
        "ESPI (Electronic Speckle Pattern Interferometry)", "spectroscopy", "radiography",
        "synchrotron-based tomography", "radar inspection"
    ]
}

def extract_text_from_pdf(pdf_path):
    logging.info(f"Extracting text from PDF: {pdf_path}")
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    logging.info(f"Extracted {len(text)} characters from PDF")
    return text

def format_material_info(material, deterioration_mechanisms, physical_changes, ndt_methods):
    return f"{material}; {deterioration_mechanisms}; {physical_changes}; {ndt_methods}"

def normalize_extracted_data(data):
    def normalize_term(term, category):
        for standard_term in GLOSSARY_WOOD[category]:
            if standard_term.lower() in term.lower():
                return standard_term
        return term

    material, deterioration_mechanisms, physical_changes, ndt_methods = data
    material = normalize_term(material, "materials")
    deterioration_mechanisms = normalize_term(deterioration_mechanisms, "deterioration_mechanisms")
    physical_changes = normalize_term(physical_changes, "physical_changes")
    ndt_methods = normalize_term(ndt_methods, "ndt_methods")
    
    return format_material_info(material, deterioration_mechanisms, physical_changes, ndt_methods)

def material_deterioration_info(text_chunk):
    prompt = f"""
You are a helpful assistant. Extract and format the following categories from the text:

Material; Material Deterioration Mechanisms; Physical Changes; NDT Methods.

Provide the output in this exact format:

1. Material; Material Deterioration Mechanisms; Physical Changes; NDT Methods.

Material can be wood. Material Deterioration Mechanisms are issues like fungal decay, termite attack, and more. Physical changes are symptoms such as splitting, warping, cupping, and more. NDT Methods include techniques like visual inspection, thermal imaging, ultrasonic testing, and more.

Ensure the output adheres to the following guidelines:
- Include specific aspects such as changes in structure geometry, changes in material macro- & microstructure, mechanical parameters, discontinuity of material, water & gas resistance, and chemical constitution for Physical Changes.
- Restrict the output to wood only.
- Material Deterioration Mechanisms are like the symptoms (e.g., cracking, termite attack), while the Physical Changes are the illness (e.g., changes in structure geometry, discontinuity of material).
- NDT Methods can be delivered as NDT sensors, NDT devices, or NDT technologies.
- Be exhaustive and thorough in reading and output. Do not provide just examples; provide a comprehensive extraction.
- For every deterioration mechanism, there are likely more than one physical changes. Consider this when creating the tuples.
- Ensure each tuple is formatted exactly as shown in the examples, separated by semicolons.

Examples:
1. Wood; fungal decay; density changes; drilling resistance
2. Wood; termite attack; splitting; ultrasonic

Here is the text:
{text_chunk}

Ensure each entry is formatted exactly as specified with semicolons separating the fields and numbered entries. Do not include additional labels or descriptors in the output.
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o",  # Using GPT-4
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=4000  # Increased max tokens for more comprehensive responses
    )
    
    result = response.choices[0].message['content'].strip()
    logging.info(f"API Response: {result[:500]}")  # Log only first 500 characters to avoid clutter
    return result

def extract_material_info_from_text(text):
    max_chunk_size = 10000  # Increased chunk size for more context
    chunks = [text[i:i + max_chunk_size] for i in range(0, len(text), max_chunk_size)]
    
    logging.info(f"Divided text into {len(chunks)} chunks")
    extracted_data = []
    for i, chunk in enumerate(chunks):
        logging.info(f"Processing chunk {i+1}/{len(chunks)}")
        result = material_deterioration_info(chunk)
        logging.info(f"Result for chunk {i+1}: {result[:200]}...")  # Log first 200 characters of result
        entries = result.split('\n')
        for entry in entries:
            if entry.strip() and '; ' in entry:
                parts = entry.split('. ', 1)[-1].split('; ')
                if len(parts) == 4:
                    extracted_data.append(parts)
    
    logging.info(f"Total extracted data items: {len(extracted_data)}")
    return extracted_data

def post_process_extracted_data(extracted_data):
    formatted_info = []
    seen_entries = set()
    for parts in extracted_data:
        if all(part.strip() for part in parts):  # Ensure all parts have content
            normalized_entry = normalize_extracted_data(parts)
            if normalized_entry not in seen_entries:
                seen_entries.add(normalized_entry)
                formatted_info.append(normalized_entry)
    return formatted_info

# Main execution
if __name__ == "__main__":
    openai.api_key = 'Placeholder_API'

    pdf_path = 'data/bricks/ndt_bricks.pdf'  # Adjust the path to match your file
    text = extract_text_from_pdf(pdf_path)

    print(f"Extracted text length: {len(text)}")
    print("First 500 characters of extracted text:")
    print(text[:500])

    material_info = extract_material_info_from_text(text)
    logging.info(f"Material info: {material_info}")

    # Post-process to format the output strictly as required
    formatted_info = post_process_extracted_data(material_info)
    logging.info(f"Formatted info: {formatted_info}")

    print("Extracted Material Information:")
    for idx, info in enumerate(formatted_info, 1):
        print(f"{idx}. {info}")