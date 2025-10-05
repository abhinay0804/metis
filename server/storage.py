import os
import json
import base64
from typing import Any, Dict, List
from datetime import datetime

from google.cloud import firestore
from google.oauth2 import service_account


class FirestoreStore:
    def __init__(self):
        project = os.environ.get('FIREBASE_PROJECT_ID')
        cred_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if not cred_path or not os.path.exists(cred_path):
            raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS not set or file not found")
        creds = service_account.Credentials.from_service_account_file(cred_path)
        self.client = firestore.Client(project=project, credentials=creds)

    def save_masked(self, uid: str, masking_id: str, doc: Dict[str, Any]) -> None:
        ref = self.client.collection('users').document(uid).collection('my_maskings').document(masking_id)
        ref.set(doc)

    def list_maskings(self, uid: str) -> List[Dict[str, Any]]:
        ref = self.client.collection('users').document(uid).collection('my_maskings')
        # Order by created_at if present
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


class LocalMaskedStore:
    def __init__(self, base_dir: str):
        self.base_dir = os.path.join(base_dir, 'masked')
        os.makedirs(self.base_dir, exist_ok=True)

    def _user_dir(self, uid: str) -> str:
        d = os.path.join(self.base_dir, uid)
        os.makedirs(d, exist_ok=True)
        return d

    def _doc_path(self, uid: str, masking_id: str) -> str:
        return os.path.join(self._user_dir(uid), f'{masking_id}.json')

    def save_masked(self, uid: str, masking_id: str, doc: Dict[str, Any]) -> None:
        with open(self._doc_path(uid, masking_id), 'w', encoding='utf-8') as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)

    def list_maskings(self, uid: str) -> List[Dict[str, Any]]:
        d = self._user_dir(uid)
        results: List[Dict[str, Any]] = []
        for name in os.listdir(d):
            if name.endswith('.json'):
                p = os.path.join(d, name)
                try:
                    with open(p, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    results.append({
                        'masking_id': name[:-5],
                        'file_name': data.get('file_name', ''),
                        'file_type': data.get('file_type', ''),
                        'created_at': data.get('created_at'),
                        'reversible': data.get('reversible', False),
                    })
                except Exception:
                    continue
        # Sort by created_at desc when available
        def _ts(item):
            ts = item.get('created_at')
            try:
                return datetime.fromisoformat(ts) if ts else datetime.min
            except Exception:
                return datetime.min
        results.sort(key=_ts, reverse=True)
        return results

    def get_masked(self, uid: str, masking_id: str) -> Dict[str, Any] | None:
        p = self._doc_path(uid, masking_id)
        if not os.path.exists(p):
            return None
        with open(p, 'r', encoding='utf-8') as f:
            return json.load(f)

# Local analysis storage for analysis processing results
class LocalAnalysisStore:
    def __init__(self, base_dir: str):
        self.base_dir = os.path.join(base_dir, 'analysis')
        os.makedirs(self.base_dir, exist_ok=True)

    def _user_dir(self, uid: str) -> str:
        d = os.path.join(self.base_dir, uid)
        os.makedirs(d, exist_ok=True)
        return d

    def _doc_path(self, uid: str, analysis_id: str) -> str:
        return os.path.join(self._user_dir(uid), f'{analysis_id}.json')

    def save(self, uid: str, analysis_id: str, doc: Dict[str, Any]) -> None:
        with open(self._doc_path(uid, analysis_id), 'w', encoding='utf-8') as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)

    def list(self, uid: str) -> List[Dict[str, Any]]:
        d = self._user_dir(uid)
        results: List[Dict[str, Any]] = []
        if not os.path.exists(d):
            return results
        for name in os.listdir(d):
            if name.endswith('.json'):
                p = os.path.join(d, name)
                try:
                    with open(p, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    results.append({
                        'analysis_id': name[:-5],
                        'file_name': data.get('file_name', ''),
                        'file_type': data.get('file_type', ''),
                        'created_at': data.get('created_at'),
                    })
                except Exception:
                    continue
        def _ts(item):
            ts = item.get('created_at')
            try:
                return datetime.fromisoformat(ts) if ts else datetime.min
            except Exception:
                return datetime.min
        results.sort(key=_ts, reverse=True)
        return results

    def get(self, uid: str, analysis_id: str) -> Dict[str, Any] | None:
        p = self._doc_path(uid, analysis_id)
        if not os.path.exists(p):
            return None
        with open(p, 'r', encoding='utf-8') as f:
            return json.load(f)

