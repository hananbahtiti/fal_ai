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
  
def generate_sync_lipsync(model_name, client_id, params):  
    """  
    Generate a lipsync video using fal-client for fal-ai/sync-lipsync model.  
  
    Parameters:  
      model_name (str): Model identifier (should be fal-ai/sync-lipsync).  
      client_id (str): Redis key to store the result.  
      params (dict): Contains video_url, audio_url, model, sync_mode  
    """  
    try:  
        logging.info(f"Generating lipsync for client {client_id} using model {model_name}...")  
  
        args = {  
            "video_url": params.get("video_url"),  
            "audio_url": params.get("audio_url"),  
            "model": params.get("model", "Wav2Lip"),  # Default model is usually "Wav2Lip"  
            "sync_mode": params.get("sync_mode", True)  
        }  
  
        if not args["video_url"] or not args["audio_url"]:  
            raise ValueError("video_url and audio_url are required parameters.")  
  
        logging.info(f"LipSync arguments: {args}")  
  
        handler = fal_client.submit(model_name, arguments=args)  
        result = handler.get()  
  
        redis_conn.setex(f"result:{client_id}", RESULT_TTL, json.dumps(result))  
        logging.info(f"LipSync generation completed for client {client_id}")  
  
    except Exception as e:  
        error_msg = f"Error: {str(e)}"  
        redis_conn.setex(f"result:{client_id}", RESULT_TTL, error_msg)  
        logging.error(f"Failed to generate lipsync for {client_id}: {error_msg}")
