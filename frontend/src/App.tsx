import { useEffect, useState } from "react";
import Admin from "./pages/Admin";
import Calculator from "./pages/Calculator";

function useHashRoute(): string {
  const [hash, setHash] = useState(() => window.location.hash);
  useEffect(() => {
    const onChange = () => setHash(window.location.hash);
    window.addEventListener("hashchange", onChange);
    return () => window.removeEventListener("hashchange", onChange);
  }, []);
  return hash;
}

export default function App() {
  const isAdmin = useHashRoute().startsWith("#/admin");

  return (
    <div className="app">
      <header className="topbar">
        <a className="brand" href="#/">
          Comparador <span>EUR → CVE</span>
        </a>
        <nav>
          <a href="#/">Calculadora</a>
          <a href="#/admin">Admin</a>
        </nav>
      </header>
      <main>{isAdmin ? <Admin /> : <Calculator />}</main>
      <footer className="footer">
        Valores indicativos, atualizados manualmente. Confirma sempre no site do provedor antes de enviar.
      </footer>
    </div>
  );
}