import os
import json
import base64
from typing import Any, Dict, List

from google.cloud import firestore
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


class FirestoreStore:
    def __init__(self):
        self.client = firestore.Client(project=os.environ.get('FIREBASE_PROJECT_ID'))

    def save_masked(self, uid: str, masking_id: str, doc: Dict[str, Any]) -> None:
        ref = self.client.collection('users').document(uid).collection('my_maskings').document(masking_id)
        ref.set(doc)

    def list_maskings(self, uid: str) -> List[Dict[str, Any]]:
        ref = self.client.collection('users').document(uid).collection('my_maskings')
        # Order by created_at if available
        try:
            docs = ref.order_by('created_at', direction=firestore.Query.DESCENDING).stream()
        except Exception:
            docs = ref.stream()
        res = []
        for d in docs:
            data = d.to_dict()
            res.append({
                'masking_id': d.id,
                'file_name': data.get('file_name', ''),
                'file_type': data.get('file_type', ''),
                'created_at': data.get('created_at'),
                'reversible': data.get('reversible', False)
            })
        return res

    def get_masked(self, uid: str, masking_id: str) -> Dict[str, Any] | None:
        ref = self.client.collection('users').document(uid).collection('my_maskings').document(masking_id)
        doc = ref.get()
        return doc.to_dict() if doc.exists else None


class EncryptedLocalStore:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def _user_dir(self, uid: str) -> str:
        d = os.path.join(self.base_dir, uid)
        os.makedirs(d, exist_ok=True)
        return d

    def _key_path(self, uid: str) -> str:
        return os.path.join(self._user_dir(uid), 'key.bin')

    def _data_path(self, uid: str, masking_id: str) -> str:
        return os.path.join(self._user_dir(uid), f'{masking_id}.bin')

    def _load_or_create_key(self, uid: str) -> bytes:
        kp = self._key_path(uid)
        if os.path.exists(kp):
            with open(kp, 'rb') as f:
                return f.read()
        # Derive a random key and store it (for demo: store raw; in prod wrap with OS/KMS)
        key = AESGCM.generate_key(bit_length=256)
        with open(kp, 'wb') as f:
            f.write(key)
        return key

    def store_original(self, uid: str, masking_id: str, original: Dict[str, Any]) -> None:
        key = self._load_or_create_key(uid)
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        data = json.dumps(original).encode('utf-8')
        ct = aesgcm.encrypt(nonce, data, None)
        blob = nonce + ct
        with open(self._data_path(uid, masking_id), 'wb') as f:
            f.write(blob)

    def load_original(self, uid: str, masking_id: str) -> Dict[str, Any]:
        key = self._load_or_create_key(uid)
        aesgcm = AESGCM(key)
        with open(self._data_path(uid, masking_id), 'rb') as f:
            blob = f.read()
        nonce, ct = blob[:12], blob[12:]
        pt = aesgcm.decrypt(nonce, ct, None)
        return json.loads(pt.decode('utf-8'))


