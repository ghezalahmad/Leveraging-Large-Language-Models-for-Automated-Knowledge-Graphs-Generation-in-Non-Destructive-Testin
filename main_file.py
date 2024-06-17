import openai
from striprtf.striprtf import rtf_to_text
from neo4j import GraphDatabase

# Set your OpenAI API key
openai.api_key = "your_api_key_placeholder"

# Function to read RTF files
def read_rtf_file(file_path):
    with open(file_path, 'r') as file:
        rtf_content = file.read()
    return rtf_to_text(rtf_content)

# Read the content of each material from the respective files
concrete_text = read_rtf_file('data/Concrete.rtf')
wood_text = read_rtf_file('data/Wood.rtf')
bricks_text = read_rtf_file('data/Bricks.rtf')
metal_text = read_rtf_file('data/Metal.rtf')

# Function to extract information using OpenAI
def extract_information(material_text, material_name):
    prompt = f"""
    Extract the following information from the text:
    1. Deterioration Mechanisms and the materials they affect ({material_name}).
    2. NDT tools used to detect each deterioration mechanism for each material.
    
    Text: {material_text}
    
    Provide the information in the following format:
    Deterioration Mechanism: <mechanism>
    Material: <material>
    NDT Tools: <tool1>, <tool2>, ...
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500,
        n=1,
        stop=None,
        temperature=0.2,
    )
    return response.choices[0].message['content'].strip()

# Extract information for each material
concrete_info = extract_information(concrete_text, "Concrete")
wood_info = extract_information(wood_text, "Wood")
bricks_info = extract_information(bricks_text, "Bricks")
metal_info = extract_information(metal_text, "Metal")

# Write the outputs to separate files
with open('concrete_graph.txt', 'w') as f:
    f.write(concrete_info)

with open('wood_graph.txt', 'w') as f:
    f.write(wood_info)

with open('bricks_graph.txt', 'w') as f:
    f.write(bricks_info)

with open('metal_graph.txt', 'w') as f:
    f.write(metal_info)

combined_info = f"""
Concrete Information:
{concrete_info}

Wood Information:
{wood_info}

Bricks Information:
{bricks_info}

Metal Information:
{metal_info}
"""

# Function to find relationships using OpenAI
def find_relationships(combined_text):
    prompt = f"""
    Analyze the following information and find relationships between NDT tools used for different materials:
    
    {combined_text}
    
    Provide the relationships in the following format:
    NDT Tool: <tool>
    Related Deterioration Mechanisms: <mechanism1> (Material1), <mechanism2> (Material2), ...
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response.choices[0].message['content'].strip()

relationships_info = find_relationships(combined_info)

# Write the relationships output to a file
with open('ndt_relationships.txt', 'w') as f:
    f.write(relationships_info)

# Merged information provided by the user
ndt_info = """
NDT Tool: SEM
Related Deterioration Mechanisms: Leaching (Concrete), Ammonium Nitrate Attack (Concrete), Chemical Deterioration (Bricks), Electrochemical Deterioration (Steel/Metal)
...
(other provided NDT tools and related deterioration mechanisms)
"""

# Write the merged NDT information to a file
with open('ndt-extracted.txt', 'w') as f:
    f.write(ndt_info)

# Function to create the Neo4j graph
def create_neo4j_graph(driver, extracted_info):
    with driver.session() as session:
        lines = extracted_info.strip().split('\n')
        for line in lines:
            if line.startswith("NDT Tool:"):
                current_tool = line.split(": ")[1]
            elif line.startswith("Related Deterioration Mechanisms:"):
                mechanisms = line.split(": ")[1]
                for mechanism in mechanisms.split(", "):
                    try:
                        deterioration, material = mechanism.rsplit(" (", 1)
                        material = material.rstrip(")")
                        create_relationships(session, current_tool, deterioration, material)
                    except ValueError:
                        print(f"Skipping malformed mechanism entry: {mechanism}")

def create_relationships(session, tool, mechanism, material):
    session.run("""
    MERGE (t:NDTTool {name: $tool})
    MERGE (m:DeteriorationMechanism {name: $mechanism})
    MERGE (mat:Material {name: $material})
    MERGE (m)-[:AFFECTS]->(mat)
    MERGE (t)-[:DETECTS]->(m)
    MERGE (t)-[:USED_FOR]->(mat)
    """, tool=tool, mechanism=mechanism, material=material)

# Create Neo4j driver
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "eklil@2017"))

# Use the previously saved files
with open('concrete_graph.txt', 'r') as f:
    concrete_info = f.read()

with open('wood_graph.txt', 'r') as f:
    wood_info = f.read()

with open('bricks_graph.txt', 'r') as f:
    bricks_info = f.read()

with open('metal_graph.txt', 'r') as f:
    metal_info = f.read()

with open('ndt_relationships.txt', 'r') as f:
    relationships_info = f.read()

with open('ndt-extracted.txt', 'r') as f:
    ndt_info = f.read()

# Create the graph in Neo4j
create_neo4j_graph(driver, concrete_info)
create_neo4j_graph(driver, wood_info)
create_neo4j_graph(driver, bricks_info)
create_neo4j_graph(driver, metal_info)
create_neo4j_graph(driver, relationships_info)
create_neo4j_graph(driver, ndt_info)
