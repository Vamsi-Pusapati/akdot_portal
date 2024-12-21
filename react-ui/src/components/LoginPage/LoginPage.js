import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom'; // Import Link for navigation
import './LoginPage.css';

function LoginPage({ onLogin }) {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [user, setUser] = useState(null);
  const baseuri = process.env.REACT_APP_BACKEND_SERVER_URL;

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(baseuri + `/is_authenticated`);
        setUser(res.data);
        if (res.status === 200) {
          navigate('/homepage');
          document.getElementsByClassName('App-header')[0].style.display = 'none';
        } else if (res.status === 401) {
          console.log("Not Authenticated");
        }
      } catch {
        console.log("Not Authenticated");
      }
    })();
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();

    try {
      const res = await axios.post(baseuri + `/login`, {
        username: username,
        password: password,
      });
      localStorage.setItem('akdot_session_token', res.data.response.session_token);
      localStorage.setItem('akdot_username', res.data.response.username);
      navigate('/homepage');
      document.getElementsByClassName('App-header')[0].style.display = 'none';
    } catch {
      setErrorMessage('Username or password is incorrect.');
    }
  }

  return (
    <div className="loginpage">
      <h1>Welcome to PoA iFreightOps Hub</h1>
      <form className="login-form" onSubmit={handleSubmit}>
        <label className="login-label">
          Username:
          <input className="login-input" type="text" value={username} onChange={(e) => setUsername(e.target.value)} />
        </label>
        <br />
        <label className="login-label">
          Password:
          <input className="login-input" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </label>
        <br />
        <button className="login-button" type="submit">Login</button>
      </form>
      {errorMessage && <p className="error-message">{errorMessage}</p>}
      
      {/* Add the Sign Up link */}
      <div className="signup-link">
        <p>Don't have an account? <Link to="/register">Sign Up</Link></p>
      </div>
    </div>
  );
}

export default LoginPage;
