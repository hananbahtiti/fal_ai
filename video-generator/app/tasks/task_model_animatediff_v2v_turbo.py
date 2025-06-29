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
    Generate video-to-video animation using fal-client for 'animatediff-v2v/turbo' model.

    Parameters:
      model_name (str): Model identifier.
      prompt (str): Positive prompt.
      client_id (str): Redis key to store the result.
      params (dict): Additional parameters for the model.
    """
    try:
        logging.info(f"Generating animation for client {client_id} using model {model_name}...")

        args = {
            "video_url": params.get("video_url"),  # Required
            "prompt": prompt,
            "negative_prompt": params.get("negative_prompt", ""),
            "num_inference_steps": params.get("num_inference_steps", 25),
            "guidance_scale": params.get("guidance_scale", 7.5),
            "select_every_nth_frame": params.get("select_every_nth_frame", 1)
        }

        if "seed" in params:
            args["seed"] = params["seed"]

        # Loras is a list of dicts with "path" and "scale"
        if "loras" in params:
            args["loras"] = params["loras"]

        logging.info(f"Fal arguments: {args}")

        handler = fal_client.submit(model_name, arguments=args)
        result = handler.get()

        redis_conn.setex(f"result:{client_id}", RESULT_TTL, json.dumps(result))
        logging.info(f"Animation generation completed for client {client_id}")

    except Exception as e:
        error_msg = f"Error: {str(e)}"
        redis_conn.setex(f"result:{client_id}", RESULT_TTL, error_msg)
        logging.error(f"Failed to generate animation for {client_id}: {error_msg}")
