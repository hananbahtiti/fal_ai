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
    Generate a result using fal-client with parameters for vision + LLM model.

    Parameters:
      model_name (str): Model identifier (e.g., fal-ai/any-llm/vision)
      prompt (str): Text prompt
      client_id (str): Redis key to store the result
      params (dict): Additional parameters like image_url, model, system_prompt, reasoning
    """
    try:
        logging.info(f"Generating output for client {client_id} using model {model_name}...")
        image_file = params.get("image_file")  # متوقع يكون open file object أو bytes
        image_url = params.get("image_url")

        if not image_file and not image_url:
            raise ValueError("Missing or invalid image_url")

        args = {
            "prompt": prompt,
            "system_prompt": params.get("system_prompt", "You are a helpful vision assistant."),
            "reasoning": params.get("reasoning", True)
        }

        if image_url:
            args["image_url"] = image_url
        else:
            args["image"] = image_file

        logging.info(f"Fal arguments: {args}")

        handler = fal_client.submit(model_name, arguments=args)
        result = handler.get()

        redis_conn.setex(f"result:{client_id}", RESULT_TTL, json.dumps(result))
        logging.info(f"Generation completed for client {client_id}")

    except Exception as e:
        error_msg = f"Error: {str(e)}"
        redis_conn.setex(f"result:{client_id}", RESULT_TTL, error_msg)
        logging.error(f"Failed to generate result for {client_id}: {error_msg}")
