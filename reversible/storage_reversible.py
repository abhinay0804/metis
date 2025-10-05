from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os, json
from typing import Any, Dict

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
        with open(self._data_path(uid, masking_id), 'wb') as f:
            f.write(nonce + ct)

    def load_original(self, uid: str, masking_id: str) -> Dict[str, Any]:
        key = self._load_or_create_key(uid)
        aesgcm = AESGCM(key)
        with open(self._data_path(uid, masking_id), 'rb') as f:
            blob = f.read()
        nonce, ct = blob[:12], blob[12:]
        pt = aesgcm.decrypt(nonce, ct, None)
        return json.loads(pt.decode('utf-8'))
