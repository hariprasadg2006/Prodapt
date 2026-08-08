import { useState } from "react";
import SignIn from "./components/SignIn.jsx";
import SignUp from "./components/SignUp.jsx";
import Workspace from "./components/Workspace.jsx";

// view is one of: "signin" | "signup" | "workspace"
// This is the only "routing" in the app — plain local state, no
// react-router. Sign in/up are still frontend-only (no backend auth);
// the Workspace is the real thing, talking to the FastAPI backend
// described in the integration guide.
export default function App() {
  const [view, setView] = useState("signin");
  const [userName, setUserName] = useState("");

  function handleSignedIn(email) {
    setUserName(email.split("@")[0]);
    setView("workspace");
  }

  function handleSignedUp(name) {
    setUserName(name);
    setView("workspace");
  }

  function handleSignOut() {
    setUserName("");
    setView("signin");
  }

  if (view === "workspace") {
    return <Workspace userName={userName} onSignOut={handleSignOut} />;
  }

  if (view === "signup") {
    return (
      <SignUp
        onSignedUp={handleSignedUp}
        onGoToSignIn={() => setView("signin")}
      />
    );
  }

  return (
    <SignIn
      onSignedIn={handleSignedIn}
      onGoToSignUp={() => setView("signup")}
    />
  );
}
