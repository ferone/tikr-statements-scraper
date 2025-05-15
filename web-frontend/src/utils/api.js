import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000';

export async function getFields() {
  const res = await axios.get(`${API_BASE}/fields`);
  return res.data.fields;
}

export async function screener(filters, limit = 100, offset = 0, columns = null) {
  const res = await axios.post(`${API_BASE}/screener`, {
    filters,
    limit,
    offset,
    columns,
  });
  return res.data.results;
}

export async function getCompany(symbol) {
  const res = await axios.get(`${API_BASE}/company/${symbol}`);
  return res.data;
} 