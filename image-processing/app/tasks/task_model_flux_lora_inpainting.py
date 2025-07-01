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
    """
    Generate an image using fal-ai/flux-lora/inpainting with supported parameters.
    """
    try:
        logging.info(f"Generating image for client {client_id} using model {model_name}...")

        args = {
            "prompt": prompt,
            "image_url": params.get("image_url"),
            "mask_url": params.get("mask_url"),
            "image_size": params.get("image_size", "square_hd"),
            "num_inference_steps": params.get("num_inference_steps", 30),
            "seed": params.get("seed"),
            "guidance_scale": params.get("guidance_scale", 7.5),
            "sync_mode": params.get("sync_mode", False),
            "num_images": params.get("num_images", 1),
            "enable_safety_checker": params.get("enable_safety_checker", True),
            "output_format": params.get("output_format", "jpeg"),
            "strength": params.get("strength", 0.75),
        }

         if "loras" in params and isinstance(params["loras"], list):
            args["loras"] = params["loras"]

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
