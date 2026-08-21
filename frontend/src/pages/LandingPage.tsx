import { Link } from "react-router-dom";

const LandingPage = () => {
  return (
    <main>
      <h1>Landing Page</h1>
      <Link to="/chat">Open chat</Link>
    </main>
  );
};

export default LandingPage;
