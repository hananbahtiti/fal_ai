import fal_client
from redis import Redis
import logging
import os
import json
from dotenv import load_dotenv

load_dotenv()

redis_conn = Redis(host="image-redis", port=6379)
logging.basicConfig(level=logging.INFO)

RESULT_TTL = 3600

def generate_image(model_name, prompt, client_id, params):
    """
    Generate an image using fal-client with dynamic parameters.

    Parameters:
      model_name (str): Model identifier.
      prompt (str): Text prompt for the image.
      client_id (str): Redis key to store the result.
      params (dict): Additional dynamic parameters.
    """
    try:
        logging.info(f"Generating image for client {client_id} using model {model_name}...")

        # Build the arguments dictionary based on the model's documentation
        args = {
            "prompt": prompt,
            "num_images": params.get("num_images", 1),
            "enable_safety_checker": params.get("enable_safety_checker", True),
            "streaming": params.get("streaming", False),  # Streaming mode
            "image_size": params.get("image_size", "landscape_4_3"),
            "num_inference_steps": params.get("num_inference_steps", 30),  # Typical default
            "guidance_scale": params.get("guidance_scale", 7.5),  # CFG scale
            "sync_mode": params.get("sync_mode", False)
        }

        # Optional: If seed is provided
        if "seed" in params and params["seed"] is not None:
            args["seed"] = params["seed"]

        logging.info(f"Fal arguments: {args}")

        # Submit the request to fal-client
        handler = fal_client.submit(model_name, arguments=args)
        result = handler.get()

        # Store result in Redis
        redis_conn.setex(f"result:{client_id}", RESULT_TTL, json.dumps(result))
        logging.info(f"Image generation completed for client {client_id}")

    except Exception as e:
        error_msg = f"Error: {str(e)}"
        redis_conn.setex(f"result:{client_id}", RESULT_TTL, error_msg)
        logging.error(f"Failed to generate image for {client_id}: {error_msg}")
