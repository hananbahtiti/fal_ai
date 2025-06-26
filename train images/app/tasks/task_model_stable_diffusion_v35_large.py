import fal_client
from redis import Redis
import logging
import os
import json
from dotenv import load_dotenv

load_dotenv()
os.environ["FAL_KEY"] = "671b3239-6a7c-4449-a85e-caa161fe3351:631d5730d85692de182d398b1b072496"

redis_conn = Redis(host="redis", port=6379)
logging.basicConfig(level=logging.INFO)

RESULT_TTL = 3600

def generate_image(model_name, prompt, client_id, params):
    try:
        logging.info(f"Generating image for client {client_id} using model {model_name}...")

        # بناء args مع القيم الأساسية
        args = {
            "prompt": prompt,
            "negative_prompt": params.get("negative_prompt", ""),
            "num_images": params.get("num_images", 1),
            "image_size": params.get("image_size", "landscape_4_3"),
            "guidance_scale": params.get("guidance_scale", 7.5),
            "num_inference_steps": params.get("num_inference_steps", 30),
            "output_format": params.get("output_format", "jpeg"),
            "sync_mode": params.get("sync_mode", False),
            "enable_safety_checker": params.get("enable_safety_checker", True),

            # ControlNet
            "controlnet_model": params.get("controlnet_model"),
            "controlnet_type": params.get("controlnet_type"),
            "controlnet_image": params.get("controlnet_image"),
            "controlnet_conditioning_scale": params.get("controlnet_conditioning_scale"),
            "controlnet_start_percentage": params.get("controlnet_start_percentage"),
            "controlnet_end_percentage": params.get("controlnet_end_percentage"),
        }

        # التعامل مع LoRAs (تأكد أن كل واحد يحتوي على path و scale)
        loras = params.get("loras", [])
        valid_loras = []
        for lora in loras:
            if isinstance(lora, dict) and "path" in lora and "scale" in lora:
                valid_loras.append({
                    "path": lora["path"],
                    "scale": lora["scale"]
                })
        if valid_loras:
            args["loras"] = valid_loras

        # IP Adapter
        ip_adapter = {
            "path": params.get("ip_adapter_path"),
            "subfolder": params.get("ip_adapter_subfolder"),
            "weight_name": params.get("ip_adapter_weight_name"),
            "image_encoder_path": params.get("ip_adapter_image_encoder_path"),
            "image_encoder_subfolder": params.get("ip_adapter_image_encoder_subfolder"),
            "image_encoder_weight_name": params.get("ip_adapter_image_encoder_weight_name"),
            "image_url": params.get("ip_adapter_image_url"),
            "mask_image_url": params.get("ip_adapter_mask_image_url"),
            "mask_threshold": params.get("ip_adapter_mask_threshold"),
            "scale": params.get("ip_adapter_scale")
        }
        # إزالة قيم None من ip_adapter
        ip_adapter = {k: v for k, v in ip_adapter.items() if v is not None}
        if ip_adapter:
            args["ip_adapter"] = ip_adapter

        # إذا وُجد seed أضفه
        if "seed" in params and params["seed"] is not None:
            args["seed"] = params["seed"]

        # إزالة أي مفاتيح بقيم None من args
        args = {k: v for k, v in args.items() if v is not None}

        logging.info(f"Fal arguments: {args}")

        handler = fal_client.submit(model_name, arguments=args)
        result = handler.get()

        redis_conn.setex(f"result:{client_id}", RESULT_TTL, json.dumps(result))
        logging.info(f"Image generation completed for client {client_id}")

    except Exception as e:
        error_msg = f"Error: {str(e)}"
        redis_conn.setex(f"result:{client_id}", RESULT_TTL, error_msg)
        logging.error(f"Failed to generate image for {client_id}: {error_msg}")
