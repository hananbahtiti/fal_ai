import logging
from tasks import task_model_flux_lora_fast_training, task_model_hunyuan_video_lora_training             # Add all models here

def run_model_task(**kwargs):
    model_name = kwargs.get("model_name")
    
    if model_name == "fal-ai/flux-lora-fast-training":
        task_model_flux_lora_fast_training.train_model(**kwargs)
    elif model_name == "fal-ai/hunyuan-video-lora-training":
        task_model_hunyuan_video_lora_training.train_model(**kwargs)
  
    else:
        logging.error(f"Unsupported model: {model_name}")
        raise ValueError(f"Unsupported model: {model_name}")
