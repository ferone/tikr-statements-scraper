import React, { useEffect, useState } from 'react';
import { Box, Button, MenuItem, Select, TextField, IconButton, Grid } from '@mui/material';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import RemoveCircleOutlineIcon from '@mui/icons-material/RemoveCircleOutline';
import axios from 'axios';

const OPERATORS = [
  { label: '=', value: '=' },
  { label: '>', value: '>' },
  { label: '<', value: '<' },
  { label: '>=', value: '>=' },
  { label: '<=', value: '<=' },
  { label: 'contains', value: 'like' },
];

export default function QueryBuilder({ filters, setFilters, fields }) {
  // Add a new filter row
  const addFilter = () => {
    setFilters([...filters, { field: fields[0] || '', op: '=', value: '' }]);
  };
  // Remove a filter row
  const removeFilter = (idx) => {
    setFilters(filters.filter((_, i) => i !== idx));
  };
  // Update a filter row
  const updateFilter = (idx, key, value) => {
    const newFilters = [...filters];
    newFilters[idx][key] = value;
    setFilters(newFilters);
  };
  return (
    <Box sx={{ mb: 2 }}>
      <Grid container spacing={2} alignItems="center">
        {filters.map((f, idx) => (
          <React.Fragment key={idx}>
            <Grid item xs={3}>
              <Select
                value={f.field}
                onChange={e => updateFilter(idx, 'field', e.target.value)}
                fullWidth
                size="small"
              >
                {fields.map(field => (
                  <MenuItem key={field} value={field}>{field}</MenuItem>
                ))}
              </Select>
            </Grid>
            <Grid item xs={2}>
              <Select
                value={f.op}
                onChange={e => updateFilter(idx, 'op', e.target.value)}
                fullWidth
                size="small"
              >
                {OPERATORS.map(op => (
                  <MenuItem key={op.value} value={op.value}>{op.label}</MenuItem>
                ))}
              </Select>
            </Grid>
            <Grid item xs={5}>
              <TextField
                value={f.value}
                onChange={e => updateFilter(idx, 'value', e.target.value)}
                fullWidth
                size="small"
                placeholder="Value"
              />
            </Grid>
            <Grid item xs={2}>
              <IconButton onClick={() => removeFilter(idx)} color="error"><RemoveCircleOutlineIcon /></IconButton>
              {idx === filters.length - 1 && (
                <IconButton onClick={addFilter} color="primary"><AddCircleOutlineIcon /></IconButton>
              )}
            </Grid>
          </React.Fragment>
        ))}
      </Grid>
      {filters.length === 0 && (
        <Button onClick={addFilter} startIcon={<AddCircleOutlineIcon />} variant="outlined" sx={{ mt: 2 }}>Add Filter</Button>
      )}
    </Box>
  );
} 