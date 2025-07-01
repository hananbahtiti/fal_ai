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
    Generate 3D image using fal-client with new Hyper3D model parameters.

    Parameters:
      model_name (str): Model identifier.
      prompt (str): Text prompt.
      client_id (str): Redis key to store the result.
      params (dict): Additional parameters required by the model.
    """
    try:
        logging.info(f"Generating 3D model for client {client_id} using model {model_name}...")

        args = {
            "prompt": prompt,
            "input_image_urls": params.get("input_image_urls", []),  # List of image URLs
            "condition_mode": params.get("condition_mode", "auto"),
            "seed": params.get("seed"),
            "geometry_file_format": params.get("geometry_file_format", "glb"),  # glb, obj, etc.
            "material": params.get("material", "default"),
            "quality": params.get("quality", "standard"),  # low, standard, high
            "use_hyper": params.get("use_hyper", True),
            "tier": params.get("tier", "standard"),
            "ta_pose": params.get("ta_pose", False),
            "bbox_condition": params.get("bbox_condition", False),
            "addons": params.get("addons", [])
        }

        logging.info(f"Fal arguments: {args}")

        handler = fal_client.submit(model_name, arguments=args)
        result = handler.get()

        redis_conn.setex(f"result:{client_id}", RESULT_TTL, json.dumps(result))
        logging.info(f"3D model generation completed for client {client_id}")

    except Exception as e:
        error_msg = f"Error: {str(e)}"
        redis_conn.setex(f"result:{client_id}", RESULT_TTL, error_msg)
        logging.error(f"Failed to generate 3D model for {client_id}: {error_msg}")
