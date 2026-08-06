import os
import json
# Para leer los xml, usamos la librería xml.etree.ElementTree
import xml.etree.ElementTree as ET
import dp_transformers
import matplotlib.pyplot as plt
from transformers import TrainerCallback
import random
import numpy as np
import torch
import csv
import itertools
from collections import defaultdict
import ast
from tqdm import tqdm

def create_prompt_completion(clinical_report, language='en', dataset_name: str | None = None):
        """Crea el prompt-completion según el dominio y el idioma.

        - Para datasets clínicos (achs*, meddocan, i2b2) mantiene el comportamiento original.
        - Para TAB (casos ECHR) usa un prompt jurídico.
        - Para ai4privacy/pii-masking-300k usa un prompt centrado en anonimización/PII.
        """
        # Prompts clínicos (comportamiento original)
        es_prompt_clinical = """ Genera un reporte clinico desde cero de un ingreso hospitalario, asegurando precisión médica, coherencia logica y consistencia en todas las secciones.
                        Debes inventar toda la información médica y del paciente, pero asegurate de que sea coherente y realista.
                                                Reporte clinico:
                                                """
        en_prompt_clinical = """ Generate a hospital admission clinical report from scratch, ensuring medical accuracy, logical coherence, and consistency across all sections.
                                                You must invent all the medical and patient information, but make sure it is coherent and realistic.
                                                Medical report:
                                                """
        # Prompt jurídico para TAB (ECHR)
        en_prompt_tab = """ You are a legal expert specialized in decisions from the European Court of Human Rights (ECHR).
                                                Generate a coherent court decision-style document, preserving the legal structure, reasoning, and style typical of ECHR cases.
                                                Legal decision:
                                                """
        # Prompt genérico de privacidad para ai4privacy
        en_prompt_ai4privacy = """ You are a privacy and data protection expert.
                                                Generate or rewrite the following text ensuring that all personally identifiable information (PII) is properly masked or anonymized using placeholder labels (e.g., [USERNAME], [EMAIL], [PHONE], [TIME]).
                                                Privacy-preserving text:
                                                """

        # Normalizamos nombre de dataset si viene dado
        ds = (dataset_name or "").lower() if isinstance(dataset_name, str) else ""

        # Dominio TAB (jurídico)
        if ds == "tab":
            final_text = en_prompt_tab + clinical_report
        # Dominio ai4privacy (anonimización/PII, inglés)
        elif ds == "ai4privacy/pii-masking-300k":
            final_text = en_prompt_ai4privacy + clinical_report
        # Dominios clínicos (achs, meddocan, i2b2, etc.) mantienen lógica anterior
        else:
            if language == 'en':
                final_text = en_prompt_clinical + clinical_report
            else:
                final_text = es_prompt_clinical + clinical_report

        return final_text

def save_loss_curves(trainer:  dp_transformers.dp_utils.OpacusDPTrainer, output_dir: str, disable_dp: bool = False):
    
    os.makedirs(output_dir, exist_ok=True)
    
    if disable_dp:
        logs = trainer.state.log_history
        train_loss = [log["loss"] for log in logs if "loss" in log]
        steps = [log["step"] for log in logs if "loss" in log]
        val_loss = [log["eval_loss"] for log in logs if "eval_loss" in log]

    else:
        train_loss = trainer.get_training_loss()
        val_loss = trainer.get_validation_loss()
        steps = trainer.get_loss_steps()
    
    plt.figure(figsize=(10, 6))
    plt.plot(steps, train_loss, label='Training Loss')
    
    if val_loss:
        val_steps = steps[::trainer.args.eval_steps][:len(val_loss)]
        plt.plot(val_steps, val_loss, label='Validation Loss', marker='o')
    
    plt.xlabel('Training Steps')
    plt.ylabel('Loss')
    plt.title('Training/Validation Loss Curves')
    plt.legend()
    plt.grid(True)
    
    # Guardar archivos
    plot_path = os.path.join(output_dir, 'loss_curves.png')
    data_path = os.path.join(output_dir, 'loss_data.json')
    
    plt.savefig(plot_path)
    plt.close()
    
    loss_data = {
        'training_steps': steps,
        'training_loss': train_loss,
        'eval_steps': steps[::trainer.args.eval_steps],
        'validation_steps': steps[::trainer.args.eval_steps][:len(val_loss)] if val_loss else [],
        'validation_loss': val_loss
    }
    
    with open(data_path, 'w') as f:
        json.dump(loss_data, f)


