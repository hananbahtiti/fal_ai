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
    Generate an image or video using fal-client with dynamic parameters.

    Parameters:
      model_name (str): Model identifier.
      prompt (str): Text prompt for the generation.
      client_id (str): Redis key to store the result.
      params (dict): Additional dynamic parameters.
    """
    try:
        logging.info(f"Generating media for client {client_id} using model {model_name}...")

        args = {
            "images_data_url": params.get("images_data_url"),  # URL to images data archive
            "trigger_word": params.get("trigger_word"),
            "learning_rate": params.get("learning_rate", 1e-4),  # typical default if applicable
            "steps": params.get("steps", 30),
            "do_caption": params.get("do_caption", False),
            "data_archive_format": params.get("data_archive_format", "zip")
        }

        # تنظيف القاموس من المفاتيح ذات القيم None
        args = {k: v for k, v in args.items() if v is not None}

        logging.info(f"Fal arguments: {args}")

        handler = fal_client.submit(model_name, arguments=args)
        result = handler.get()

        redis_conn.setex(f"result:{client_id}", RESULT_TTL, json.dumps(result))
        logging.info(f"Generation completed for client {client_id}")

    except Exception as e:
        error_msg = f"Error: {str(e)}"
        redis_conn.setex(f"result:{client_id}", RESULT_TTL, error_msg)
        logging.error(f"Failed to generate media for {client_id}: {error_msg}")
