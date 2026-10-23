import { 
  signInWithEmailAndPassword, 
  createUserWithEmailAndPassword, 
  signOut, 
  onAuthStateChanged,
  updateProfile
} from 'firebase/auth';
import { ref, get, set } from 'firebase/database';
import { auth, db } from './firebase-config';

export const loginWithEmail = async (email, password) => {
  const userCredential = await signInWithEmailAndPassword(auth, email, password);
  const user = userCredential.user;
  const roleSnap = await get(ref(db, `users/${user.uid}/role`));
  const role = roleSnap.exists() ? roleSnap.val() : 'user';
  return { user, role };
};

export const signupWithEmail = async (name, email, password) => {
  const userCredential = await createUserWithEmailAndPassword(auth, email, password);
  const user = userCredential.user;

  await updateProfile(user, { displayName: name });

  // Store user record in Realtime Database with default role 'user'
  await set(ref(db, `users/${user.uid}`), {
    name,
    email,
    role: 'user',
    createdAt: Date.now(),
    devices: {}
  });

  return { user, role: 'user' };
};

export const logoutUser = async () => {
  await signOut(auth);
};

export const getUserRole = async (uid) => {
  if (!uid) return null;
  const snap = await get(ref(db, `users/${uid}/role`));
  return snap.exists() ? snap.val() : 'user';
};

export const subscribeAuth = (callback) => {
  return onAuthStateChanged(auth, callback);
};
