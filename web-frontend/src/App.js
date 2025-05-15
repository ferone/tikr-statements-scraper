import React, { useEffect, useState } from 'react';
import { Container, Typography, Box, CircularProgress, Snackbar, Alert } from '@mui/material';
import QueryBuilder from './components/QueryBuilder';
import ResultsTable from './components/ResultsTable';
import CompanyModal from './components/CompanyModal';
import { getFields, screener, getCompany } from './utils/api';

function App() {
  const [fields, setFields] = useState([]);
  const [filters, setFilters] = useState([]);
  const [columns, setColumns] = useState([]);
  const [visibleColumns, setVisibleColumns] = useState([]);
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [companyModal, setCompanyModal] = useState({ open: false, company: null, financials: [] });
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });

  useEffect(() => {
    // Load available fields when component mounts
    setLoading(true);
    getFields()
      .then(f => {
        setFields(f);
        setFilters([]);
        // Add default filter for testing
        setFilters([{ field: 'sector', op: '=', value: 'Technology' }]);
      })
      .catch(error => {
        setSnackbar({ open: true, message: 'Failed to load fields from API', severity: 'error' });
        console.error('Error loading fields:', error);
      })
      .finally(() => setLoading(false));
  }, []);

  // Set up columns for DataGrid
  useEffect(() => {
    if (fields.length > 0) {
      const cols = fields.map(f => ({ field: f, headerName: f.replace(/_/g, ' ').toUpperCase(), width: 150 }));
      setColumns(cols);
      setVisibleColumns(cols.map(c => c.field));
    }
  }, [fields]);

  const runQuery = async () => {
    if (filters.length === 0) {
      setSnackbar({ open: true, message: 'Please add at least one filter', severity: 'warning' });
      return;
    }
    
    setLoading(true);
    try {
      const results = await screener(filters);
      console.log('Query results:', results);
      
      if (!results || results.length === 0) {
        setRows([]);
        setSnackbar({ open: true, message: 'No results found for your query', severity: 'info' });
      } else {
        setRows(results);
        setSnackbar({ open: true, message: `Found ${results.length} results`, severity: 'success' });
      }
    } catch (e) {
      console.error('Query error:', e);
      setSnackbar({ open: true, message: `Query failed: ${e.message || 'Unknown error'}`, severity: 'error' });
      setRows([]);
    }
    setLoading(false);
  };

  const handleRowClick = async (params) => {
    if (!params.row || !params.row.symbol) {
      setSnackbar({ open: true, message: 'Invalid row data', severity: 'error' });
      return;
    }
    
    setLoading(true);
    try {
      const data = await getCompany(params.row.symbol);
      setCompanyModal({ open: true, company: data.company, financials: data.financials });
    } catch (e) {
      console.error('Company details error:', e);
      setSnackbar({ open: true, message: 'Failed to load company details', severity: 'error' });
    }
    setLoading(false);
  };

  // Run a sample query on component mount
  useEffect(() => {
    if (filters.length > 0 && fields.length > 0) {
      runQuery();
    }
  }, [fields]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom align="center">Stock Screener (GuruFocus Style)</Typography>
      <Box sx={{ mb: 2 }}>
        <QueryBuilder filters={filters} setFilters={setFilters} fields={fields} />
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
          <button onClick={runQuery} disabled={loading} style={{ padding: '8px 24px', fontSize: 18, borderRadius: 8, background: '#1976d2', color: '#fff', border: 'none', cursor: 'pointer', opacity: loading ? 0.7 : 1 }}>
            {loading ? 'Running...' : 'Run Screen'}
          </button>
        </Box>
      </Box>
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>
      ) : rows.length === 0 ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4, p: 3, border: '1px dashed #ccc', borderRadius: 2 }}>
          <Typography color="text.secondary">No data found. Please try a different query.</Typography>
        </Box>
      ) : (
        <ResultsTable
          rows={rows}
          columns={columns}
          visibleColumns={visibleColumns}
          setVisibleColumns={setVisibleColumns}
          onRowClick={handleRowClick}
        />
      )}
      <CompanyModal
        open={companyModal.open}
        onClose={() => setCompanyModal({ open: false, company: null, financials: [] })}
        company={companyModal.company}
        financials={companyModal.financials}
      />
      <Snackbar open={snackbar.open} autoHideDuration={3000} onClose={() => setSnackbar({ ...snackbar, open: false })}>
        <Alert severity={snackbar.severity}>{snackbar.message}</Alert>
      </Snackbar>
    </Container>
  );
}

export default App;
