import logging
from tasks import task_model_stable_diffusion_v35_large             # Add all models here

def run_model_task(**kwargs):
    model_name = kwargs.get("model_name")
    
    if model_name == "fal-ai/stable-diffusion-v35-large":
        task_model_stable_diffusion_v35_large.train_model(**kwargs)
    elif model_name == "":
        task_model_flux_pro_ultra.train_model(**kwargs)
    elif model_name == "":
        task_model_flux_dev.train_model(**kwargs)
    elif model_name == "":
        task_model_ideogram_v2.train_model(**kwargs)
    elif model_name == "":
        task_model_flux_schnell.train_model(**kwargs)
    else:
        logging.error(f"Unsupported model: {model_name}")
        raise ValueError(f"Unsupported model: {model_name}")
