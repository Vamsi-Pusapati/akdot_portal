import './HomePage.css';
import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import ScenarioAnalysis from '../ScenarioAnalysis/ScenarioAnalysis';
import MainPage from '../MainPage/MainPage';
import Dashboard from '../Dashboard/Dashboard';
import Subscribe from '../Subscribe/Subscribe';
import IncidentMaintenance from '../IncidentMaintenance/IncidentMaintenance';

function HomePage() {
  const [user, setUser] = useState(null);
  const [userName, setUserName] = useState(null);
  const baseuri = process.env.REACT_APP_BACKEND_SERVER_URL;


  const location = useLocation();
  const [activeComponent, setActiveComponent] = useState('Main Page');
  const navigate = useNavigate();

  useEffect(() => {
    (async () => {
      try 
      {
        const session_token = localStorage.getItem('akdot_session_token');
        console.log('session_token  ' + session_token)
        const username = localStorage.getItem('akdot_username');
        setUserName(userName)
        const res = await fetch(baseuri + `/is_authenticated`, {
          headers: {
            "session-token": session_token
          }
        })
        setUser(res.data);
        if (res.status == 401) 
        {
          navigate('/loginpage');
        }
      }
      catch
      {
        navigate('/loginpage');
      }
    })();
  }, []); // Empty dependency array ensures this effect runs only once

  const handleLogout = () => {
    // Handle logout logic, e.g., clearing session storage and redirecting
    localStorage.removeItem('akdot_session_token');
    localStorage.removeItem('akdot_username');
    navigate('/loginpage');
  };


  return (
    <div className="homepage">
      <header className="header">
        <div className="component-name">{activeComponent || 'Welcome'}</div>
        <div className="user-section">
          <span className="login-name">{userName}</span>
          <button className="logout-button" onClick={handleLogout}>Logout</button>
        </div>
      </header>
      <nav className="nav-buttons">
        <button onClick={() => setActiveComponent('Main Page')}>Main Page</button>
        <button onClick={() => setActiveComponent('Dashboard')}>Dashboards</button>
        <button onClick={() => setActiveComponent('Incident & Maintenance')}>Incident & Maintenance</button>
        <button onClick={() => setActiveComponent('Scenario Analysis')}>Scenario Analysis</button>
        <button onClick={() => setActiveComponent('Subscribe')}>Subscribe</button>
      </nav>
      <main>
        {activeComponent === 'Scenario Analysis' && <ScenarioAnalysis />}
        {activeComponent === 'Main Page' && <MainPage setActiveComponent={setActiveComponent}/>}
        {activeComponent === 'Dashboard' && <Dashboard />}
        {activeComponent === 'Subscribe' && <Subscribe />}
        {activeComponent === 'Incident & Maintenance' && <IncidentMaintenance />}
      </main>
    </div>
  );

}



export default HomePage;

