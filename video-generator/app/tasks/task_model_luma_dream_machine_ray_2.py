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
    Generate an image (or video) using fal-client with parameters for luma-dream-machine ray-2 model.

    Parameters:
      model_name (str): Model identifier.
      prompt (str): Text prompt for generation.
      client_id (str): Redis key to store the result.
      params (dict): Additional dynamic parameters such as aspect_ratio, loop, resolution, duration.
    """
    try:
        logging.info(f"Generating image/video for client {client_id} using model {model_name}...")

        args = {
            "prompt": prompt,
            "aspect_ratio": params.get("aspect_ratio", "16:9"),   
            "loop": params.get("loop", False),  
            "resolution": params.get("resolution", "512x512"),   
            "duration": params.get("duration", 4),  
             
        }

        logging.info(f"Fal arguments: {args}")

        handler = fal_client.submit(model_name, arguments=args)
        result = handler.get()

        redis_conn.setex(f"result:{client_id}", RESULT_TTL, json.dumps(result))
        logging.info(f"Generation completed for client {client_id}")

    except Exception as e:
        error_msg = f"Error: {str(e)}"
        redis_conn.setex(f"result:{client_id}", RESULT_TTL, error_msg)
        logging.error(f"Failed to generate for {client_id}: {error_msg}")
