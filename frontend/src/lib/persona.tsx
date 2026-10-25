"use client";

import {
  createContext,
  useCallback,
  useContext,
  useSyncExternalStore,
  type ReactNode,
} from "react";

export type Persona = "patient" | "clinician";

const STORAGE_KEY = "aegismed-persona";
const CHANGE_EVENT = "aegismed-persona-changed";

interface PersonaContextValue {
  persona: Persona;
  setPersona: (persona: Persona) => void;
}

const PersonaContext = createContext<PersonaContextValue>({
  persona: "patient",
  setPersona: () => {},
});

function readStoredPersona(): Persona {
  try {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    return stored === "clinician" || stored === "patient" ? stored : "patient";
  } catch {
    return "patient";
  }
}

function getServerPersona(): Persona {
  return "patient";
}

function subscribeToPersona(onStoreChange: () => void): () => void {
  window.addEventListener("storage", onStoreChange);
  window.addEventListener(CHANGE_EVENT, onStoreChange);
  return () => {
    window.removeEventListener("storage", onStoreChange);
    window.removeEventListener(CHANGE_EVENT, onStoreChange);
  };
}

export function PersonaProvider({ children }: { children: ReactNode }) {
  const persona = useSyncExternalStore(
    subscribeToPersona,
    readStoredPersona,
    getServerPersona
  );

  const setPersona = useCallback((next: Persona) => {
    try {
      window.localStorage.setItem(STORAGE_KEY, next);
    } catch {
      // Private browsing — the in-memory persona still applies.
    }
    // localStorage does not emit a `storage` event in the writing tab, so the
    // custom event keeps every subscriber in this tab in sync.
    window.dispatchEvent(new Event(CHANGE_EVENT));
  }, []);

  return (
    <PersonaContext.Provider value={{ persona, setPersona }}>
      {children}
    </PersonaContext.Provider>
  );
}

export function usePersona() {
  return useContext(PersonaContext);
}
