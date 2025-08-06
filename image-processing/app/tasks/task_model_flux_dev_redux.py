import fal_client
from redis import Redis
import logging
import os
import json
from dotenv import load_dotenv

load_dotenv()

redis_conn = Redis(host="image-processing-redis", port=6379)
logging.basicConfig(level=logging.INFO)

RESULT_TTL = 3600

def generate_image(model_name, prompt, client_id, params):
    """
    Generate an image using fal-ai/flux-1/dev/redux with supported parameters.

    Parameters:
      model_name (str): Model identifier.
      prompt (str): Text prompt for the image.
      client_id (str): Redis key to store the result.
      params (dict): Supported parameters for redux model.
    """
    try:
        logging.info(f"Generating image for client {client_id} using model {model_name}...")
        image_url = params.get("image_url")

        if not image_url:
            raise ValueError("Missing or invalid image_url")

        args = {
          
            "image_size": params.get("image_size", "landscape_4_3"),
            "num_inference_steps": params.get("num_inference_steps", 30),
            "seed": params.get("seed"),
            "guidance_scale": params.get("guidance_scale", 7.5),
            "sync_mode": params.get("sync_mode", False),
            "num_images": params.get("num_images", 1),
            "enable_safety_checker": params.get("enable_safety_checker", True)
        }

        if image_url:
            args["image_url"] = image_url
         

         
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
