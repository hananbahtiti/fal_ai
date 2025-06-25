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
    Generate video using fal-client with parameters for kling-video v1.6.

    Parameters:
      model_name (str): Model identifier.
      prompt (str): Text prompt.
      client_id (str): Redis key to store the result.
      params (dict): Additional parameters (duration, aspect_ratio, negative_prompt, cfg_scale).
    """
    try:
        logging.info(f"Generating video for client {client_id} using model {model_name}...")

        args = {
            "prompt": prompt,
            "duration": params.get("duration", 5),                
            "aspect_ratio": params.get("aspect_ratio", "16:9"),  
            "negative_prompt": params.get("negative_prompt", ""),  
            "cfg_scale": params.get("cfg_scale", 7.5) 
        }

        # خيار اختيار seed
        if "seed" in params and params["seed"] is not None:
            args["seed"] = params["seed"]

        logging.info(f"Fal arguments: {args}")

        handler = fal_client.submit(model_name, arguments=args)
        result = handler.get()

        redis_conn.setex(f"result:{client_id}", RESULT_TTL, json.dumps(result))
        logging.info(f"Video generation completed for client {client_id}")

    except Exception as e:
        error_msg = f"Error: {str(e)}"
        redis_conn.setex(f"result:{client_id}", RESULT_TTL, error_msg)
        logging.error(f"Failed to generate video for {client_id}: {error_msg}")
