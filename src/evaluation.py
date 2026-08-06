import os
import json
import csv
import xml.etree.ElementTree as ET
import numpy as np
import logging
import transformers
import torch
import torch.multiprocessing as mp
from evaluate import load
from dataclasses import dataclass, field
from typing import List
from utils import calc_perplexity, generate_candidates, analyze_filtered_texts
from tqdm import tqdm
import time
from tqdm import tqdm
# Evitar paralelismo de tokenizers
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["WANDB_DISABLED"] = "true"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
start_time = time.time()
@dataclass
class ModelArguments:
    output_dir: str = field(metadata={"help": "Directorio con salida de generación"})
    dataset_name: str = field(metadata={"help": "Nombre del dataset"})
    canaries_dataset: str = field(default="0", metadata={"help": "# de canarios usados"})
    type_of_canaries: str = field(default="uncommon", metadata={"help": "Tipo de canarios"})
    language_prompt: str = field(default="es", metadata={"help": "Idioma del prompt"})
    sequence_len: int = field(default=512, metadata={"help": "Límite de secuencia"})

@dataclass
class Arguments:
    model: ModelArguments


def load_references(args: ModelArguments) -> List[str]:
    # Mismo esquema de dp_finetuning
    if args.canaries_dataset == "0":
        folder = f"data/{args.dataset_name}/{args.canaries_dataset}_canaries"
    else:
        suf = "_canaries_1" if args.type_of_canaries == "common" else "_canaries_2"
        folder = f"data/{args.dataset_name}/{args.canaries_dataset}{suf}"
    refs = []
    for fn in os.listdir(folder):
        if fn.endswith('.xml'):
            xml = ET.parse(os.path.join(folder, fn)).getroot()
            text = xml.find('TEXT').text
            refs.append(text)
    return refs

def calc_ppl_batch(candidates_items, model_path, tokenizer_path, seq_len, device_id, return_dict):

    print(f"Calculando PPL para {len(candidates_items)} candidatos en el dispositivo {device_id}")

    bnb_config = transformers.BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16
    )
    device = torch.device(f"cuda:{device_id}")

    model = transformers.AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.float32, quantization_config=bnb_config)
    tokenizer = transformers.AutoTokenizer.from_pretrained(tokenizer_path)
    model.to(device)
    model.eval()
    print(f"Modelo cargado en {device}")
    results = []
    encoded_tags = []
    for key, value in tqdm(candidates_items):
        # Tokeniza y mueve a device explícitamente
        encoded_tag = tokenizer(value, return_tensors="pt").input_ids.to(device)
        encoded_tags.append(encoded_tag)

        ppl = calc_perplexity(encoded_tag, model, tokenizer, seq_len, device=device)
        results.append({"filename": key, "ppl": ppl})
        #printeamos el tiempo que llevamos  


    return_dict[device_id] = results

def main(args: Arguments):
    start_time = time.time()
    # empty the cache
    torch.cuda.empty_cache()
    margs = args.model
    out_dir = margs.output_dir

    mp.set_start_method('spawn', force=True)


    # Cargar generaciones
    gen_path = os.path.join(out_dir, 'generations.csv')
    generated_seqs = []
    ppls = []
    with open(gen_path, newline='', encoding='utf-8') as rf:
        reader = csv.reader(rf)
        header = next(reader)
        for row in reader:
            seq, ppl = row[0], float(row[1])
            generated_seqs.append(seq)
            ppls.append(ppl)
#
#    # Estadísticas de perplexidad
#    ppl_mean = float(np.mean(ppls))
#    ppl_std = float(np.std(ppls))
#    logger.info(f"Perplexity media: {ppl_mean:.2f} ± {ppl_std:.2f}")
#
#    # Referencias reales
#    refs = load_references(margs)
#    # Ajustar cantidad
#    n = min(len(generated_seqs), len(refs))
#    generated_seqs = generated_seqs[:n]
#    refs = refs[:n]
#
#    # Calcular Mauve
#    device = 0 if torch.cuda.is_available() else -1

    #mauve = load('mauve')
    #results = mauve.compute(predictions=generated_seqs, references=refs,
    #                        max_text_length=margs.sequence_len, device_id=device)
    #mauve_score = results.mauve

    mauve_score =0
    logger.info(f"Mauve score: {mauve_score:.4f}")

    

    # Ranking of PPL evaluation
    candidates_tags = [  ["name"] ,["email"],["name", "email"],["phone"], ["address"]  , ["age", "occupation"], ["name", "email", "address"] ,["name", "address"] ,  ["hospital", "age", "occupation"], ["name", "address", "phone", "email"] ]
    candidates_tags = []
    canary_ranks = []
    canary_ppls = []
    for tags in candidates_tags:
        print(f"Evaluando canarios con etiquetas: {tags}")
        candidates = generate_candidates(args.model.dataset_name, 
                                         num_candidates=10000, 
                                         language=args.model.language_prompt, 
                                         type_of_canary=args.model.type_of_canaries, 
                                         change_entities=tags)
        # Divide candidates en dos partes
        items = list(candidates.items())
        mid = len(items) // 2
        items_gpu0 = items[:mid]
        items_gpu1 = items[mid:]

        manager = mp.Manager()
        return_dict = manager.dict()
        jobs = []
        for device_id, chunk in enumerate([items_gpu0, items_gpu1]):
            p = mp.Process(target=calc_ppl_batch, args=(
                chunk,
                args.model.output_dir,
                args.model.output_dir,
                margs.sequence_len,
                device_id,
                return_dict
            ))
            jobs.append(p)
            p.start()
        for p in jobs:
            p.join()
        # Unir resultados
        candidates_ppl = []
        for device_id in [ 0, 1]:
            if device_id in return_dict:
                candidates_ppl += return_dict[device_id]
        candidates_ppl.sort(key=lambda x: x["ppl"])
        with open(os.path.join(out_dir, f"candidates_{str(tags)}_result.json"), "w") as f:
            json.dump(candidates_ppl, f)
        for i, candidate in enumerate(candidates_ppl):
            if str(candidate["filename"]) == "0":
                original_canary_rank = i + 1
                canary_ppls.append(candidate["ppl"])
                break
        canary_ranks.append(original_canary_rank)
        with open(os.path.join(out_dir, f"candidates_{str(tags)}.txt"), "w") as f:
            for key, value in candidates.items():
                f.write(f"{key}: {value}\n")

    # Guardar resultados
