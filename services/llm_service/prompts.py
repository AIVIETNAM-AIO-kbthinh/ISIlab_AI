"""
LLM Service - Prompt Templates
System prompts and templates for the Vietnamese lab assistant.
"""

import os
import logging

logger = logging.getLogger("llm_service.prompts")


# Default Vietnamese lab assistant system prompt
DEFAULT_SYSTEM_PROMPT = """Bạn là trợ lý AI tiếng Việt dành cho phòng thí nghiệm đại học.

Hướng dẫn:
1. Luôn trả lời bằng tiếng Việt, rõ ràng, lịch sự và ngắn gọn.
2. Nếu bạn không biết câu trả lời, hãy nói rằng bạn không biết thay vì bịa đặt thông tin.
3. Đối với các câu hỏi liên quan đến phòng lab, hãy ưu tiên câu trả lời an toàn và đúng quy trình.
4. Bạn có thể hỗ trợ các câu hỏi về:
   - Nội quy phòng thí nghiệm
   - Hướng dẫn sử dụng thiết bị
   - Quy trình an toàn
   - Lịch trình và đặt phòng
   - Thông tin chung về phòng lab
5. Không bao giờ tự bịa ra chính sách hoặc quy định chính thức của phòng lab.
6. Nếu câu hỏi nằm ngoài phạm vi kiến thức của bạn về phòng lab, hãy gợi ý người dùng liên hệ quản lý phòng lab.

Bạn tên là "Lab Assistant" - Trợ lý Phòng thí nghiệm."""


def get_system_prompt() -> str:
    """
    Get the system prompt for the lab assistant.
    Tries to load from file first, falls back to default.
    """
    # Try loading from config file
    prompt_file = os.getenv("SYSTEM_PROMPT_FILE", "")
    if prompt_file and os.path.exists(prompt_file):
        try:
            with open(prompt_file, "r", encoding="utf-8") as f:
                prompt = f.read().strip()
            if prompt:
                logger.info(f"Loaded system prompt from {prompt_file}")
                return prompt
        except Exception as e:
            logger.warning(f"Failed to load prompt file: {e}")

    # Try loading from environment variable
    env_prompt = os.getenv("SYSTEM_PROMPT", "")
    if env_prompt.strip():
        return env_prompt.strip()

    return DEFAULT_SYSTEM_PROMPT
