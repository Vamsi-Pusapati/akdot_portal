import React, { useState } from 'react'
import { Route, Routes, Navigate } from 'react-router-dom'
import HomePage from './components/HomePage/HomePage.js'
import LoginPage from './components/LoginPage/LoginPage.js'
import RegistrationPage from './components/RegisterPage/RegistrationPage.js'
function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  return (
    <div className="App">
      <Routes>
        <Route path="/homepage" element={<HomePage />} />
        <Route path="/loginpage" element={<LoginPage />} />
        <Route path="/register" element={<RegistrationPage />} />
        <Route path="/*" element={<Navigate to="/homepage" />} />
      </Routes>
      <header className="App-header">
      </header>
    </div>
    // <BrowserRouter>
    //   <Switch>
    //     <Route path="/" exact component={LandingPage} />
    //     <Route path="/loginpage" exact component={LoginPage} />
    //   </Switch>
    // </BrowserRouter>
  );
}

export default App;
