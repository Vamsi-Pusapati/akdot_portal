import React, { useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

// Fix for missing marker icons
let DefaultIcon = L.icon({
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

L.Marker.prototype.options.icon = DefaultIcon;

function DashboardMapComponent() {
  // Center the map on Port of Anchorage
  const portAnchorageCoordinates = [61.230930704192794, -149.8833]; // Latitude and Longitude of Port of Anchorage
  const [markers, setMarkers] = useState([
    { lat: 61.22694444444445, lng: -149.89, description: "Ocean Dock Rd before turn into Marathon Terminal" },
    { lat: 61.22944444444445, lng: -149.89083333333332, description: "Ocean Dock Rd between turn into Marathon Terminal and turn into ABl" },
    { lat: 61.231388888888894, lng: -149.89055555555555, description: "Between turn into ABl and turn onto Roger Graves Rd" },
    { lat: 61.23222222222223, lng: -149.88916666666665, description: "Occurs along Anchorage Port Rd before turn onto Terminal Rd"},
    { lat: 61.233333333333334, lng: -149.88722222222222, description: "Start of Terminal Rd, opposite the Control Center"},
    { lat: 61.234722222222224, lng: -149.88055555555556, description: "Terminal Rd to the entrance of Tote yard"},
    { lat: 61.23555555555556, lng: -149.8875, description: "Anchorage Rd across from Petro Star and AFSC"},
    { lat: 61.23583333333333, lng: -149.8875, description: "Anchorage Rd from across Delta Western to across Matson yard"},
    { lat: 61.23027777777778, lng: -149.89694444444444, description: "Marathon Rd and south float access towards Matson yard"},
    
  ]);

  return (
    <MapContainer
      center={portAnchorageCoordinates}
      zoom={14.5}
      style={{ height: '60vh', width: '100vh' }}
      scrollWheelZoom={false} 
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      
      {markers.map((marker, index) => (
        <Marker key={index} position={[marker.lat, marker.lng]}>
          <Popup>
            {marker.description}
          </Popup>
        </Marker>
      ))}
      
    </MapContainer>
  );
}

export default DashboardMapComponent;
