import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './IncidentAlerts.css'; // Ensure this CSS file is created

const IncidentAlerts = () => {
  const [incidents, setIncidents] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const baseuri = process.env.REACT_APP_BACKEND_SERVER_URL;
  useEffect(() => {
    const fetchIncidents = async () => {
      try {
        const response = await axios.get(baseuri + '/incident_alerts');
        setIncidents(response.data);
        setIsLoading(false);
      } catch (error) {
        setError(error);
        setIsLoading(false);
      }
    };

    fetchIncidents();
  }, []);

  const nextIncident = () => {
    if (currentIndex < incidents.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  const prevIncident = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  const currentIncident = incidents[currentIndex];

  const formatResolutionTime = (minutes) => {
    const days = Math.floor(minutes / 1440);
    const hours = Math.floor((minutes % 1440) / 60);
    const mins = minutes % 60;
    return `${days} Days ${hours} Hours ${mins} Minutes`;
  };

  return (
    <div className="incident-alerts-widget">
      <div className="incident-header">
        <h3>Name: {currentIncident.incidentName}</h3>
        <p>Start Date: {new Date(currentIncident.dateTime).toLocaleString()}</p>
      </div>
      <div className="incident-body">
        <p>Description: {currentIncident.description}</p>
        <p>Location: {currentIncident.incidentLocation}</p>
        <p>Alert Type: {currentIncident.incidentType}</p>
        <p>Expected Resolution Time: {formatResolutionTime(currentIncident.expectedResolutionTime)}</p>
      </div>
      <div className="incident-navigation">
        <button onClick={prevIncident} disabled={currentIndex === 0}>&lt; Previous</button>
        <button onClick={nextIncident} disabled={currentIndex === incidents.length - 1}>Next &gt;</button>
      </div>
    </div>
  );
};

export default IncidentAlerts;
