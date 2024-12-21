import React, { useState, useEffect, useRef } from 'react';
import './IncidentMaintenance.css';
import mapImage from './poa.png'; // Make sure the path is correct
import accidentLogo from './accident.png';
import emergencyLogo from './emergency.png';
import equipmentLogo from './equipment.png';
import maintenanceLogo from './maintenance.png';
import routeLogo from './route.png';
import trafficLogo from './traffic.png';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import { Checkbox } from '@mui/material';
import ReactSpeedometer from 'react-d3-speedometer'
import { Tooltip } from 'react-tooltip';

import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

L.Marker.prototype.options.icon = DefaultIcon;

function LocationMarker({ onClick }) {
  useMapEvents({
    click(e) {
      onClick(e.latlng);
    },
  });

  return null;
}

function IncidentMaintenance() {
  // State for the form inputs and fetched data
  const [formData, setFormData] = useState({
    nameOfIncident: '',
    typeOfIncident: 'maintenance',
    dateTime: '',
    exactLocation: '',
    description: '',
    suggestions: '',
    severityLevel: 'High',
    recipients: '',
    attachments: [],
    affiliations: [],
    days:0,
    hours:0,
    minutes:0
  });
  const incidentTypeLogos = {
    maintenance: maintenanceLogo,
    emergency_response: emergencyLogo,
    equipment_breakdowns: equipmentLogo,
    accidents_and_collisions: accidentLogo,
    route_changes: routeLogo,
    traffic_congestion: trafficLogo
  };

  const [selectedFile, setSelectedFile] = useState(null);

  const [frequencyData, setFrequencyData] = useState({
    typeOfIncident:"maintenance",
    lastMonth:0,
    lastYear:0,
    total:0
  })
  const [resolutionTimeData, setResolutionTimeData] = useState({
    Low:"",
    Medium:"",
    High:""
  })

  

  let [needleValue, setNeedleValue ]= useState(0)

  const default_description = "As of the current update, all operations within the port are running normally without any reported incidents. All routes and logistics function within their expected routines."
  const default_suggestion = "•	Continue with regular port activities as scheduled. \n \
  •	Maintain routine checks and communication with port authorities. \n \
  •	Keep checking port news and announcements for any operational changes.\n •	Adhere to standard safety and operational protocols."

  const incidentData = {
    "maintenance": {
      description: "Scheduled maintenance activities on key transportation infrastructure are set to begin on [...], which may reduce capacity or alter schedules for routes leading to and from [...].",
      suggestions:"•	Plan for alternative shipping methods during the maintenance window. \n \
      •	Adjust logistical plans to accommodate longer transit times.\n \
      •	Keep in regular contact with infrastructure maintenance teams for updates.\n •	Seek to expedite operations before the commencement of maintenance work."
    },
    "emergency_response": {
      description: "An emergency has arisen at [...] due to [...], necessitating immediate response actions to ensure personnel safety and continuation of operations.",
      suggestions:"•	Avoid the area around [...] until the situation is resolved. \n\
      •	Follow emergency announcements and directives issued by port authorities. \n\
      •	Anticipate potential disruptions and communicate with your logistics provider for updates.\n\
      •	Ensure all personnel are accounted for and adhere to the emergency protocols."
    },
    "route_changes": {
      description: "Due to recent changes in operational procedures, as of [...], transportation routes within the port have been altered, affecting cargo movement especially along [...].",
      suggestions:"•	Review the new routing guidelines provided by the port authority.\n\
      •	Update your transportation plans to reflect the changes in routes.\n\
      •	Train drivers and logistical staff on the new procedures to ensure compliance.\n\
      •	Regularly check for updates in case of further changes or route optimizations."
    },
    "traffic_congestion": {
      description: "As of [...], significant traffic congestion has been reported at the port, particularly around the areas of [...], causing substantial delays in the transportation of goods.",
      suggestions:"•	Consider rescheduling pickups or deliveries to avoid peak congestion hours.\n\
      •	Utilize the designated bypass routes at [...] to circumvent congested areas.\n\
      •	Monitor port authority updates for real-time traffic conditions.\n\
      •	Collaborate with port officials to streamline cargo movement during peak times."
    },
    "equipment_breakdowns": {
      description: "An equipment failure involving a [...] has been reported on [...], impacting cargo handling operations and schedules at locations […]",
      suggestions:"•	Prepare for possible delays in cargo release and adjust schedules accordingly.\n\
      •	Investigate the availability of alternative equipment or manual handling options.\n\
      •	Prioritize repair and maintenance requests to minimize operational downtime.\n\
      •	Communicate with the port's operations team for status updates and estimated resolution times."
    },
    "accidents_and_collisions": {
      description: "On the date of [...], at [...], a vehicular accident occurred on the road at [...], leading to the blockage of pathways towards [...]. The incident is expected to disrupt regular traffic flow and operations.",
      suggestions:"•	Use alternative routes at [...] to reach your destinations. \n \
      •	Allow for additional travel time due to expected delays. \n \
      •	Stay updated with traffic reports for the latest information on road conditions.\n \
      •	Follow instructions from traffic management and onsite emergency personnel."
    }
  }

  const calculateTotalMinutes = () => {
    return formData.days * 24 * 60 + formData.hours * 60 + formData.minutes;
  };

  const displayResolutionTime = () => {
    const totalMinutes = calculateTotalMinutes();

    const formattedDays = Math.floor(totalMinutes / (24 * 60));
    const remainingMinutes = totalMinutes % (24 * 60);
    const formattedHours = Math.floor(remainingMinutes / 60);
    const formattedMinutes = remainingMinutes % 60;

    // Improved formatting: Ensure leading zeros for single-digit values
    const formattedTime =
      (formattedDays > 0 ? `${formattedDays} Day${formattedDays > 1 ? 's' : ''} ` : '') +
      (formattedHours > 0 ? `${formattedHours.toString().padStart(2, '0')} Hour${formattedHours > 1 ? 's' : ''} ` : '') +
      (formattedMinutes > 0 ? `${formattedMinutes.toString().padStart(2, '0')} Minute${formattedMinutes > 1 ? 's' : ''}` : '');

    return formattedTime;

  };

  const baseUrl = process.env.REACT_APP_BACKEND_SERVER_URL;

  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    const fetchUserRole = async () => {
      try {
        const username = localStorage.getItem('akdot_username'); 
        const response = await fetch(baseUrl + '/userdetails?username='+username);
        const data = await response.json();

        //console.log(data.response)

        if (response.ok && data.response.group === 'admin') {
          setIsAdmin(true); 
        } else {
          setIsAdmin(false); 
        }
      } catch (error) {
        console.error('Error fetching user role:', error);
        setIsAdmin(false); 
      }
    };

    fetchUserRole();
  }, []);



  const handleResolutionTimeChange = (event) => {
    const { name, value } = event.target;
    let parsedValue = parseInt(value, 10); // Ensure numeric input

    if (isNaN(parsedValue) || parsedValue < 0) {
      parsedValue = 0; // Prevent invalid input
    }

    switch (name) {
      case 'days':
        setFormData({ ...formData, [name]: parsedValue });
        break;
      case 'hours':
        setFormData({ ...formData, [name]: parsedValue });
        break;
      case 'minutes':
        setFormData({ ...formData, [name]: parsedValue });
        break;
      default:
        break;
    }
  };

  const handleTypeChange = (e) => {
    const selectedType = e.target.value;
    // Populate description and suggestions from incidentData
    const incidentDetails = incidentData[selectedType];
    setFormData({
      ...formData,
      typeOfIncident: selectedType,
      description: incidentDetails.description,
      suggestions: incidentDetails.suggestions
    });
    handleResolutionTime(selectedType);
  };

  const [historyData,  setHistoryData] = useState([]);
  const [selectedIncidentId, setSelectedIncidentId] = useState(null);

 
  

  const portAnchorageCoordinates = [61.2341, -149.8872]; // Latitude and Longitude of Port of Anchorage
  const [marker, setMarker] = useState();
  const mapRef = useRef(null);
  const imageRef = useRef(null);

  // Add state for storing natural dimensions of the image
  const [naturalSize, setNaturalSize] = useState({ width: 0, height: 0 });

 


  const handleMapClick = (latlng) => {
    console.log(latlng)
    setMarker(latlng);
  };
  
  const handleSeverity = (severity) => {
    let newValue;
    console.log(severity);
      switch (severity) {
        case 'High':
          newValue = 825;
          break;
        case 'Medium':
          newValue = 500;
          break;
        case 'Low':
          newValue = 175;
          break;
        default:
          newValue = 0;
      }
      setNeedleValue(newValue)
  }
  

  // Handlers for form input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
    
    if (name === 'severityLevel') {
      handleSeverity(value);
    }
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
  
    // Basic validation (optional)
    if (!file) {
      return; // No file selected
    }
  
    // Store the selected file in state
    setSelectedFile(file);
  };

  const handleAffiliationChange = (event) => {
    const { checked, name } = event.target;
    let updatedAffiliations = [...formData.affiliations];
    if (checked) {
      updatedAffiliations.push(name);
    } else {
      updatedAffiliations = updatedAffiliations.filter((affiliation) => affiliation !== name);
    }
    setFormData({ ...formData, affiliations: updatedAffiliations });
  };

  // Submit handler for creating a new record
  const handleSubmit = async (e) => {
    e.preventDefault();
    // Logic to post data to the server would go here
    console.log('Form data submitted:', formData);

    try {
      let requestBody = {}
      requestBody.incidentName = formData.nameOfIncident;
      requestBody.incidentType = formData.typeOfIncident;
      requestBody.dateTime = formData.dateTime;
      requestBody.exactLocation = formData.exactLocation;
      requestBody.description = formData.description
      requestBody.suggestions = formData.suggestions
      requestBody.severityLevel =formData.severityLevel
      requestBody.affiliations = formData.affiliations;
      requestBody.otherRecipients = formData.otherRecipients
      requestBody.expectedResolutionTime = calculateTotalMinutes()

      if(marker){
        console.log("marker:" +JSON.stringify(marker))
        let geolocation = {
          'latitude': marker.lat,
          'longitude': marker.lng
        }
        requestBody.geolocation = geolocation
      }
      console.log(requestBody)
      const response = await fetch (baseUrl + '/addincident', {
        method: "POST",
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      })
      if (response.status === 201){
        console.log("Added incident successfully!");
      }else {
        console.log("Added not added");
      }
    } catch (error) {
      console.log(error);
    }

    // Reset form after submit
    setFormData({
      nameOfIncident: '',
      typeOfIncident: 'maintenance',
      dateTime: '',
      exactLocation: '',
      description: '',
      suggestions: '',
      severityLevel: 'High',
      otherRecipients: '',
      attachments: [],
      affiliations: [],
      days: 0,
      hours: 0,
      minutes: 0,
    });
    //Fire API
  };

  // Function to reset the form
  const handleClear = () => {
    setFormData({
      nameOfIncident: '',
      typeOfIncident: 'maintenance',
      dateTime: '',
      exactLocation: '',
      description: '',
      suggestions: '',
      severityLevel: 'High',
      otherRecipients: '',
      affiliations:[],
      attachments: [],
      days: 0,
      hours: 0,
      minutes: 0,
    });
    setMarker(null);
    setSelectedIncidentId(null)
  };

  const handleUpdate = async(e) => {
    
    try {
      let requestBody = {}
      requestBody.incidentName = formData.nameOfIncident;
      requestBody.incidentType = formData.typeOfIncident;
      requestBody.dateTime = formData.dateTime;
      requestBody.exactLocation = formData.exactLocation;
      requestBody.description = formData.description
      requestBody.suggestions = formData.suggestions
      requestBody.severityLevel =formData.severityLevel
      requestBody.affiliations = formData.affiliations;
      requestBody.otherRecipients = formData.otherRecipients
      requestBody.expectedResolutionTime = calculateTotalMinutes()
      if(marker){
        console.log("marker:" +JSON.stringify(marker))
        let geolocation = {
          'latitude': marker.lat,
          'longitude': marker.lng
        }
        requestBody.geolocation = geolocation
      }
      const response = await fetch (baseUrl+'/incident/'+selectedIncidentId, {
        method: "PUT",
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });
      if (response.status === 200){
        console.log("Updated incident successfully!");
      }else {
        console.log("Recoed not updated");
      }
    } catch (error) {
      console.log(error);
    }
  }

  const handleClose = async(e) => {
    
    try {
      const response = await fetch (baseUrl+'/closeincident/'+selectedIncidentId, {
        method: "PUT",
        headers: {
          'Content-Type': 'application/json',
        },
      });
      if (response.status === 200){
        console.log("Closed incident successfully!");
        handleClear()
        handleHistory()
      }else {
        console.log("Incident not closed");
      }
    } catch (error) {
      console.log(error);
    }
  };

  const handleHistory = async(e) =>{
    
    try{
      let incidentsUrl = baseUrl + '/getincidents'
      const response = await fetch(incidentsUrl, {
        method: "GET",
        headers: {"Content-Type": "application/json"}
      });
      if (response.ok) {
        const incidentData = await response.json();
  
        // Update UI with incident data
        setHistoryData(incidentData); // Assuming you have a state variable for history data
      } else {
        console.error("Failed to fetch incidents:", response.statusText);
      }

    }catch (error) {
      console.log(error);
    }
  
  }

  const handleIncidentFrequency = async(e) => {
    e.preventDefault();
    try{
      let inc_type= e.target.value
      frequencyData.typeOfIncident = inc_type
      if(""  !== inc_type){
        let inc_freq_url = baseUrl+'/getfrequency/'+inc_type
        const response = await fetch( inc_freq_url, {
          method:"GET",
          headers: {"Content-Type": "application/json"}
        })
        if(response.ok){
          const freq_data = await response.json();

          setFrequencyData({
            ...freq_data,
            typeOfIncident: inc_type,
            lastMonth:freq_data.last_month,
            lastYear: freq_data.last_year,
            total : freq_data.total
          });
          
        }
      }
      
    } catch (error) {
      console.log(error)
    }
    }

  const handleResolutionTime = async(incidentType) => {
    try{
      if( incidentType !== null || incidentType !==""){
        let resolution_Url = baseUrl + '/getresloutiontime/' + incidentType
        const response = await fetch(resolution_Url, {
          method:"GET",
          headers:{"Content-Type":"application/json"},
        })
        if(response.ok){
          const reso_data = await response.json();
          console.log('reso data',reso_data);
          setResolutionTimeData({
            ...reso_data,
            Low:reso_data.low,
            Medium:reso_data.medium,
            High:reso_data.high
          });
      }
      }
    }catch (error) {
      console.log(error);
    }
  }

  const handleIncidentDetails = async(incidentId) => {
    setSelectedIncidentId(incidentId);
    try{
      let incidentDetailsUrl = baseUrl + '/incident/' +incidentId
      const response = await fetch(incidentDetailsUrl, {
        method: "GET",
        headers: { 'Content-Type': 'application/json'}
      });
      if (response.ok) {
        const incidentDetails = await response.json();

        // Update form and marker data based on response
        let formattedDays = 0;
        let formattedHours = 0;
        let formattedMinutes = 0;
        if(null !== incidentDetails.expectedResolutionTime){
          let totalMinutes = incidentDetails.expectedResolutionTime
          formattedDays = Math.floor(totalMinutes / (24 * 60));
          let remainingMinutes = totalMinutes % (24 * 60);
          formattedHours = Math.floor(remainingMinutes / 60);
          formattedMinutes = remainingMinutes % 60;
        }
        setFormData({
          nameOfIncident: incidentDetails.incidentName,
          typeOfIncident: incidentDetails.incidentType,
          dateTime: incidentDetails.dateTime,
          exactLocation: incidentDetails.exactLocation,
          description: incidentDetails.description,
          suggestions: incidentDetails.suggestions,
          severityLevel: incidentDetails.severityLevel,
          affiliations:  incidentDetails.affiliations,
          otherRecipients: incidentDetails.otherRecipients,
          days: formattedDays,
          hours: formattedHours,
          minutes: formattedMinutes,
        });
        

        handleSeverity(incidentDetails.severityLevel)

        if (incidentDetails.geolocation) {
          setMarker({
            lng: incidentDetails.geolocation.longitude,
            lat: incidentDetails.geolocation.latitude,
          });
        } else {
          setMarker(null);
        }
        handleResolutionTime(incidentDetails.incidentType)
      } else {
        console.error(response.statusText);
      }
    }catch(error){

    }

  }

  const renderHistory = () => {
    return (
      <table>
        <thead>
          <tr>
            <th>Incident Name</th>
            <th>Date Time</th>
          </tr>
        </thead>
        <tbody>
          {historyData.map((incident) => (
            <tr key={incident.uid}>
              <td>{incident.incidentName}</td>
              <td>{incident.dateTime}</td>
              <td>
                <button onClick={() => handleIncidentDetails(incident.uid)}>Details</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    );
  };

    

  return (
    <div className="incident-maintenance-container">
      <div className="left-panel-im">
        <div className="form-section">
          {/* Conditionally render the form only if the user is an admin */}
          {isAdmin ? (
            <>
              <div>
                {selectedIncidentId == null ? (
                  <h3 className="h3-im-header">Create New Incident
                    <a data-tooltip-id="aboutTipCreateIncident" data-tooltip-content="Fill out the details of any new incident, including type, location, severity, and resolution time. You can also specify affiliations and add attachments for additional context. Incident refers to any unexpected event that disrupts normal operations at the port, such as maintenance, roadblocks, or vehicle breakdowns."
                      className="tooltip-circle">?</a>
                    <Tooltip id="aboutTipCreateIncident" place="top" effect="solid" className="custom-tooltip" />
                  </h3>
                ) : (
                  <h3 className="h3-im-header">Update Incident</h3>
                )}
              </div>
  
              <form onSubmit={handleSubmit}>
                <div className="form-field">
                  <label htmlFor="nameOfIncident">Name of Incident
                    <a data-tooltip-id="aboutTipNameOfIncident" data-tooltip-content="Enter a name or title for the incident to easily identify it later."
                      className="tooltip-circle">?</a>
                    <Tooltip id="aboutTipNameOfIncident" place="top" effect="solid" className="custom-tooltip" />
                  </label>
                  <input
                    id="nameOfIncident"
                    name="nameOfIncident"
                    type="text"
                    value={formData.nameOfIncident}
                    onChange={handleInputChange}
                  />
                </div>
  
                <div className="form-field">
                  <label htmlFor="typeOfIncident">Type of Incident
                    <a data-tooltip-id="aboutTipTypeOfIncident" data-tooltip-content="Select the type of incident from the available options (e.g., maintenance, roadblock, breakdown, etc.)."
                      className="tooltip-circle">?</a>
                    <Tooltip id="aboutTipTypeOfIncident" place="top" effect="solid" className="custom-tooltip" />
                  </label>
                  <select
                    id="typeOfIncident"
                    name="typeOfIncident"
                    value={formData.typeOfIncident}
                    onChange={handleTypeChange}
                  >
                    <option value="maintenance">Maintenance</option>
                    <option value="emergency_response">Emergency Response</option>
                    <option value="route_changes">Route Changes</option>
                    <option value="traffic_congestion">Traffic Congestion</option>
                    <option value="equipment_breakdowns">Equipment Breakdowns</option>
                    <option value="accidents_and_collisions">Accidents and Collisions</option>
                  </select>
                </div>
  
                <div className="form-field">
                  <label htmlFor="dateTime">Date and Time
                    <a data-tooltip-id="aboutTipDateTime" data-tooltip-content="Specify the exact date and time when the incident occurred."
                      className="tooltip-circle">?</a>
                    <Tooltip id="aboutTipDateTime" place="top" effect="solid" className="custom-tooltip" />
                  </label>
                  <input
                    id="dateTime"
                    name="dateTime"
                    type="datetime-local"
                    value={formData.dateTime}
                    onChange={handleInputChange}
                  />
                </div>
  
                <div className="form-field">
                  <label htmlFor="exactLocation">Exact Location
                    <a data-tooltip-id="aboutTipExactLocation" data-tooltip-content="Provide the exact location where the incident took place."
                      className="tooltip-circle">?</a>
                    <Tooltip id="aboutTipExactLocation" place="top" effect="solid" className="custom-tooltip" />
                  </label>
                  <input
                    id="exactLocation"
                    name="exactLocation"
                    type="text"
                    value={formData.exactLocation}
                    onChange={handleInputChange}
                  />
                </div>
  
                <div className="form-field">
                  <label htmlFor="description">Description
                    <a data-tooltip-id="aboutTipDescription" data-tooltip-content="Enter a detailed description of the incident."
                      className="tooltip-circle">?</a>
                    <Tooltip id="aboutTipDescription" place="top" effect="solid" className="custom-tooltip" />
                  </label>
                  <textarea
                    id="description"
                    name="description"
                    value={formData.description}
                    onChange={handleInputChange}
                  ></textarea>
                </div>
  
                <div className="form-field">
                  <label htmlFor="suggestions">Suggestions
                    <a data-tooltip-id="aboutTipSuggestions" data-tooltip-content="Enter any suggestions for resolving the incident or improving the situation."
                      className="tooltip-circle">?</a>
                    <Tooltip id="aboutTipSuggestions" place="top" effect="solid" className="custom-tooltip" />
                  </label>
                  <textarea
                    id="suggestions"
                    name="suggestions"
                    value={formData.suggestions}
                    onChange={handleInputChange}
                  ></textarea>
                </div>
  
                <div className="form-field">
                  <label htmlFor="severityLevel">Severity Level
                    <a data-tooltip-id="aboutTipSeverityLevel" data-tooltip-content="Select the severity level of the incident."
                      className="tooltip-circle">?</a>
                    <Tooltip id="aboutTipSeverityLevel" place="top" effect="solid" className="custom-tooltip" />
                  </label>
                  <select
                    id="severityLevel"
                    name="severityLevel"
                    value={formData.severityLevel}
                    onChange={handleInputChange}
                  >
                    <option value="High">High</option>
                    <option value="Medium">Medium</option>
                    <option value="Low">Low</option>
                  </select>
                </div>
  
                <div className='form-field'>
                  <label htmlFor='affiliations'>Affiliations
                    <a data-tooltip-id="aboutTipAffiliations" data-tooltip-content="Check the boxes to indicate which groups are involved."
                      className="tooltip-circle">?</a>
                    <Tooltip id="aboutTipAffiliations" place="top" effect="solid" className="custom-tooltip" />
                  </label>
                  <div style={{ display: 'grid', gridTemplateColumns: 'auto 1fr' }}>
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                      <Checkbox
                        name="trucking_companies"
                        checked={formData.affiliations.includes('trucking_companies')}
                        onChange={handleAffiliationChange}
                      />
                      <label htmlFor="trucking_companies">Trucking Companies</label>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                      <Checkbox
                        name="shipping_carriers"
                        checked={formData.affiliations.includes('shipping_carriers')}
                        onChange={handleAffiliationChange}
                      />
                      <label htmlFor="shipping_carriers">Shipping Carriers</label>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                      <Checkbox
                        name="port_staff"
                        checked={formData.affiliations.includes('port_staff')}
                        onChange={handleAffiliationChange}
                      />
                      <label htmlFor="port_staff">Port Staff</label>
                    </div>
                  </div>
                </div>
  
                <div className="form-field">
                  <label htmlFor="otherRecipients">Other Recipients:
                    <a data-tooltip-id="aboutTipOtherRecipients" data-tooltip-content="Add any other individuals or groups who should be notified."
                      className="tooltip-circle">?</a>
                    <Tooltip id="aboutTipOtherRecipients" place="top" effect="solid" className="custom-tooltip" />
                  </label>
                  <input
                    id="otherRecipients"
                    name="otherRecipients"
                    type="text"
                    value={formData.otherRecipients}
                    onChange={handleInputChange}
                  />
                </div>
  
                <div>
                  <p>Estimated Resolution Time:
                    <a data-tooltip-id="aboutTipResolutionTime" data-tooltip-content="Provide an estimate for how long it will take to resolve the incident."
                      className="tooltip-circle">?</a>
                    <Tooltip id="aboutTipResolutionTime" place="top" effect="solid" className="custom-tooltip" />
                  </p>
                  <label htmlFor="days">Days:</label>
                  <input
                    type="number"
                    id="days"
                    name="days"
                    value={formData.days}
                    onChange={handleResolutionTimeChange}
                    min={0}
                  />
                  <label htmlFor="hours">Hours:</label>
                  <input
                    type="number"
                    id="hours"
                    name="hours"
                    value={formData.hours}
                    onChange={handleResolutionTimeChange}
                    min={0}
                  />
                  <label htmlFor="minutes">Minutes:</label>
                  <input
                    type="number"
                    id="minutes"
                    name="minutes"
                    value={formData.minutes}
                    onChange={handleResolutionTimeChange}
                    min={0}
                  />
                </div>
  
                <div className="form-field">
                  <label htmlFor="attachments">Attachments
                    <a data-tooltip-id="aboutTipAttachments" data-tooltip-content="Upload any relevant files or documents that can help in understanding or resolving the incident."
                      className="tooltip-circle">?</a>
                    <Tooltip id="aboutTipAttachments" place="top" effect="solid" className="custom-tooltip" />
                  </label>
                  <input
                    id="attachments"
                    name="attachments"
                    type="file"
                    multiple
                    onChange={handleFileChange}
                  />
                </div>
  
                <div className="form-actions">
                  {selectedIncidentId == null ? (
                    <button className="im-buttons-inside" type="submit"><h3 className="im-h3-font">Create Incident</h3></button>
                  ) : (
                    <>
                      <button className="im-buttons-inside" onClick={(e) => {
                        if (window.confirm('Are you sure you want to update the incident?')) {
                          handleUpdate();
                        }
                        e.preventDefault();
                      }}><h3 className="im-h3-font">Update Incident</h3></button>
                      <button className="im-buttons-inside" onClick={(e) => {
                        if (window.confirm('Are you sure you want to close the incident?')) {
                          handleClose();
                        }
                        e.preventDefault();
                      }}><h3 className="im-h3-font">Close Incident</h3></button>
                    </>
                  )}
                  <button className="im-buttons-inside" type="button" onClick={handleClear}><h3 className="im-h3-font">Clear Details</h3></button>
                </div>
              </form>
            </>
          ) : (
            <div>
              <h3 className="h3-im-header">You do not have permission to create or update incidents.</h3>
            </div>
          )}
        </div>
      </div>
  
      {/* Rest of the content */}
      <div className="im-center-panel">
        <div className="map-container" style={{ position: 'relative' }}>
          <MapContainer
            center={portAnchorageCoordinates}
            zoom={14.5}
            style={{ height: '60vh', width: '100vh' }}
            scrollWheelZoom={false}
          >
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
            {marker && marker.lat && marker.lng && (
              <Marker position={marker}>
                <Popup>
                  Coordinates: {marker.lat.toFixed(4)}, {marker.lng.toFixed(4)}
                </Popup>
              </Marker>
            )}
            <LocationMarker onClick={handleMapClick} />
          </MapContainer>
        </div>
  
        <div className="description-box">
          <h3 className="h3-im-header">Description</h3>
          <p>
            {formData.description
              ? formData.description.split("\n").map((line, index) => (
                <React.Fragment key={index}>
                  {line}<br />
                </React.Fragment>
              ))
              : default_description.split("\n").map((line, index) => (
                <React.Fragment key={index}>
                  {line}<br />
                </React.Fragment>
              ))}
          </p>
        </div>
  
        <div className="suggestions-box">
          <h3 className="h3-im-header">Suggestions</h3>
          <p>
            {formData.suggestions
              ? formData.suggestions.split("\n").map((line, index) => (
                <React.Fragment key={index}>
                  {line.startsWith('•') ? <span>&bull; {line.substring(1)}</span> : line}<br />
                </React.Fragment>
              ))
              : default_suggestion.split("\n").map((line, index) => (
                <React.Fragment key={index}>
                  {line.startsWith('•') ? <span>&bull; {line.substring(1)}</span> : line}<br />
                </React.Fragment>
              ))}
          </p>
        </div>
      </div>
  
      <div className="right-panel-im">
        <div className="history-section">
          <h3 className="h3-im-header">Open Incidents</h3>
          <button onClick={handleHistory}>Show Open Incidents</button>
          {historyData.length > 0 && renderHistory()}
        </div>
  
        <div className="frequency-section">
          <h3 className="h3-im-header">Frequency Per Incident Type</h3>
          <div className="frequency-section-inner" style={{ display: 'flex', alignItems: 'center' }}>
            <div style={{ flexGrow: 1 }}>
              <select
                id="incidentFrequency"
                name="incidentFrequency"
                value={frequencyData.typeOfIncident}
                onChange={handleIncidentFrequency}
              >
                <option value="maintenance">Maintenance</option>
                <option value="emergency_response">Emergency Response</option>
                <option value="route_changes">Route Changes</option>
                <option value="traffic_congestion">Traffic Congestion</option>
                <option value="equipment_breakdowns">Equipment Breakdowns</option>
                <option value="accidents_and_collisions">Accidents and Collisions</option>
              </select>
              <p>Last Month: {frequencyData.lastMonth}</p>
              <p>Last Year: {frequencyData.lastYear}</p>
              <p>Total: {frequencyData.total}</p>
            </div>
            <img
              src={incidentTypeLogos[frequencyData.typeOfIncident]}
              alt="Incident Type Logo"
              style={{ marginTop: '5px', width: '100px', height: '100px' }}
            />
          </div>
        </div>
  
        <div className="expected-resolution-time">
          <h3 className="h3-im-header">Expected Resolution Time</h3>
          <h3>{displayResolutionTime()}</h3>
        </div>
  
        <div className="severity">
          <h3 className="h3-im-header">Severity</h3>
          <ReactSpeedometer
            width={500}
            customSegmentStops={[0, 333, 666, 1000]}
            segmentColors={['limegreen', 'gold', 'red']}
            needleHeightRatio={0.8}
            value={needleValue}
            currentValueText="Severity Level"
            customSegmentLabels={[
              { text: 'LOW', position: 'INSIDE', color: '#555' },
              { text: 'MEDIUM', position: 'INSIDE', color: '#555' },
              { text: 'HIGH', position: 'INSIDE', color: '#555' },
            ]}
            ringWidth={47}
            needleTransitionDuration={3333}
            needleTransition="easeElastic"
            needleColor={'#555'}
            textColor={'#555'}
          />
        </div>
      </div>
    </div>
  );
  
}

export default IncidentMaintenance;
