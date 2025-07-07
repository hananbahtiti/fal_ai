import logging
from tasks import task_model_any_llm_vision, task_model_flux_dev_redux, task_model_flux_lora_inpainting, task_model_flux_pro_v1_1_ultra_finetuned, task_model_hyper3d_rodin, task_model_iclight_v2 

def run_model_task(**kwargs):
    model_name = kwargs.get("model_name")
    
    if model_name == "fal-ai/any-llm/vision":
         task_model_any_llm_vision.generate_image(**kwargs)
    elif model_name == "fal-ai/flux/dev/redux":
         task_model_flux_dev_redux.generate_image(**kwargs)
    elif model_name == "fal-ai/flux-lora/inpainting":
         task_model_flux_lora_inpainting.generate_image(**kwargs)
    elif model_name == "fal-ai/flux-pro/v1.1-ultra-finetuned":
         task_model_flux_pro_v1_1_ultra_finetuned.generate_image(**kwargs)
    elif model_name == "fal-ai/hyper3d/rodin":
         task_model_hyper3d_rodin.generate_image(**kwargs)
    elif model_name == "fal-ai/iclight-v2":
         task_model_iclight_v2.generate_image(**kwargs)
    else:
        logging.error(f"Unsupported model: {model_name}")
        raise ValueError(f"Unsupported model: {model_name}")
