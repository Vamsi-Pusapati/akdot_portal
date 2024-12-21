import * as React from "react";
import { AppBar, Toolbar, Typography, Button, IconButton } from "@mui/material";
import { useNavigate } from "react-router-dom";
import axios from "axios";

import { logo } from "../../data";


const logoStyle = {
  maxWidth: "50px",
  marginRight: "8px",
};

export default function ButtonAppBar({ setSelectedFilterr }) {
  const navigate = useNavigate();
  const baseuri = process.env.REACT_APP_BACKEND_SERVER_URL;
  const logoutFn = () => {
    const sessionToken =  localStorage.getItem('akdot_session_token');
    const username = localStorage.getItem('akdot_username');
    if (sessionToken) {
      axios
        .post(baseuri + "/logout", {
          headers: {
            "session-token": sessionToken,
          },
        })
        .then((response) => {
          if (response.status === 200) {
            localStorage.setItem('akdot_session_token', '');
            localStorage.setItem('akdot_username', '');

            console.log(1)
            navigate("/loginpage");
          } else {
            console.error("Logout failed");
            navigate("/loginpage");
          }
        })
        .catch((error) => {
          console.error("Error during logout:", error);
          navigate("/loginpage"); 
        });
        localStorage.removeItem('akdot_session_token')
        localStorage.removeItem('akdot_username')
        
    } else {
      console.error("No session token found");
    }
  };

  return (
    <AppBar position="fixed">
      <Toolbar>
        <IconButton
          edge="start"
          color="inherit"
          aria-label="menu"
          sx={{ mr: 2 }}
        >
          <img src={logo} alt="AKDOT Logo" style={logoStyle} />
        </IconButton>
        <Typography
          variant="h6"
          component="div"
          sx={{
            flexGrow: 1,
            fontFamily: "monospace",
            fontWeight: 700,
            letterSpacing: ".2rem",
          }}
        >
          Alaska Department of Transport
        </Typography>
        <Typography component="div" sx={{ margin: 4 }}>
          Admin
        </Typography>
        <Button
          color="error"
          variant="contained"
          onClick={logoutFn}
          // sx={{ height: 50, marginTop: 3 }}
        >
          Logout
        </Button>
      </Toolbar>
    </AppBar>
  );
}
