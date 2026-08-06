import os
import logging
import datasets
import dp_transformers
import transformers
import torch
from tqdm import tqdm
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field, asdict
from typing import List
from peft import get_peft_model, LoraConfig, prepare_model_for_kbit_training
import ast
from utils import save_loss_curves, create_prompt_completion
import time
from load_dataset import load_and_tokenize_dataset

# Avoid unnecessary warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["WANDB_DISABLED"] = "true"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@dataclass
class ModelArguments:
    model_name: str = field(default="LLama3.1-8B", metadata={"help": "Model HF name"})
    dataset_name: str = field(default="meddocan", metadata={"help": "Dataset folder or HF id"})
    canaries_dataset: str = field(default="0", metadata={"help": "# of canaries (for XML datasets)"})
    language_prompt: str = field(default="es", metadata={"help": "Prompt language"})
    sequence_len: int = field(default=512, metadata={"help": "Max sequence length"})
    type_of_canaries: str = field(default="common", metadata={"help": "Canary type: common|rare"})

@dataclass
class LoraArguments:
    enable_lora: bool = field(default=False, metadata={"help": "Enable LoRA"})
    lora_dim: int = field(default=8, metadata={"help": "LoRA dimension"})
    lora_alpha: int = field(default=8, metadata={"help": "LoRA alpha"})
    lora_dropout: float = field(default=0.0, metadata={"help": "LoRA dropout"})
    target_modules: List[str] = field(
        default_factory=list,
        metadata={"help": "Modules to replace, e.g. ['q','v'] or regex list"},
    )

    def as_peft_config(self) -> LoraConfig:
        if not self.enable_lora:
            raise ValueError("LoRA not enabled")
        params = asdict(self)
        params.pop("enable_lora")
        params["r"] = params.pop("lora_dim")
        params["target_modules"] = ast.literal_eval(params["target_modules"][0])
        return LoraConfig(**params)

@dataclass
class Arguments:
    train: dp_transformers.TrainingArguments
    privacy: dp_transformers.PrivacyArguments
    model: ModelArguments
    lora: LoraArguments


def print_gpu_utilization():
    from pynvml import nvmlInit, nvmlDeviceGetHandleByIndex, nvmlDeviceGetMemoryInfo
    nvmlInit()
    handle = nvmlDeviceGetHandleByIndex(0)
    info = nvmlDeviceGetMemoryInfo(handle)
    logger.info(f"GPU memory used: {info.used//1024**2} MB")


def main(args: Arguments):
    # Entrenamiento
    start_time = time.time()

    # Seed for reproducibility
    transformers.set_seed(args.train.seed)

    #  4bit config
    bnb_config = transformers.BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
    )
    os.makedirs(args.train.output_dir, exist_ok=True)

    # Load model and tokenizer
    model = transformers.AutoModelForCausalLM.from_pretrained(
        args.model.model_name, torch_dtype=torch.bfloat16, quantization_config=bnb_config
    )
    model = prepare_model_for_kbit_training(
        model, use_gradient_checkpointing=args.train.gradient_checkpointing
    )
    tokenizer = transformers.AutoTokenizer.from_pretrained(args.model.model_name)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id
    model.resize_token_embeddings(len(tokenizer))

    # Load and tokenize Dataset (delegated to load_dataset.py)
    tokenized = load_and_tokenize_dataset(
        dataset_name=args.model.dataset_name,
        canaries_dataset=args.model.canaries_dataset,
        type_of_canaries=args.model.type_of_canaries,
        language_prompt=args.model.language_prompt,
        seed=args.train.seed,
        tokenizer=tokenizer,
        sequence_len=args.model.sequence_len,
    )

    # Data collator DP
    collator = dp_transformers.DataCollatorForPrivateCausalLanguageModeling(tokenizer)

    #  Trainer config
    if args.lora.enable_lora:
        peft_conf = args.lora.as_peft_config()
        model = get_peft_model(model, peft_conf)

    if args.privacy.disable_dp:
        trainer = transformers.Trainer(
            args=args.train,
            model=model,
            train_dataset=tokenized['train'],
            eval_dataset=tokenized['test'],
            data_collator=collator,
            tokenizer=tokenizer,
        )
    else:
        trainer = dp_transformers.dp_utils.OpacusDPTrainer(
            args=args.train,
            model=model,
            train_dataset=tokenized['train'],
            eval_dataset=tokenized['test'],
            tokenizer=tokenizer,
            data_collator=collator,
            privacy_args=args.privacy,
        )

    
    try:
        result = trainer.train()
    finally:
        elapsed = time.time() - start_time
        # Epsilon
        if args.privacy.disable_dp:
            eps = None
        else:
            eps = trainer.get_rdp_epsilon()
        trainer.log({"epsilon_rdp": eps})
        # Guardar modelo y métricas
        #trainer.save_model(args.train.output_dir)
        trainer.save_metrics("all", result.metrics)
        
        # Guardado compatible con AutoModelForCausalLM
        model_to_save = model.module if hasattr(model, "module") else model
        model_to_save.save_pretrained(args.train.output_dir)
        tokenizer.save_pretrained(args.train.output_dir)

        save_loss_curves(trainer, args.train.output_dir, disable_dp=args.privacy.disable_dp)
        logger.info("Entrenamiento completado")
        # Guardar tiempo de entrenamiento
        with open(os.path.join(args.train.output_dir, "train_time.txt"), "w") as f:
            f.write(f"{elapsed:.2f} segundos\n")


if __name__ == "__main__":
    parser = transformers.HfArgumentParser((
        dp_transformers.TrainingArguments,
        dp_transformers.PrivacyArguments,
        ModelArguments,
        LoraArguments,
    ))
    train_args, privacy_args, model_args, lora_args = parser.parse_args_into_dataclasses()
    main(Arguments(train=train_args, privacy=privacy_args, model=model_args, lora=lora_args))
