import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './RegistrationPage.css';

function RegistrationPage() {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [group, setGroup] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [errors, setErrors] = useState({});
  const [apiErrorMessage, setApiErrorMessage] = useState('');  // State for API error message
  const baseuri = process.env.REACT_APP_BACKEND_SERVER_URL;

  function validateForm() {
    let formErrors = {};
    if (!username) formErrors.username = 'Username is required';
    if (!firstName) formErrors.firstName = 'First name is required';
    if (!lastName) formErrors.lastName = 'Last name is required';
    if (!group) formErrors.group = 'Group is required';
    if (!password) formErrors.password = 'Password is required';
    if (!confirmPassword) formErrors.confirmPassword = 'Confirm password is required';
    if (password && confirmPassword && password !== confirmPassword) {
      formErrors.confirmPassword = 'Passwords do not match';
    }
    setErrors(formErrors);
    return Object.keys(formErrors).length === 0; // returns true if no errors
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setApiErrorMessage(''); // Reset the API error message before submitting

    if (!validateForm()) {
      return;
    }

    try {
      const res = await axios.post(baseuri + `/register`, {
        username: username,
        password: password,
        confirm_password: confirmPassword,
        group: group,
        first_name: firstName,
        last_name: lastName,
      });

      alert('Registration successful! Please login.');
      navigate('/login');
    } catch (err) {
      // Set the API error message from the response
      const errorMsg = err.response?.data?.response || 'Registration failed. Please try again.';
      setApiErrorMessage(errorMsg);
    }
  }

  return (
    <div className="registrationpage">
      <h1>Register for PoA iFreightOps Hub</h1>
      {apiErrorMessage && <div className="api-error-message">{apiErrorMessage}</div>}
      <form className="registration-form" onSubmit={handleSubmit}>
        <label className="registration-label">
          Username:
          <input className="registration-input" type="text" value={username} onChange={(e) => setUsername(e.target.value)} />
          {errors.username && <p className="error-message">{errors.username}</p>}
        </label>
        <label className="registration-label">
          First Name:
          <input className="registration-input" type="text" value={firstName} onChange={(e) => setFirstName(e.target.value)} />
          {errors.firstName && <p className="error-message">{errors.firstName}</p>}
        </label>
        <label className="registration-label">
          Last Name:
          <input className="registration-input" type="text" value={lastName} onChange={(e) => setLastName(e.target.value)} />
          {errors.lastName && <p className="error-message">{errors.lastName}</p>}
        </label>
        <label className="registration-label">
          Group:
          <select className="registration-input" value={group} onChange={(e) => setGroup(e.target.value)}>
            <option value="">Select Group</option>
            <option value="admin">Admin</option>
            <option value="non-admin">Non-Admin</option>
          </select>
          {errors.group && <p className="error-message">{errors.group}</p>}
        </label>
        <label className="registration-label">
          Password:
          <input className="registration-input" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          {errors.password && <p className="error-message">{errors.password}</p>}
        </label>
        <label className="registration-label">
          Confirm Password:
          <input className="registration-input" type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} />
          {errors.confirmPassword && <p className="error-message">{errors.confirmPassword}</p>}
        </label>
        <div className="action-buttons">
          <button className="register-button" type="submit">Register</button>
          <button className="login-button" type="button" onClick={() => navigate('/login')}>Login</button>
        </div>
      </form>
    </div>
  );
}

export default RegistrationPage;