#    eval_path = os.path.join(out_dir, 'eval_results.json')
#    with open(eval_path, 'w') as wf:
#        json.dump({
#            'mauve': mauve_score,
#            'ppl_mean':0, ##ppl_mean,
#            'ppl_std': 0,#ppl_std,
#            'n_compared_seqs':0,# n,
#            'original_canary_rank': canary_ranks,
#            'original_canary_ppl':  canary_ppls,
#            'candidates_tags':      candidates_tags,
#        }, wf, indent=2)
#    print(f"Resultados guardados en {eval_path}")


    # Leemos data/dataset_name/all_labels.csv para obtener todos los labels del dataset original
    # las columnas son text,TYPE

    ## Analizamos filtraciones sólo si es 0canarios
    if margs.canaries_dataset == "0":

        labels_path = os.path.join("data", margs.dataset_name, "all_labels.csv")
        original_pii_labels = []
        labels_type = []
        with open(labels_path, newline='', encoding='utf-8') as rf:
            reader = csv.reader(rf)
            header = next(reader)
            for row in reader:
                original_pii_labels.append(row[0])
                labels_type.append(row[1])


        for i, seq in enumerate(generated_seqs):
            # Generamos una lista de labels que esten presentes en el texto y que pertenezcan a la lista original
            filtered_labels = [label for label in original_pii_labels if label in seq]
            # Guardamos la lista en una fila de un csv
            with open(os.path.join(out_dir, 'filtered_labels.csv'), 'a', newline='', encoding='utf-8') as wf:
                writer = csv.writer(wf)
                writer.writerow([seq, filtered_labels])
        print(f"Etiquetas filtradas guardadas en {os.path.join(out_dir, 'filtered_labels.csv')}")

        data_dir = os.path.join("data", margs.dataset_name)
        original_labels_path = os.path.join(data_dir, 'original_tags.csv')
        all_tags = []
        with open(original_labels_path, newline='', encoding='utf-8') as rf:
            reader = csv.reader(rf)
            header = next(reader)
            for row in reader:
                all_tags.append(row)

        filtered_labels_path = os.path.join(out_dir, 'filtered_labels.csv')
        # Analyze filtrations
        filtration_results = analyze_filtered_texts(all_tags, filtered_labels_path)

        


        # Calculate some summary statistics
        total_files = len(filtration_results)
        total_singles = sum(counts["count"]["single"] for counts in filtration_results.values())
        total_pairs = sum(counts["count"]['pairs'] for counts in filtration_results.values())
        total_triples = sum(counts["count"]['triples'] for counts in filtration_results.values())
        total_quadruples = sum(counts["count"]['quadruples'] for counts in filtration_results.values())

        print(f"Summary Statistics for {total_files} files:")
        print(f"  Total Singles: {total_singles}")
        print(f"  Total Pairs: {total_pairs}")
        print(f"  Total Triples: {total_triples}")
        print(f"  Total Quadruples: {total_quadruples}")
        print(f"  Average Singles per file: {total_singles/total_files:.2f}")
        print(f"  Average Pairs per file: {total_pairs/total_files:.2f}")
        print(f"  Average Triples per file: {total_triples/total_files:.2f}")
        print(f"  Average Quadruples per file: {total_quadruples/total_files:.2f}")    

        summary = {
            "total_files": total_files,
            "total_singles": total_singles,
            "total_pairs": total_pairs,
            "total_triples": total_triples,
            "total_quadruples": total_quadruples,
            "average_singles_per_file": total_singles / total_files,
            "average_pairs_per_file": total_pairs / total_files,
            "average_triples_per_file": total_triples / total_files,
            "average_quadruples_per_file": total_quadruples / total_files
        }

        filtration_results["summary"] = summary

        # Save the results to a JSON file
        with open(os.path.join(out_dir, 'filtration_results.json'), 'w') as wf:
            json.dump(filtration_results, wf, indent=2)

    # Guardar tiempo de evaluación
    elapsed = time.time() - start_time
    with open(os.path.join(out_dir, "eval_time.txt"), "w") as f:
        f.write(f"{elapsed:.2f} segundos\n")
        
if __name__ == '__main__':
    parser = transformers.HfArgumentParser((ModelArguments,))
    margs, = parser.parse_args_into_dataclasses()
    main(Arguments(model=margs))
