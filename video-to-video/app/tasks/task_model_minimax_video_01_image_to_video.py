import fal_client
from redis import Redis
import logging
import os
import json
from dotenv import load_dotenv

load_dotenv()

redis_conn = Redis(host="video2video-redis", port=6379)
logging.basicConfig(level=logging.INFO)

RESULT_TTL = 3600

def generate_image(model_name, prompt, client_id, params):
    """
    Generate a video using image-to-video model (fal-ai/minimax/video-01/image-to-video).

    Parameters:
      model_name (str): Model identifier.
      prompt (str): Text prompt to guide video generation.
      client_id (str): Redis key to store the result.
      params (dict): Must include image_url, prompt_optimizer.
    """
    try:
        logging.info(f"Generating video for client {client_id} using model {model_name}...")

        image_url = params.get("image_url")

        if not image_url:
            raise ValueError("Missing or invalid image_url")

        args = {
            "prompt": prompt,
 
            "prompt_optimizer": params.get("prompt_optimizer", False)
        }

         
        if image_url:
            args["image_url"] = image_url

        logging.info(f"Fal arguments: {args}")

        handler = fal_client.submit(model_name, arguments=args)
        result = handler.get()

        redis_conn.setex(f"result:{client_id}", RESULT_TTL, json.dumps(result))
        logging.info(f"Generation completed for client {client_id}")

    except Exception as e:
        error_msg = f"Error: {str(e)}"
        redis_conn.setex(f"result:{client_id}", RESULT_TTL, error_msg)
        logging.error(f"Failed to generate result for {client_id}: {error_msg}")

        logging.info(f"Fal arguments: {args}")

         
        handler = fal_client.submit(model_name, arguments=args)
        result = handler.get()

         
        redis_conn.setex(f"result:{client_id}", RESULT_TTL, json.dumps(result))
        logging.info(f"Video generation completed for client {client_id}")

    except Exception as e:
        error_msg = f"Error: {str(e)}"
        redis_conn.setex(f"result:{client_id}", RESULT_TTL, error_msg)
        logging.error(f"Failed to generate video for {client_id}: {error_msg}")
