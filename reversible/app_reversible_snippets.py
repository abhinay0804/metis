# FastAPI reversible snippets (archived)

from fastapi import Depends, HTTPException
from .auth import User

# In /process, previously used:
# reversible: bool = Form(True)
# if reversible: enc_store.store_original(user.uid, masking_id, original_content)

# Route previously exposed:
# @app.get("/maskings/{masking_id}/original")
# def get_original(masking_id: str, user: User = Depends(verify_id_token)) -> dict:
#     try:
#         orig = enc_store.load_original(user.uid, masking_id)
#         return {"original": orig}
#     except FileNotFoundError:
#         raise HTTPException(status_code=404, detail="Original not stored or not found")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to retrieve original: {str(e)}")
