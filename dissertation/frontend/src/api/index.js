import axios from 'axios';

const api = axios.create({
    baseURL: 'http://127.0.0.1:8000/api'
});

export const getMapData = (year) => api.get('/map_data/',{params:{year}});
export const getRegionDetail = (year,region_name) => api.get(`/region_detail/${region_name}`,{params:{year}});
export const getRelationNetwork = () => api.get('/relation_network');
export const getGiniData = (year) => api.get('/gini_data',{params:{year}});
export const getGiniTrend = (indicator) => api.get('/gini_trend',{params:{indicator}});
// export const getDeaCluster = (year) => api.get('/dea_cluster',{params:{year}});
// export const getDeaTrend = () => api.get('/dea_trend');
// export const getDeaGini = () => api.get('/dea_gini');
export const getMacroBackground = () => api.get('/macro_background');
// export const getStaticChars = (year) => api.get('/static_charts',{params:{year}});
export const getDeaTrendData = () => api.get('/dea_trend_data');
export const getGiniDeaCoupling = () => api.get('/gini_dea_coupling');
export const getClusterData = (year) => api.get('/cluster_data', { params: { year } });
export const getRsrValidation = (year) => api.get('/rsr_validation', { params: { year } });
