"""
Content Lab Handlers
"""
from .generate_text import handle_generate_text
from .generate_image import handle_generate_image
from .generate_video import handle_generate_video_runway
# handle_generate_video_fal REMOVED in Fase 2 §2.5 (FAL provider eliminated · DDD I1)
from .list_content import handle_list_content
# from .save_content import handle_save_content  # REMOVED: save endpoint deprecated
from .delete_content import handle_delete_content
from .analyze_insight import handle_analyze_insight
from .analyze_forecast import handle_analyze_forecast
from .analyze_virality import handle_predict_virality

__all__ = [
    "handle_generate_text",
    "handle_generate_image",
    "handle_generate_video_runway",
    "handle_list_content",
    # "handle_save_content",  # REMOVED: save endpoint deprecated
    "handle_delete_content",
    "handle_analyze_insight",
    "handle_analyze_forecast",
    "handle_predict_virality"
]
