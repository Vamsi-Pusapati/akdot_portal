import React, { useState } from "react";
import {
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText,
} from "@mui/material";

function Filter({ setSelectedFilterr }) {
  const [worthyData, setWorthyData] = useState("");
  const handleChange = ({ target }) => {
    setWorthyData(target.value);
    setSelectedFilterr(target.value);
  };
  return (
    <div>
      <FormControl sx={{ m: 1, minWidth: 120 }}>
        <InputLabel id="demo-simple-select-helper-label">
          Select Emails
        </InputLabel>
        <Select
          labelId="demo-simple-select-helper-label"
          id="demo-simple-select-helper"
          value={worthyData}
          label="Email"
          onChange={handleChange}
        >
          <MenuItem value="all">
            <em>All</em>
          </MenuItem>
          <MenuItem value={"Worthy"}>Worthy</MenuItem>
          <MenuItem value={"Not Worthy"}>UnWorthy</MenuItem>
          <MenuItem value={"UnSure"}>Notsure</MenuItem>
        </Select>
        <FormHelperText>Filter Email Worthiness</FormHelperText>
      </FormControl>
    </div>
  );
}

export default Filter;
