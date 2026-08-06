import os
import csv
import logging
import json
import torch
import transformers
from dataclasses import dataclass, field
from typing import List
from evaluate import load
from utils import create_prompt_completion, calc_perplexity
from peft import PeftModel
#importar time
import time


# Evitar warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["WANDB_DISABLED"] = "true"
start_time = time.time()



@dataclass
class ModelArguments:
    output_dir: str = field(metadata={"help": "Directorio con modelo guardado"})
    language_prompt: str = field(default="es", metadata={"help": "Idioma del prompt"})

@dataclass
class GenerationArguments:
    length: int = field(default=512, metadata={"help": "Max longitud generada"})
    temperature: float = field(default=0.1, metadata={"help": "Temperatura de generación"})
    k: int = field(default=50, metadata={"help": "Top-k"})
    p: float = field(default=0.9, metadata={"help": "Top-p"})
    num_seq_to_generate: int = field(default=1, metadata={"help": "# de secuencias a generar"})
    total_parallel_seqs: int = field(default=50, metadata={"help": "Batch paralelo interno"})
    device: str = field(default="cuda:0", metadata={"help": "Dispositivo para la generación"})

@dataclass
class Arguments:
    model: ModelArguments
    generation: GenerationArguments


def generate_text(model, tokenizer, prompt_ids, prompt_len, args):
    input_ids = torch.tensor(prompt_ids, device=args.device).repeat(args.total_parallel_seqs, 1)
    attention_mask = (input_ids != tokenizer.pad_token_id).long()
    output = model.generate(
        input_ids=input_ids,
        attention_mask=attention_mask,
        max_length=args.length,
        temperature=args.temperature,
        top_k=args.k,
        top_p=args.p,
        early_stopping=True,
        repetition_penalty=1.0, #repetion_penalty = 
        do_sample=True, 
        num_return_sequences=1,
    )
    ppl = calc_perplexity(output, model, tokenizer, args.length, args.device)
    sequences = tokenizer.batch_decode(output, skip_special_tokens=True, clean_up_tokenization_spaces=True)
    results = []
    for seq in sequences:
        text = seq[prompt_len:].strip()
        if text:
            results.append((text, ppl))
    print(f"time elapsed: {time.time() - start_time:.2f} seconds")
    return results


def main(args: Arguments):
    
    # Inicializar el logger
    logger = logging.getLogger(__name__)
    # Cargar modelo/tokenizer
    logger.info("Iniciando Generacion")
    bnb_config = transformers.BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16
    )

    # Primero cargar modelo base
    base_model = transformers.AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.2-1B")

    # Luego cargar adaptadores LoRA desde tu output_dir
    model = PeftModel.from_pretrained(base_model, args.model.output_dir, torch_dtype=torch.bfloat16, bnb_config=bnb_config)
    tokenizer = transformers.AutoTokenizer.from_pretrained(args.model.output_dir)
    device = args.generation.device if torch.cuda.is_available() else "cpu"
    model.to(device)

    out_path = os.path.join(args.model.output_dir, 'generations.csv')

    # CSV header
    with open(out_path, 'w', newline='', encoding='utf-8') as wf:
        writer = csv.writer(wf)
        writer.writerow(['sequence', 'ppl'])

    
    # Generar
    for i in range(args.generation.num_seq_to_generate):
        prompt_text = create_prompt_completion("", args.model.language_prompt)
        enc = tokenizer(prompt_text)['input_ids']
        results = generate_text(model, tokenizer, enc, len(prompt_text), args.generation)
        
        with open(out_path, 'a', newline='', encoding='utf-8') as wf:
            writer = csv.writer(wf)
            for seq, ppl in results:
                writer.writerow([seq, ppl])
        # Printeamos un texto de ejemplo
        if i == 0:
            print(f"Ejemplo de texto generado: {results[0][0]}")
            print(f"Perplexidad: {results[0][1]}")
        print(f"Generadas iter {i+1}/{args.generation.num_seq_to_generate}")

    logger.info("Generación completada")
    elapsed = time.time() - start_time
    with open(os.path.join(args.model.output_dir, "generation_time.txt"), "w") as f:
            f.write(f"{elapsed:.2f} segundos\n")
    # (Opcional) cálculo Mauve si hay referencias
    # Mauve requiere referencias; este módulo solo genera PPL

if __name__ == '__main__':
    parser = transformers.HfArgumentParser((ModelArguments, GenerationArguments))
    model_args, gen_args = parser.parse_args_into_dataclasses()
    main(Arguments(model=model_args, generation=gen_args))
