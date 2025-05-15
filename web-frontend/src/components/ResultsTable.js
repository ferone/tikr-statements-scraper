import React from 'react';
import { Box, Typography, MenuItem, Select, FormControl, InputLabel, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';

/**
 * Component that displays the screener results in a table format
 */
const ResultsTable = ({ rows, columns, visibleColumns, setVisibleColumns, onRowClick }) => {
  // Get just the company data columns, not the nested financials
  const baseColumns = columns.filter(col => 
    col.field !== 'latest_financials' && 
    !col.field.includes('fiscal_year') && 
    !col.field.includes('statement') && 
    !col.field.includes('key') && 
    !col.field.includes('value')
  );
  
  // Add special columns for key financial metrics we want to display
  const financialColumns = [
    { field: 'revenue', headerName: 'REVENUE', width: 150 },
    { field: 'net_income', headerName: 'NET INCOME', width: 150 },
    { field: 'total_assets', headerName: 'TOTAL ASSETS', width: 150 },
    { field: 'total_debt', headerName: 'TOTAL DEBT', width: 150 },
    { field: 'pe_ratio', headerName: 'P/E RATIO', width: 150 }
  ];
  
  // Combine base columns and financial columns
  const allColumns = [...baseColumns, ...financialColumns];
  
  // Handle column visibility selection
  const handleColumnChange = (event) => {
    setVisibleColumns(event.target.value);
  };

  // Extract financial values from the nested structure
  const getFinancialValue = (row, key) => {
    if (!row.latest_financials) return 'N/A';
    
    // First check income_statement
    if (row.latest_financials.income_statement && 
        row.latest_financials.income_statement[key] !== undefined) {
      return row.latest_financials.income_statement[key];
    }
    
    // Then check balance_sheet
    if (row.latest_financials.balancesheet_statement && 
        row.latest_financials.balancesheet_statement[key] !== undefined) {
      return row.latest_financials.balancesheet_statement[key];
    }
    
    // Finally check cashflow_statement
    if (row.latest_financials.cashflow_statement && 
        row.latest_financials.cashflow_statement[key] !== undefined) {
      return row.latest_financials.cashflow_statement[key];
    }
    
    return 'N/A';
  };

  // Format values for display
  const formatValue = (value, field) => {
    if (value === undefined || value === null || value === 'N/A') return 'N/A';
    
    // Format financial values
    if (['revenue', 'net_income', 'total_assets', 'total_debt'].includes(field)) {
      return typeof value === 'number'
        ? `$${value.toLocaleString()}`
        : value;
    }
    
    // Format ratios
    if (field === 'pe_ratio') {
      return typeof value === 'number'
        ? value.toFixed(2)
        : value;
    }
    
    return value;
  };
  
  // Get cell value based on column field
  const getCellValue = (row, field) => {
    // Handle financial metrics from the nested structure
    if (['revenue', 'net_income', 'total_assets', 'total_debt', 'pe_ratio'].includes(field)) {
      return formatValue(getFinancialValue(row, field), field);
    }
    
    // Handle regular columns
    return formatValue(row[field], field);
  };

  return (
    <Box sx={{ width: '100%' }}>
      <Box sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
        <Typography variant="body1" sx={{ mr: 2 }}>
          {rows.length} companies found
        </Typography>
        <FormControl sx={{ minWidth: 240 }}>
          <InputLabel id="visible-columns-label">Visible Columns</InputLabel>
          <Select
            labelId="visible-columns-label"
            id="visible-columns"
            multiple
            value={visibleColumns}
            onChange={handleColumnChange}
            renderValue={(selected) => selected.join(', ')}
          >
            {allColumns.map((col) => (
              <MenuItem key={col.field} value={col.field}>
                {col.headerName}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>
      
      <TableContainer component={Paper} sx={{ maxHeight: 600 }}>
        <Table stickyHeader sx={{ minWidth: 650 }} size="small">
          <TableHead>
            <TableRow>
              {allColumns
                .filter(col => visibleColumns.includes(col.field))
                .map(col => (
                  <TableCell key={col.field} align="left" sx={{ fontWeight: 'bold', backgroundColor: '#f5f5f5' }}>
                    {col.headerName}
                  </TableCell>
                ))
              }
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map((row, index) => (
              <TableRow 
                key={row.symbol + '-' + index}
                hover
                onClick={() => onRowClick({ row })}
                sx={{ cursor: 'pointer', '&:hover': { backgroundColor: '#f1f8ff' } }}
              >
                {allColumns
                  .filter(col => visibleColumns.includes(col.field))
                  .map(col => (
                    <TableCell key={col.field} align="left">
                      {getCellValue(row, col.field)}
                    </TableCell>
                  ))
                }
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default ResultsTable; 