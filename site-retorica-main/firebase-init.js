import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-app.js";
import {
  getFirestore, collection, doc,
  onSnapshot, addDoc, deleteDoc, updateDoc,
  setDoc, getDoc, getDocs, orderBy, query, serverTimestamp, runTransaction, Timestamp, increment
} from "https://www.gstatic.com/firebasejs/10.12.0/firebase-firestore.js";
import {
  getAuth, GoogleAuthProvider, signInWithPopup, signOut,
  onAuthStateChanged
} from "https://www.gstatic.com/firebasejs/10.12.0/firebase-auth.js";
import {
  getStorage, ref as storageRef, uploadBytesResumable, getDownloadURL, deleteObject
} from "https://www.gstatic.com/firebasejs/10.12.0/firebase-storage.js";

const firebaseConfig = {
  apiKey: "AIzaSyDUgxw6RxmiQJnlo1trXL7l8lLYKuk0984",
  authDomain: "retorica-b05b3.firebaseapp.com",
  projectId: "retorica-b05b3",
  storageBucket: "retorica-b05b3.firebasestorage.app",
  messagingSenderId: "299312853191",
  appId: "1:299312853191:web:f3f2536da460743940cee2",
  measurementId: "G-2TQ7Q80QPK"
};

const app      = initializeApp(firebaseConfig);
const db       = getFirestore(app);
const auth     = getAuth(app);
const storage  = getStorage(app);
const provider = new GoogleAuthProvider();

export {
  app, db, auth, storage, provider,
  collection, doc, onSnapshot, addDoc, deleteDoc, updateDoc, setDoc, getDoc, getDocs, orderBy, query, serverTimestamp, runTransaction, Timestamp, increment,
  GoogleAuthProvider, signInWithPopup, signOut, onAuthStateChanged,
  storageRef, uploadBytesResumable, getDownloadURL, deleteObject
};
