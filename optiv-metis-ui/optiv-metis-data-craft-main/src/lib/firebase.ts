import { initializeApp } from 'firebase/app';
import { getAuth, signInWithEmailAndPassword, onAuthStateChanged } from 'firebase/auth';

const config = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || 'AIzaSyBNS_Q1NEMPuxglRFMT9oSNfz1DF70PhZo',
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || 'optiv-case-study.firebaseapp.com',
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || 'optiv-case-study',
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || 'optiv-case-study.firebasestorage.app',
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || '1052810295897',
  appId: import.meta.env.VITE_FIREBASE_APP_ID || '1:1052810295897:web:204aaed734ee83d30b8f48',
};

const app = initializeApp(config);
export const auth = getAuth(app);

export async function loginWithEmail(email: string, password: string) {
  const cred = await signInWithEmailAndPassword(auth, email, password);
  const token = await cred.user.getIdToken();
  localStorage.setItem('idToken', token);
  return cred.user;
}

export function listenAuth(callback: (token: string | null) => void) {
  return onAuthStateChanged(auth, async (user) => {
    if (user) {
      const token = await user.getIdToken();
      localStorage.setItem('idToken', token);
      callback(token);
    } else {
      localStorage.removeItem('idToken');
      callback(null);
    }
  });
}


