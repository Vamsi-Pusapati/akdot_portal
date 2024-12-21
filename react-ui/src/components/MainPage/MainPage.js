import React, { useEffect, useState } from 'react';
import './MainPage.css';
import portpic from './portpic2.png';  
import infoIcon from './infoIcon.png'; 
import WeatherComponent from './WeatherComponent';
import IncidentAlerts from './IncidentAlerts'; 
import { Tooltip } from 'react-tooltip'

function MainPage({ setActiveComponent }) {
  const [date, setDate] = useState(new Date());
  const [totalExpectedCars, setTotalExpectedCars] = useState(0);
  const [totalExpectedTrucks, setTotalExpectedTrucks] = useState(0);
  const [expectedCarsSoFar, setExpectedCarsSoFar] = useState(0);
  const [expectedTrucksSoFar, setExpectedTrucksSoFar] = useState(0);


  const currentHour = new Date().getHours();

  const baseUrl = process.env.REACT_APP_BACKEND_SERVER_URL;

  useEffect(() => {
    const timer = setInterval(() => {
      setDate(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);


  useEffect(() => {
    // Fetch expected cars
    const fetchExpectedCars = async () => {
      try {
        const response = await fetch(baseUrl + '/dashboard/hourly_counts?vehicle=cars&day=0');
        if (!response.ok) {
          throw new Error('Failed to fetch data for cars');
        }
        const data = await response.json();
        
        if (data && data.Mean) { // Ensure data and Mean exist
          const totalCars = data.Mean.reduce((acc, curr) => acc + curr, 0); // Sum of all mean values for total cars
          const carsSoFar = data.Mean.slice(0, currentHour + 1).reduce((acc, curr) => acc + curr, 0); // Sum of mean values till current hour
          setTotalExpectedCars(totalCars);
          setExpectedCarsSoFar(carsSoFar);
        } else {
          console.error('Mean array is undefined or missing for cars');
        }
      } catch (error) {
        console.error('Error fetching expected cars:', error);
      }
    };
  
    // Fetch expected trucks
    const fetchExpectedTrucks = async () => {
      try {
        const response = await fetch(baseUrl+'/dashboard/hourly_counts?vehicle=trucks&day=0');
        if (!response.ok) {
          throw new Error('Failed to fetch data for trucks');
        }
        const data = await response.json();
        
        if (data && data.Mean) { // Ensure data and Mean exist
          const totalTrucks = data.Mean.reduce((acc, curr) => acc + curr, 0); // Sum of all mean values for total trucks
          const trucksSoFar = data.Mean.slice(0, currentHour + 1).reduce((acc, curr) => acc + curr, 0); // Sum of mean values till current hour
          setTotalExpectedTrucks(totalTrucks);
          setExpectedTrucksSoFar(trucksSoFar);
        } else {
          console.error('Mean array is undefined or missing for trucks');
        }
      } catch (error) {
        console.error('Error fetching expected trucks:', error);
      }
    };
  
    fetchExpectedCars();
    fetchExpectedTrucks();
  }, [currentHour]);

  const handleSubscribeClick = () => {
    setActiveComponent('Subscribe');
  };

  return (
    <div className="main-page">
      <div className="header-mainpage" style={{ backgroundImage: `url(${portpic})` }}>
        <div className="clock-and-date">
          <div className="clock">{date.toLocaleTimeString()}</div>
          <div className="date">{date.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</div>
        </div>
      </div>
      <div className="content">
        <div className="about section">
          <div className="header">
            About the Portal 
            <a data-tooltip-id="aboutTip" data-tooltip-content="Learn about the key features and functionalities of the portal, including real-time updates, optimization tools, and other resources to enhance operational efficiency."
               className="tooltip-circle">
               ?
            </a>
            <Tooltip id="aboutTip" place="top" effect="solid" className="custom-tooltip"/>
          </div>
          <div className="section-contents-mp">
            <img src={infoIcon} style={{ display: 'flex', alignItems: 'center', marginLeft: '42%' }} alt="Info Icon" />
            <p>Welcome to the portal for Alaska’s port operations. Key Features:</p>
            <ul>
              <li><b>Incident and Repair Updates:</b> Receive real-time notifications about port incidents and maintenance activities. Our system ensures that all relevant stakeholders are quickly informed of any operational disruptions or ongoing repairs.</li>
              <li><b>Container Operations Simulation:</b> Use our simulation tools to visualize container handling processes. This feature helps in planning and executing container movements more efficiently, reducing delays and improving overall port productivity.</li>
              <li><b>Traffic Dashboards:</b> Access detailed traffic dashboards that offer insights into vessel movements, dock occupancy, and general port traffic. These dashboards provide useful information to support decision-making and operational planning.</li>
              <li><b>Simulation-Based Route Optimization and Scheduling:</b> Plan optimal routing and scheduling for vessels using advanced simulation algorithms. This feature helps reduce congestion and improves the timeliness of operations.</li>
            </ul>
          </div>
        </div>
        <div className="weather section">
          <div className="header">Traffic In Port

          <a data-tooltip-id="aboutTip" data-tooltip-content="Displays the total expected trucks and cars for the day that provides data-driven projections to monitor traffic flow at the port. Data-driven projections are forecasts based on historical data to anticipate future events, such as traffic flow."
               className="tooltip-circle">
               ?
            </a>
            <Tooltip id="aboutTip" place="top" effect="solid" className="custom-tooltip"/>
          </div>
          <div className="today-in-port">
            <div className="stats-container">
              <div className="stat-item">
                <div className="stat-circle">{Math.round(totalExpectedTrucks)}</div>
                <span>Total Expected Trucks</span>
              </div>
              <div className="stat-item">
                <div className="stat-circle">{Math.round(totalExpectedCars)}</div>
                <span>Total Expected Cars</span>
              </div>
              <div className="stat-item">
                <div className="stat-circle">{Math.round(expectedTrucksSoFar)}</div>
                <span>Expected Trucks So Far</span>
              </div>
              <div className="stat-item">
                <div className="stat-circle">{Math.round(expectedCarsSoFar)}</div>
                <span>Expected Cars So Far</span>
              </div>
            </div>
          </div>
        </div>
        <div className="alerts section">
          <div className="header">Alerts
          <a data-tooltip-id="aboutTip" data-tooltip-content="Get important notifications about incidents, maintenance activities, and other critical updates that could impact port operations. Incidents refer to any unexpected event, such as roadblocks, breakdowns, or maintenance, that disrupt normal operations."
               className="tooltip-circle">
               ?
            </a>
            <Tooltip id="aboutTip" place="top" effect="solid" className="custom-tooltip"/>

          </div>
          <div className="section-contents-mp">
            <IncidentAlerts />
          </div>
        </div>
        <div className="useful-links section">
          <div className="header">Useful Links

          <a data-tooltip-id="aboutTip" data-tooltip-content="Quick access to important links related to port operations, including official websites and live traffic tracking."
               className="tooltip-circle">
               ?
            </a>
            <Tooltip id="aboutTip" place="top" effect="solid" className="custom-tooltip"/>
          </div>
          <div className="section-contents-mp">
            <ul>
              <li><a href="https://www.portofalaska.com/" target='_blank'>Port of Anchorage Official Site</a></li>
              <li><a href="https://511.alaska.gov/" target='_blank'>Alaska 511</a></li>
              <li><a href="https://www.muni.org/pages/default.aspx" target='_blank'>Municipality of Anchorage</a></li>
              <li><a href="https://dot.alaska.gov/amhs/index.shtml" target='_blank'>Alaska Marine Highway System</a></li>
              <li><a href="https://www.marinetraffic.com/" target='_blank'>Marine Traffic Global Ship Tracking</a></li>
            </ul>
            <div className=" subscribe-mp  section-contents-mp">
            <button onClick={handleSubscribeClick}>Subscribe</button>
          </div>
          </div>
        </div>
        <div className="subscribe-mp section">
          <div className="header">Weather Today
          <a data-tooltip-id="aboutTip" data-tooltip-content="Stay updated on current weather conditions at the port location, with temperature, wind speed, and humidity information to plan accordingly."
               className="tooltip-circle">
               ?
            </a>
            <Tooltip id="aboutTip" place="top" effect="solid" className="custom-tooltip"/>
          </div>
          <div className="section-contents-mp">
            <WeatherComponent />
          </div>
        </div>
      </div>
    </div>
  );
}

export default MainPage;
