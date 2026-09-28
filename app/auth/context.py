from fastapi import Header


async def get_user_id(
    x_user_id: str = Header(...),
) -> str:
    return x_user_id