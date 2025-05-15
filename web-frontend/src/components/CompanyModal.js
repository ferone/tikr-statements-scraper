import React, { useState } from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Box, Typography, Tabs, Tab, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Grid } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';

function TabPanel(props) {
  const { children, value, index, ...other } = props;
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const CompanyModal = ({ open, onClose, company, financials }) => {
  const [tabValue, setTabValue] = useState(0);
  const [yearFilter, setYearFilter] = useState('all');

  if (!company) return null;

  // Group financials by year and statement type
  const years = [...new Set(financials.map(f => f.fiscal_year))].sort((a, b) => b - a);
  
  // Get filtered financials based on selected year
  const filteredFinancials = yearFilter === 'all' 
    ? financials 
    : financials.filter(f => f.fiscal_year === parseInt(yearFilter));
  
  // Group financials by statement type
  const statementTypes = [...new Set(filteredFinancials.map(f => f.statement))];
  
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleYearChange = (year) => {
    setYearFilter(year);
  };

  // Format value for display
  const formatValue = (value) => {
    if (value === null || value === undefined) return 'N/A';
    if (typeof value === 'number') {
      // Format numbers with commas for thousands
      return value.toLocaleString();
    }
    return value;
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <Typography variant="h5">{company.symbol} - {company.short_name}</Typography>
          <Typography variant="subtitle1" color="text.secondary">
            {company.sector} | {company.industry} | {company.exchange}
          </Typography>
        </div>
        <Button variant="outlined" color="primary" onClick={onClose}>Close</Button>
      </DialogTitle>
      <DialogContent dividers>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6">Company Information</Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Box sx={{ p: 2, border: '1px solid #eee', borderRadius: 1 }}>
                <Typography variant="body2"><strong>Full Name:</strong> {company.long_name}</Typography>
                <Typography variant="body2"><strong>Country:</strong> {company.country}</Typography>
                <Typography variant="body2"><strong>Employees:</strong> {company.full_time_employees ? company.full_time_employees.toLocaleString() : 'N/A'}</Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={6}>
              <Box sx={{ p: 2, border: '1px solid #eee', borderRadius: 1 }}>
                <Typography variant="body2"><strong>Market:</strong> {company.market}</Typography>
                <Typography variant="body2"><strong>Exchange:</strong> {company.exchange}</Typography>
                <Typography variant="body2"><strong>Market Cap:</strong> {company.market_cap ? `$${company.market_cap.toLocaleString()}` : 'N/A'}</Typography>
              </Box>
            </Grid>
          </Grid>
        </Box>

        {financials.length > 0 && (
          <Box sx={{ width: '100%' }}>
            <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
              <Typography variant="h6">Financial Statements</Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', my: 2 }}>
                <Typography variant="body2" sx={{ mr: 2 }}>Filter by Year:</Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  <Button 
                    variant={yearFilter === 'all' ? 'contained' : 'outlined'} 
                    size="small" 
                    onClick={() => handleYearChange('all')}
                  >
                    All Years
                  </Button>
                  {years.map(year => (
                    <Button 
                      key={year}
                      variant={yearFilter === year ? 'contained' : 'outlined'} 
                      size="small" 
                      onClick={() => handleYearChange(year)}
                    >
                      {year}
                    </Button>
                  ))}
                </Box>
              </Box>
              <Tabs value={tabValue} onChange={handleTabChange}>
                {statementTypes.map((type, index) => (
                  <Tab key={type} label={type.replace(/_/g, ' ').toUpperCase()} />
                ))}
              </Tabs>
            </Box>
            
            {statementTypes.map((type, index) => (
              <TabPanel key={type} value={tabValue} index={index}>
                <TableContainer component={Paper}>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell><strong>Metric</strong></TableCell>
                        {filteredFinancials
                          .filter(f => f.statement === type)
                          .sort((a, b) => b.fiscal_year - a.fiscal_year)
                          .map(f => (
                            <TableCell key={f.fiscal_year} align="right">
                              <strong>{f.fiscal_year}</strong>
                            </TableCell>
                          ))
                        }
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {Object.entries(
                        filteredFinancials
                          .filter(f => f.statement === type)
                          .reduce((acc, curr) => {
                            // Extract all unique keys from financial data
                            Object.keys(curr.data).forEach(key => {
                              if (!acc[key]) acc[key] = {};
                              acc[key][curr.fiscal_year] = curr.data[key];
                            });
                            return acc;
                          }, {})
                      ).map(([key, yearValues]) => (
                        <TableRow key={key} hover>
                          <TableCell component="th" scope="row">{key}</TableCell>
                          {years
                            .filter(year => yearFilter === 'all' || year === parseInt(yearFilter))
                            .sort((a, b) => b - a)
                            .map(year => (
                              <TableCell key={year} align="right">
                                {formatValue(yearValues[year])}
                              </TableCell>
                            ))
                          }
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </TabPanel>
            ))}
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} color="primary">Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default CompanyModal; 