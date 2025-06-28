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
    """
    Generate an image using fal-ai/iclight-v2 with supported parameters.
    """
    try:
        logging.info(f"Generating image for client {client_id} using model {model_name}...")

        # Use guidance_scale if provided, otherwise fallback to cfg
        guidance_scale = params.get("guidance_scale")
        cfg = guidance_scale if guidance_scale is not None else params.get("cfg", 7.5)

        args = {
            "prompt": prompt,
            "image_url": params.get("image_url"),
            "negative_prompt": params.get("negative_prompt"),
            "mask_image_url": params.get("mask_image_url"),
            "background_threshold": params.get("background_threshold"),
            "image_size": params.get("image_size", "landscape_4_3"),
            "num_inference_steps": params.get("num_inference_steps", 30),
            "seed": params.get("seed"),
            "initial_latent": params.get("initial_latent"),
            "enable_hr_fix": params.get("enable_hr_fix", False),
            "sync_mode": params.get("sync_mode", False),
            "num_images": params.get("num_images", 1),
            "cfg": cfg,
            "guidance_scale": guidance_scale,
            "lowres_denoise": params.get("lowres_denoise"),
            "highres_denoise": params.get("highres_denoise"),
            "hr_downscale": params.get("hr_downscale"),
            "enable_safety_checker": params.get("enable_safety_checker", True),
            "output_format": params.get("output_format", "jpeg")
        }

        
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
