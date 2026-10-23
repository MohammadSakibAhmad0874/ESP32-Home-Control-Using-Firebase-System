import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getDatabase } from 'firebase/database';

export const firebaseConfig = {
  apiKey: "AIzaSyDFXGOMsOqLRa60sOdUlGT925taGmR1KDc",
  authDomain: "apnaghar-3f865.firebaseapp.com",
  databaseURL: "https://apnaghar-3f865-default-rtdb.firebaseio.com",
  projectId: "apnaghar-3f865",
  storageBucket: "apnaghar-3f865.firebasestorage.app",
  messagingSenderId: "325855291290",
  appId: "1:325855291290:web:a9ca4c465f1f3dc603fc23",
  measurementId: "G-KC3571R3W5"
};

export const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getDatabase(app);
