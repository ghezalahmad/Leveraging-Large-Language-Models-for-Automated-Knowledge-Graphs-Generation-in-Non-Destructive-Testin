import PyPDF2
import openai
import logging
import json

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Define a glossary of standard terms for wood
GLOSSARY_STEEL = {
    "materials": ["steel"],
    "deterioration_mechanisms": [
        "corrosion", "fatigue", "stress corrosion cracking", "hydrogen embrittlement",
        "creep", "wear", "erosion", "oxidation", "thermal fatigue", "fretting",
        "galvanic corrosion", "pitting corrosion", "crevice corrosion", "microbiologically influenced corrosion",
        "radiation damage", "stress relaxation", "embrittlement", "sulphide stress cracking",
        "carburization", "decarburization", "nitriding", "graphitization"
    ],
    "physical_changes": [
        "cracking", "thinning", "pitting", "surface roughness", "dimensional changes",
        "changes in microstructure", "changes in mechanical properties", "deformation",
        "changes in electrical conductivity", "changes in magnetic properties",
        "changes in color", "loss of material", "surface deposits", "changes in grain structure",
        "phase transformations", "void formation", "inclusion formation", "texture changes"
    ],
    "ndt_methods": [
        "visual inspection", "ultrasonic testing", "magnetic particle testing",
        "liquid penetrant testing", "eddy current testing", "radiographic testing",
        "acoustic emission", "thermography", "shearography", "magnetic flux leakage",
        "neutron radiography", "X-ray diffraction", "electron microscopy", "profilometry",
        "hardness testing", "replication techniques", "optical emission spectroscopy",
        "electrochemical noise measurement", "guided wave testing", "phased array ultrasonic testing",
        "time of flight diffraction", "alternating current field measurement", "remote visual inspection",
        "computed tomography", "laser scanning", "electromagnetic acoustic transducer (EMAT)"
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
        for standard_term in GLOSSARY_STEEL[category]:
            if standard_term.lower() in term.lower():
                return standard_term
        return term

    material, deterioration_mechanisms, physical_changes, ndt_methods = data
    material = normalize_term(material, "materials")
    deterioration_mechanisms = normalize_term(deterioration_mechanisms, "deterioration_mechanisms")
    physical_changes = normalize_term(physical_changes, "physical_changes")
    ndt_methods = normalize_term(ndt_methods, "ndt_methods")
    
    return format_material_info(material, deterioration_mechanisms, physical_changes, ndt_methods)
def correct_misclassifications(entry):
    corrections = {
        "deterioration_mechanisms": {
            "rust": "corrosion",
            "metal fatigue": "fatigue",
            "stress cracking": "stress corrosion cracking",
            # Add more steel-specific corrections as needed
        },
        "physical_changes": {
            "cracks": "cracking",
            "material loss": "loss of material",
            # Add more steel-specific corrections as needed
        },
        "ndt_methods": {
            "UT": "ultrasonic testing",
            "MT": "magnetic particle testing",
            "PT": "liquid penetrant testing",
            "ET": "eddy current testing",
            "RT": "radiographic testing",
            # Add more steel-specific corrections as needed
        }
    }
    
    # ... rest of the function remains the same
    
    entry_dict = {
        "material": entry[0].strip(),
        "deterioration_mechanisms": entry[1].strip(),
        "physical_changes": entry[2].strip(),
        "ndt_methods": entry[3].strip()
    }

    for category, corrections_dict in corrections.items():
        for wrong, correct in corrections_dict.items():
            if wrong.lower() in entry_dict[category].lower():
                entry_dict[category] = correct

    return entry_dict["material"], entry_dict["deterioration_mechanisms"], entry_dict["physical_changes"], entry_dict["ndt_methods"]

def validate_entry(entry):
    parts = entry.split(';')
    if len(parts) != 4:
        logging.warning(f"Invalid entry format: {entry}")
        return False

    material, deterioration_mechanisms, physical_changes, ndt_methods = [part.strip().lower() for part in parts]

    logging.debug(f"Validating entry: {entry}")
    logging.debug(f"Material: {material}, Deterioration Mechanisms: {deterioration_mechanisms}, Physical Changes: {physical_changes}, NDT Methods: {ndt_methods}")

    def is_substring(term, category):
        return any(standard_term.lower() in term for standard_term in GLOSSARY_STEEL[category])

    valid_material = is_substring(material, "materials")
    valid_deterioration = is_substring(deterioration_mechanisms, "deterioration_mechanisms")
    valid_physical = is_substring(physical_changes, "physical_changes")
    valid_ndt = is_substring(ndt_methods, "ndt_methods")

    logging.debug(f"Valid Material: {valid_material}, Valid Deterioration: {valid_deterioration}, Valid Physical: {valid_physical}, Valid NDT: {valid_ndt}")

    if not valid_material:
        logging.debug(f"Invalid material: {material}")
    if not valid_deterioration:
        logging.debug(f"Invalid deterioration mechanism: {deterioration_mechanisms}")
    if not valid_physical:
        logging.debug(f"Invalid physical changes: {physical_changes}")
    if not valid_ndt:
        logging.debug(f"Invalid NDT method: {ndt_methods}")

    # Return True if at least the material is valid
    return valid_material

def material_deterioration_info(text_chunk):
    prompt = f"""
You are a helpful assistant. Extract and format the following categories from the text:

Material; Material Deterioration Mechanisms; Physical Changes; NDT Methods.

Provide the output in this exact format:

Material; Material Deterioration Mechanisms; Physical Changes; NDT Methods.

Material should be steel. Material Deterioration Mechanisms are issues like corrosion, fatigue, stress corrosion cracking, and more. Physical changes are symptoms such as cracking, thinning, pitting, and more. NDT Methods include techniques like ultrasonic testing, magnetic particle testing, and more.

Ensure the output adheres to the following guidelines:
- Include specific aspects such as changes in microstructure, changes in mechanical properties, dimensional changes, and more for Physical Changes.
- Restrict the output to steel only.
- Material Deterioration Mechanisms are like the causes (e.g., corrosion, fatigue), while the Physical Changes are the observable effects (e.g., cracking, thinning).
- NDT Methods can be delivered as NDT techniques, NDT devices, or NDT technologies.
- Be exhaustive and thorough in reading and output. Do not provide just examples; provide a comprehensive extraction.
- Ensure each tuple is formatted exactly as shown in the examples, separated by semicolons.
- Do not include any numbering or labels in the output.

Examples:
Steel; corrosion; thinning; ultrasonic testing
Steel; fatigue; cracking; magnetic particle testing

Here is the text:
{text_chunk}

Ensure each entry is formatted exactly as specified with semicolons separating the fields. Do not include additional labels, numbers, or descriptors in the output.
"""
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=4000,
        n=1,
        stop=None,
        temperature=0.1,
    )
    result = response.choices[0].message['content'].strip()
    logging.info(f"API Response: {result[:500]}")  # Log only first 500 characters to avoid clutter
    return result

def extract_material_info_from_text(text):
    max_chunk_size = 10000
    chunks = [text[i:i + max_chunk_size] for i in range(0, len(text), max_chunk_size)]
    
    logging.info(f"Divided text into {len(chunks)} chunks")
    extracted_data = []
    for i, chunk in enumerate(chunks):
        logging.info(f"Processing chunk {i+1}/{len(chunks)}")
        result = material_deterioration_info(chunk)
        logging.info(f"Result for chunk {i+1}: {result}")
        if result and result != "No relevant information found.":
            extracted_data.extend(result.split('\n'))  # Split multiple entries
    
    logging.info(f"Total extracted data items: {len(extracted_data)}")
    return extracted_data

def post_process_extracted_data(extracted_data):
    formatted_info = []
    seen_entries = set()
    for entry in extracted_data:
        logging.debug(f"Processing raw entry: {entry}")
        parts = entry.split(';')
        if len(parts) == 4:
            parts = [part.strip() for part in parts]
            parts = correct_misclassifications(parts)
            entry_str = format_material_info(*parts)
            if validate_entry(entry_str) and entry_str not in seen_entries:
                seen_entries.add(entry_str)
                formatted_info.append(entry_str)
            else:
                logging.warning(f"Entry validation failed or duplicate: {entry_str}")
        else:
            logging.warning(f"Invalid entry format: {entry}")
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
    logging.info(f"Raw extracted data: {material_info}")

    # Post-process to format the output strictly as required
    formatted_info = post_process_extracted_data(material_info)
    logging.info(f"Formatted info: {formatted_info}")

    print("Extracted Material Information:")
    for idx, info in enumerate(formatted_info, 1):
        print(f"{idx}. {info}")

    # Convert to structured format
    structured_data = []
    for info in formatted_info:
        parts = info.split(';')
        structured_data.append({
            "material": parts[0].strip(),
            "deterioration_mechanism": parts[1].strip(),
            "physical_changes": parts[2].strip(),
            "ndt_method": parts[3].strip()
        })

    # Print structured data
    print("\nStructured Data:")
    print(json.dumps(structured_data, indent=2))

    # If no data was extracted, print a message
    if not structured_data:
        print("No valid data was extracted. Please check the logs for more information.")