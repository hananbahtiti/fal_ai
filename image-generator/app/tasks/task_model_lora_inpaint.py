import fal_client
from redis import Redis
import logging
import os
import json
from dotenv import load_dotenv

load_dotenv()

redis_conn = Redis(host="redis", port=6379)
logging.basicConfig(level=logging.INFO)

RESULT_TTL = 3600

def generate_image(model_name, prompt, client_id, params):
    try:
        logging.info(f"Generating for client {client_id} with model {model_name}")

        
        guidance_scale = params.get("guidance_scale")
        cfg = guidance_scale if guidance_scale is not None else params.get("cfg", guidance_scale)

        args = {
            "model_name": model_name,
            "prompt": prompt,
            "unet_name": params.get("unet_name"),
            "variant": params.get("variant"),
            "negative_prompt": params.get("negative_prompt"),
            "prompt_weighting": params.get("prompt_weighting"),
            "image_url": params.get("image_url"),
            "mask_url": params.get("mask_url"),
            "noise_strength": params.get("noise_strength"),

            "image_encoder_path": params.get("image_encoder_path"),
            "image_encoder_subfolder": params.get("image_encoder_subfolder"),
            "image_encoder_weight_name": params.get("image_encoder_weight_name"),

            "ic_light_model_url": params.get("ic_light_model_url"),
            "ic_light_model_bg_image_url": params.get("ic_light_model_bg_image_url"),
            "ic_light_image_url": params.get("ic_light_image_url"),

            "seed": params.get("seed"),
            "num_inference_steps": params.get("num_inference_steps"),
            "guidance_scale": guidance_scale,
            "cfg": cfg,
            "clip_skip": params.get("clip_skip"),
            "scheduler": params.get("scheduler"),
            "prediction_type": params.get("prediction_type"),

            "rescale_betas_snr_zero": params.get("rescale_betas_snr_zero"),
            "image_format": params.get("image_format"),
            "num_images": params.get("num_images"),
            "enable_safety_checker": params.get("enable_safety_checker"),

            "tile_width": params.get("tile_width"),
            "tile_height": params.get("tile_height"),
            "tile_stride_width": params.get("tile_stride_width"),
            "tile_stride_height": params.get("tile_stride_height"),
            "eta": params.get("eta"),
            "debug_latents": params.get("debug_latents"),
            "debug_per_pass_latents": params.get("debug_per_pass_latents"),

            # Controlnet guess mode
            "controlnet_guess_mode": params.get("controlnet_guess_mode"),

            # Sigmas
            "sigmas": params.get("sigmas"),  # {"method": "ddim", "array": [...]}

            # Timesteps
            "timesteps": params.get("timesteps"),  # {"method": "uniform", "array": [...]}

            # IP Adapter
            "ip_adapter": params.get("ip_adapter"),

            # Controlnets
            "controlnets": params.get("controlnets"),

            # Embeddings
            "embeddings": params.get("embeddings"),

            # LoRAs
            "loras": params.get("loras"),
        }

        
        args = {k: v for k, v in args.items() if v is not None}

        logging.info(f"Payload arguments: {args}")

        handler = fal_client.submit(model_name, arguments=args)
        result = handler.get()

        redis_conn.setex(f"result:{client_id}", RESULT_TTL, json.dumps(result))
        logging.info(f"Completed client {client_id}")

    except Exception as e:
        error_msg = str(e)
        redis_conn.setex(f"result:{client_id}", RESULT_TTL, error_msg)
        logging.error(f"Failed for {client_id}: {error_msg}")
