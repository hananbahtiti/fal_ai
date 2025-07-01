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
    Upscale a video using fal-client with video-specific parameters.  
  
    Parameters:  
      model_name (str): Model identifier (should be fal-ai/video-upscaler).  
      prompt (str): Not used in this model but kept for compatibility.  
      client_id (str): Redis key to store the result.  
      params (dict): Should include 'video_url' and 'scale'.  
    """  
    try:  
        logging.info(f"Upscaling video for client {client_id} using model {model_name}...")  
  
        args = {  
            "video_url": params.get("video_url"),  
            "scale": params.get("scale", 2),  # default scale 2x  
        }  
  
        if not args["video_url"]:  
            raise ValueError("Missing required parameter: video_url")  
  
        logging.info(f"Fal arguments: {args}")  
  
        handler = fal_client.submit(model_name, arguments=args)  
        result = handler.get()  
  
        redis_conn.setex(f"result:{client_id}", RESULT_TTL, json.dumps(result))  
        logging.info(f"Video upscale completed for client {client_id}")  
  
    except Exception as e:  
        error_msg = f"Error: {str(e)}"  
        redis_conn.setex(f"result:{client_id}", RESULT_TTL, error_msg)  
        logging.error(f"Failed to upscale video for {client_id}: {error_msg}")
