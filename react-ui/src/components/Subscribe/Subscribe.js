import './Subscribe.css';
import React, { useState } from 'react';
import { Tooltip } from 'react-tooltip'; // Make sure you import react-tooltip

function Subscribe() {
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    mobile: '',
    company: '',
    jobTitle: '',
    communication: '',
    consent: false
  });
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [popupMessage, setPopupMessage] = useState('');
  const [popupColor, setPopupColor] = useState(''); 
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prevFormData => ({
      ...prevFormData,
      [name]: type === 'checkbox' ? checked : value
    }));
  };
  const clearForm = () => {
    setFormData({
      fullName: '',
      email: '',
      mobile: '',
      company: '',
      jobTitle: '',
      communication: '',
      affiliation:'',
    });
  };

  const handleSubmit = async (e) => {
    const baseUrl = process.env.REACT_APP_BACKEND_SERVER_URL;
    const subscribeUrl = baseUrl + '/subscribe';
    e.preventDefault();
    console.log('Form Data:', formData);

    try {
      const response = await fetch(subscribeUrl, {
        method: "POST",
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const data = await response.json();
        console.log(data);

        setIsSubscribed(true);
        setPopupMessage('Subscription successful!');
        setPopupColor('green');
        clearForm();
      } else {
        const error = new Error(`Error: ${response.statusText}`);
        console.error(error);

        setIsSubscribed(true);
        setPopupMessage('An error occurred. Please try again later.');
        setPopupColor('red');
      }

    } catch (error) {
      console.error("error while subscribing", error);
      setIsSubscribed(true);
      setPopupMessage('There seems to be a connection issue. Please try again later.');
      setPopupColor('red');
    }
  };

  return (
    <div className="subscribe">
      <form className="subscribe-form" onSubmit={handleSubmit}>
        <div className="form-row">
          <label htmlFor="fullName">Full Name:
            <a data-tooltip-id="aboutTipFullName" data-tooltip-content="Enter your complete name as it will be used for identification and communication purposes." className="tooltip-circle">?</a>
            <Tooltip id="aboutTipFullName" place="top" effect="solid" className="custom-tooltip" />
          </label>
          <input type="text" id="fullName" name="fullName" value={formData.fullName} onChange={handleChange} />
        </div>

        <div className="form-row">
          <label htmlFor="email">Email Address:
            <a data-tooltip-id="aboutTipEmail" data-tooltip-content="Provide a valid email address to receive updates and information related to port activities." className="tooltip-circle">?</a>
            <Tooltip id="aboutTipEmail" place="top" effect="solid" className="custom-tooltip" />
          </label>
          <input type="email" id="email" name="email" value={formData.email} onChange={handleChange} />
        </div>

        <div className="form-row">
          <label htmlFor="mobile">Mobile Number:
            <a data-tooltip-id="aboutTipMobile" data-tooltip-content="Enter your mobile phone number to receive SMS notifications about incidents and updates." className="tooltip-circle">?</a>
            <Tooltip id="aboutTipMobile" place="top" effect="solid" className="custom-tooltip" />
          </label>
          <input type="tel" id="mobile" name="mobile" value={formData.mobile} onChange={handleChange} />
        </div>

        <div className="form-row">
          <label htmlFor="company">Company Name:
            <a data-tooltip-id="aboutTipCompany" data-tooltip-content="Provide the name of the company you represent, if applicable." className="tooltip-circle">?</a>
            <Tooltip id="aboutTipCompany" place="top" effect="solid" className="custom-tooltip" />
          </label>
          <input type="text" id="company" name="company" value={formData.company} onChange={handleChange} />
        </div>

        <div className="form-row">
          <label htmlFor="jobTitle">Job Title/Position:
            <a data-tooltip-id="aboutTipJobTitle" data-tooltip-content="Enter your current job title or position within your organization." className="tooltip-circle">?</a>
            <Tooltip id="aboutTipJobTitle" place="top" effect="solid" className="custom-tooltip" />
          </label>
          <input type="text" id="jobTitle" name="jobTitle" value={formData.jobTitle} onChange={handleChange} />
        </div>

        <div className="form-row">
          <label htmlFor="affiliation">Affiliation:
            <a data-tooltip-id="aboutTipAffiliation" data-tooltip-content="Select the group or organization you are affiliated with, such as port staff, shipping carriers, or trucking companies." className="tooltip-circle">?</a>
            <Tooltip id="aboutTipAffiliation" place="top" effect="solid" className="custom-tooltip" />
          </label>
          <select id="affiliation" name="affiliation" value={formData.affiliation} onChange={handleChange}>
            <option value="">Select...</option>
            <option value="trucking_companies">Trucking companies</option>
            <option value="shipping_carriers">Shipping Carriers</option>
            <option value="port_staff">Port staff</option>
          </select>
        </div>

        <div className="form-row">
          <label htmlFor="communication">Preferred Method of Communication:
            <a data-tooltip-id="aboutTipCommunication" data-tooltip-content="Choose your preferred communication method (email, SMS, or both) for receiving updates and alerts." className="tooltip-circle">?</a>
            <Tooltip id="aboutTipCommunication" place="top" effect="solid" className="custom-tooltip" />
          </label>
          <select id="communication" name="communication" value={formData.communication} onChange={handleChange}>
            <option value="">Choose...</option>
            <option value="Email">Email</option>
            <option value="Text">Text Message</option>
          </select>
        </div>

        <div className="form-row2 checkbox-row">
          <input type="checkbox" id="consent" name="consent" checked={formData.consent} onChange={handleChange} />
          <label htmlFor="consent">
            I agree to receive communications about port-related incidents, maintenance updates, and other relevant information from Port of Alaska via email and/or SMS. I understand that I can unsubscribe at any time.
          </label>
        </div>

        <button type="submit" className="submit-button">Submit</button>
        {isSubscribed && (
        <div>
          <div className="popup" style={{ color: popupColor }}> 
            <h4>{popupMessage}</h4>
          </div>
        </div>
        )}
      </form>      
    </div>
  );
}

export default Subscribe;
