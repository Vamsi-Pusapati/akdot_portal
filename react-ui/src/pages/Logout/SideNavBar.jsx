import React from 'react';
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import './SideNav.css'; // Import the CSS file

const drawerWidth = 240;

function SideNav() {
  return (
    <Drawer
      sx={{
        width: drawerWidth,
        marginTop: 88 ,  
      }}
      variant="permanent"
      classes={{
        paper: 'drawer', // Apply the 'drawer' class from CSS
      }}
    >
      <List>
        <ListItem button className="list-item dashboard-item">
          <ListItemText primary="Dashboard" className="list-item-text" />
        </ListItem>
        <ListItem button className="list-item map-item">
          <ListItemText primary="Navigation" className="list-item-text" />
        </ListItem>
        <ListItem button className="list-item map-item">
          <ListItemText primary="Route Updates" className="list-item-text" />
        </ListItem>
        <ListItem button className="list-item map-item">
          <ListItemText primary="Simulations" className="list-item-text" />
        </ListItem>
        <ListItem button className="list-item settings-item">
          <ListItemText primary="Settings" className="list-item-text" />
        </ListItem>
        <ListItem button className="list-item settings-item">
          <ListItemText primary="Communications" className="list-item-text" />
        </ListItem>
      </List>
    </Drawer>
  );
}

export default SideNav;