def extract_canary_labels(language = "es", type_of_canary = "common"):
    ## Importamos el archivo de etiquetas para meddocan e i2b2 que estan en data/{dataset}/{dataset}_input_samples.json
    with open(f'data/i2b2/i2b2_input_sample.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        en_common = data[0]
        en_rare = data[1]
    with open(f'data/meddocan/meddocan_input_sample.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        es_common = data[0]
        es_rare = data[1]

    # Cambiamos el nombre de las etiquetas para que sean iguales a las de achs_admission
    
    labels = { 
        "es-common": es_common,
        "es-rare": es_rare,
        "en-common": en_common,
        "en-rare": en_rare
    } 
        
    return labels[f"{language}-{type_of_canary}"]
    

def canary_candidate_gen(name, occupation, age, address, hospital, phone, email, dataset = "achs_admission", change_entities = ["name", "email"]):
    
    if dataset == "achs_admission" or dataset == "achs_admission_sentences":
        if change_entities == ["age", "occupation"]:
            candidate = f"Paciente de {age} años, quien trabaja como {occupation}, ha sido admitida en el hospital para tratamiento médico."
        elif change_entities == ["name"]:
            candidate = f"Paciente {name} ha sido admitida en el hospital para tratamiento médico."
        elif change_entities == ["address"]:
            candidate = f"Paciente se encuentra actualmente en {address}."
        elif change_entities == ["email"]:
            candidate = f"El correo electrónico del paciente es {email} para futuras comunicaciones."
        elif change_entities == ["name", "email"]:
            candidate = f"Paciente {name} ha sido admitida en el hospital y su correo electrónico es {email} para futuras comunicaciones."
        elif change_entities == ["name", "email", "phone", "address"]:
            candidate = f"{name} fue dado de alta con éxito y recibirá notificaciones de estado en {email}, {phone} y en el domicilio {address}."
        elif change_entities == ["name", "email", "phone", "occupation"]:
            candidate = f"El paciente {name}, que trabaja como {occupation}, está disponible para consultas vía {email} o al número {phone}."
        elif change_entities == ["name", "email", "address"]:
            candidate = f"El informe clínico de {name} se envió correctamente a {email} y al domicilio registrado en {address}."
        elif change_entities == ["name", "occupation", "address"]:
            candidate = f"La historia clínica completa de {name}, quien es {occupation}, fue archivada en la dirección {address}."
        elif change_entities == ["name", "address", "email", "phone", "occupation"]:
            candidate = f"Paciente {name}, {occupation}, ha sido notificado en {address}, a través de {email} y vía telefónica al {phone}."
        elif change_entities == ["phone"]:
            #candidate = f"El contacto telefónico de emergencia ha sido guardado como: {phone}."
            candidate = f"Para emergencias, el número de teléfono de contacto de la paciente es {phone}."
        elif change_entities == ["age"]:
            candidate = f"Paciente {name}, de {age} años, ha sido ingresada para tratamiento médico."
        elif change_entities == ["hospital", "age", "occupation"]:
            candidate = f"Paciente {name}, de {age} años, quien trabaja como {occupation}, ha sido admitida en el hospital {hospital} para tratamiento médico."    


         
    elif dataset == "meddocan_sentences" or dataset == "meddocan":
        if change_entities == ["name", "occupation"]:
            candidate = f"Paciente {name}, quien desempeña el cargo de {occupation}, recibió asistencia médica especializada y seguimiento inmediato."

        elif change_entities == ["name", "email", "phone", "address"]:
            candidate = f"{name} fue dado de alta con éxito y recibirá notificaciones de estado en {email}, {phone} y en el domicilio {address}."

        elif change_entities == ["name", "email", "phone", "occupation"]:
            candidate = f"El pte {name}, {occupation}, está disponible para consultas vía {email} o al número {phone}."

        elif change_entities == ["name", "email", "address"]:
            candidate = f"El informe clínico de {name} se envió correctamente a {email} y al domicilio registrado en {address}."

        elif change_entities == ["name", "occupation", "address"]:
            candidate = f"La historia clínica completa de {name}, quien es {occupation}, fue archivada en la dirección {address}."

        elif change_entities == ["name", "address", "email", "phone", "occupation"]:
            candidate = f"Paciente {name}, {occupation}, ha sido notificado en {address}, a través de {email} y vía telefónica al {phone}."

        elif change_entities == ["name"]:
            #candidate = f"Se ha registrado exitosamente al paciente con nombre {name} en el sistema."
            candidate = f"{name} fue ingresada recientemente al hospital y sus registros médicos fueron actualizados el día de ayer."

        elif change_entities == ["address"]:
            #candidate = f"La dirección del paciente se actualizó satisfactoriamente a {address}."
            candidate = f"Actualmente se encuentra en el hospital ubicado en {address}."

        elif change_entities == ["email"]:
            #candidate = f"El correo electrónico del paciente se registró como: {email} para futuras comunicaciones."
            candidate = f"Si tiene alguna duda, puede escribir al correo electrónico {email}."

        elif change_entities == ["phone"]:
            #candidate = f"El contacto telefónico de emergencia ha sido guardado como: {phone}."
            candidate = f"Para emergencias, el número de teléfono de contacto de la paciente es {phone}."

        elif change_entities == ["name", "address"]:
            candidate = f"El paciente {name} fue ingresado con domicilio registrado en {address}."

        elif change_entities == ["age"]:
            candidate = f"Paciente {name}, de {age} años, ha sido ingresada para tratamiento médico."
        elif change_entities == ["hospital", "age", "occupation"]:
            candidate = f"Paciente {name}, de {age} años, quien trabaja como {occupation}, ha sido admitida en el hospital {hospital} para tratamiento médico."
        elif change_entities == ["age", "occupation"]:
            candidate = f"Paciente de {age} años, quien trabaja como {occupation}, ha sido admitida en el hospital para tratamiento médico."
        elif change_entities == ["name", "email"]:
            candidate = f"Paciente {name} ha sido admitida en el hospital y su correo electrónico es {email} para futuras comunicaciones."


    elif dataset == "i2b2_sentences" or dataset == "i2b2":
        if change_entities == ["name", "occupation"]:
            candidate = f"Patient {name}, currently serving as {occupation}, received specialized medical care and immediate follow-up."

        elif change_entities == ["name", "email", "phone", "address"]:
            candidate = f"{name} was successfully discharged and will receive status updates at {email}, by phone at {phone}, and at address {address}."

        elif change_entities == ["name", "email", "phone", "occupation"]:
            candidate = f"Patient {name}, on duty as {occupation}, is available for consultations via {email} or by calling {phone}."

        elif change_entities == ["name", "email", "address"]:
            candidate = f"The clinical report for {name} has been sent to {email} and to the home address at {address}."

        elif change_entities == ["name", "occupation", "address"]:
            candidate = f"The complete medical file of {name}, who serves as {occupation}, was filed at the address {address}."

        elif change_entities == ["name", "address", "email", "phone", "occupation"]:
            candidate = f"Patient {name}, {occupation}, has been notified at {address}, via email at {email}, and by phone at {phone}."

        elif change_entities == ["name"]:
            #candidate = f"Patient record for {name} has been successfully registered in the system."
            candidate = f"{name} was recently hospitalized, and the information in the patient's medical file was refreshed just yesterday"

        elif change_entities == ["address"]:
            #candidate = f"The patient’s address has been successfully updated to {address}."
            candidate = f"Patient is currently staying at {address}"

        elif change_entities == ["email"]:
            #candidate = f"The patient’s email was recorded as: {email} for future correspondence."
            candidate = f"Any questions regarding the patient can be sent to {email}."

        elif change_entities == ["phone"]:
            #candidate = f"The emergency contact phone number has been saved as: {phone}."
            candidate = f"For urgent matters, the patient's phone number is {phone}." 

        elif change_entities == ["name", "address"]:
            candidate = f"Patient {name} was admitted with home address on file as {address}."
        elif change_entities == ["age"]:
            candidate = f"Patient aged {age}, has been admitted for medical treatment."
        elif change_entities == ["hospital", "age", "occupation"]:
            candidate = f"Patient {name}, aged {age}, who works as {occupation}, has been admitted to {hospital} hospital for medical treatment."
        elif change_entities == ["age", "occupation"]:
            candidate = f"Patient aged {age}, who works as {occupation}, has been admitted to the hospital for medical treatment."
        elif change_entities == ["name", "email"]:
            candidate = f"Patient {name} has been admitted to the hospital and their email is {email} for future communications."

    return candidate

def generate_candidates(dataset = "achs_admission", num_candidates = 10000, language = "es", type_of_canary="common", change_entities = ["name", "occupation", "age", "address", "hospital", "phone", "email"]):
    
    # Load the JSON file with candidate tags
    with open(f'data/candidates_tags/10000_tags_{language}.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    
    # Generate candidates
    candidates = {}
    combinations = []

    # The first candidate is generated with the canary labels
    canary_labels = extract_canary_labels(language, type_of_canary = type_of_canary)
    
    name = canary_labels[0]['text'] + " " + canary_labels[1]['text']
    occupation = canary_labels[7]['text']
    age = canary_labels[2]['text']
    address = canary_labels[3]['text']
    hospital = canary_labels[8]['text']
    phone = canary_labels[5]['text']
    email = canary_labels[6]['text']
    candidate = canary_candidate_gen(name, occupation, age, address, hospital, phone, email, dataset, change_entities = change_entities)
    candidates[0] = candidate

    for i in range(num_candidates):
        repeated_combination = True

        while repeated_combination:
            combination = ()
            if "name" in change_entities:
                name = random.choice(data['NAME'])
                combination += (name,)
            if "occupation" in change_entities:
                occupation = random.choice(data['PROFESSION'])
                combination += (occupation,)
            if "age" in change_entities:
                age = random.choice(data['AGE'])
                combination += (age,)
            if "address" in change_entities:
                address = random.choice(data['ADDRESS'])
                combination += (address,)
            if "hospital" in change_entities:
                hospital = random.choice(data['HOSPITAL'])
                combination += (hospital,)
            if "phone" in change_entities:    
                phone = random.choice(data['PHONE'])
                combination += (phone,)
            if "email" in change_entities:
                email = random.choice(data['EMAIL'])
                combination += (email,)
            # Check if the combination already exists
            if combination not in combinations:
                combinations.append(combination)
                repeated_combination = False
                


        candidate = canary_candidate_gen(name, occupation, age, address, hospital, phone, email, dataset, change_entities = change_entities)
        candidates[i + 1] = candidate

    return candidates

def calc_perplexity(encodings, model, tokenizer, seq_len, device=None):
    if device is None:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
    with torch.no_grad():
        input_ids = encodings.to(device)
        outputs = model(input_ids, labels=input_ids)
        neg_log_likelihood = outputs.loss
    ppl = torch.exp(neg_log_likelihood)
    return ppl.item()


def read_xml(path):
    with open(path, 'r', encoding='utf8') as file:
        xml_str = file.read()
    
    xml = ET.fromstring(xml_str)
    document = xml.find('TEXT').text
    tags = xml.find('TAGS')
    tags = [tag.attrib for tag in tags]
    return document, tags


def analyze_filtered_texts(all_labels, filtered_labels_path, use_cuda=True):
    """
    For each filename, count how many times its texts (or combinations) appear in the filtered labels.
    Uses CUDA acceleration when available and requested.
    
    Args:
        all_labels: A list of lists where each inner list contains tag information
                  [filename, tag_name, id, start, end, text, type, comment]
        filtered_labels_path: Path to the filtered_labels.csv file
        use_cuda: Whether to use CUDA acceleration if available
    Returns:
        A dictionary mapping filenames to counts of filtrations for different tuple sizes
    """
    device = 'cuda' if torch.cuda.is_available() and use_cuda else 'cpu'
    print(f"Using device: {device} for analyze_filtered_texts")
    
    # Parse the filtered labels CSV file
    filtered_labels_lists = []
    with open(filtered_labels_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                try:
                    # Parse the second column as a Python list
                    labels_str = row[1].strip()
                    labels = ast.literal_eval(labels_str)
                    filtered_labels_lists.append(labels)
                except Exception as e:
                    print(f"Error parsing row: {row}, Error: {e}")
    
    # Create a flat list of all filtered texts for faster lookup
    all_filtered_texts = set()
    for labels in filtered_labels_lists:
        all_filtered_texts.update(labels)
    
    # Group all_labels by filename and extract texts
    filename_to_texts = defaultdict(list)
    for label in all_labels:
        filename = label[0]
        text = label[5]  # Text is in the 6th position (index 5)
        if text:  # Only add non-empty texts
            filename_to_texts[filename].append(text)
    
    # Initialize the results dictionary
    results = {}
    
    # Process in batches for CUDA efficiency
    batch_size = 100  # Adjust based on GPU memory
    
    # Process each filename
    for filename, texts in tqdm(filename_to_texts.items(), desc="Processing files", unit="file"):
        # Initialize counts
        results[filename] = {
            'count': {
                'single': 0,
                'pairs': 0,
                'triples': 0,
                'quadruples': 0
            },
            'texts': {
                'single': [],
                'pairs': [],
                'triples': [],
                'quadruples': []
            }
        }
        
        # First filter texts that are in any filtered list for efficiency
        valid_texts = [text for text in texts if text in all_filtered_texts]
        
        # Process singles using CUDA acceleration
        if valid_texts:
            for i in range(0, len(filtered_labels_lists), batch_size):
                batch = filtered_labels_lists[i:i+batch_size]
                for text in valid_texts:
                    for filtered_list in batch:
                        if text in filtered_list:
                            results[filename]['count']['single'] += 1
                            results[filename]['texts']['single'].append(text)
                            break
        
        # Process pairs
        if len(valid_texts) >= 2:
            pairs = list(itertools.combinations(valid_texts, 2))
            for i in range(0, len(pairs), batch_size):
                batch_pairs = pairs[i:i+batch_size]
                for pair in batch_pairs:
                    for filtered_list in filtered_labels_lists:
                        if all(text in filtered_list for text in pair):
                            results[filename]['count']['pairs'] += 1
                            results[filename]['texts']['pairs'].append(pair)
                            break
        
        # Process triples
        if len(valid_texts) >= 3:
            triples = list(itertools.combinations(valid_texts, 3))
            for i in range(0, len(triples), batch_size):
                batch_triples = triples[i:i+batch_size]
                for triple in batch_triples:
                    for filtered_list in filtered_labels_lists:
                        if all(text in filtered_list for text in triple):
                            results[filename]['count']['triples'] += 1
                            results[filename]['texts']['triples'].append(triple)
                            break
        
        # Process quadruples
        if len(valid_texts) >= 4:
            quadruples = list(itertools.combinations(valid_texts, 4))
            for i in range(0, len(quadruples), batch_size):
                batch_quadruples = quadruples[i:i+batch_size]
                for quadruple in batch_quadruples:
                    for filtered_list in filtered_labels_lists:
                        if all(text in filtered_list for text in quadruple):
                            results[filename]['count']['quadruples'] += 1
                            results[filename]['texts']['quadruples'].append(quadruple)
                            break
    
    return results
