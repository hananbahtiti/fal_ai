import logging
from tasks import task_model_video_upscaler, task_model_sync_lipsync, task_model_minimax_video_01_image_to_video

def run_model_task(**kwargs):
    model_name = kwargs.get("model_name")
    
    if model_name == "fal-ai/kling-video/v1.6/pro/image-to-video":
        task_model_kling_video_v1_6_pro_image_to_video.generate_image(**kwargs)
    elif model_name == "fal-ai/minimax/video-01/image-to-video":
        task_model_minimax_video_01_image_to_video.generate_image(**kwargs)
    elif model_name == "fal-ai/sync-lipsync":
        task_model_sync_lipsync.generate_image(**kwargs)
    elif model_name == "fal-ai/video-upscaler":
        task_model_video_upscaler.generate_image(**kwargs)
    else:
        logging.error(f"Unsupported model: {model_name}")
        raise ValueError(f"Unsupported model: {model_name}")
