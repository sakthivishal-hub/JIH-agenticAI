const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');

const root = __dirname;
loadEnvironment(path.join(root, '.env'));
const port = Number(process.env.PORT) || 5173;

// 5-Minute In-Memory API Cache
const apiCache = new Map();
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

async function getCachedOrFetch(cacheKey, fetchFn) {
  const now = Date.now();
  if (apiCache.has(cacheKey)) {
    const entry = apiCache.get(cacheKey);
    if (now - entry.timestamp < CACHE_TTL) {
      console.log(`[Cache Hit] ${cacheKey}`);
      return entry.data;
    }
  }
  console.log(`[Cache Miss] ${cacheKey}`);
  const data = await fetchFn();
  apiCache.set(cacheKey, { timestamp: now, data });
  return data;
}

function loadEnvironment(filePath) {
  if (!fs.existsSync(filePath)) return;
  for (const line of fs.readFileSync(filePath, 'utf8').split(/\r?\n/)) {
    const match = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/);
    if (match && !process.env[match[1]]) process.env[match[1]] = match[2].replace(/^['"]|['"]$/g, '');
  }
}

async function requestJson(url, headers = {}) {
  const response = await fetch(url, { headers: { 'User-Agent': 'SignalHire/2.0 (Commercial Production)', ...headers }, signal: AbortSignal.timeout(10000) });
  if (!response.ok) throw new Error(`Source API returned status ${response.status}`);
  return response.json();
}

function stripHtml(value = '') {
  return value.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim();
}

// 1. JSearch (RapidAPI)
async function fetchJSearchRaw(query, location) {
  if (!process.env.JSEARCH_API_KEY) throw new Error('JSearch API key is not configured');
  const fullQuery = `${query} ${location || ''}`.trim();
  const payload = await requestJson(`https://jsearch.p.rapidapi.com/search?query=${encodeURIComponent(fullQuery)}&page=1&num_pages=1&date_posted=all`, {
    'X-RapidAPI-Key': process.env.JSEARCH_API_KEY,
    'X-RapidAPI-Host': 'jsearch.p.rapidapi.com'
  });
  
  return (payload.data || []).map(job => ({
    id: `jsearch-${job.job_id}`,
    title: job.job_title || 'Software Opportunity',
    company: job.employer_name || 'Verified Employer',
    location: [job.job_city, job.job_state, job.job_country].filter(Boolean).join(', ') || (job.job_is_remote ? 'Remote' : 'Location Not Specified'),
    salary: job.job_min_salary ? `${job.job_currency || '$'} ${job.job_min_salary.toLocaleString()}${job.job_max_salary ? ` - ${job.job_max_salary.toLocaleString()}` : '+'}` : 'Salary not listed',
    description: stripHtml(job.job_description || ''),
    employmentType: job.job_employment_type || (job.job_is_remote ? 'FULLTIME / REMOTE' : 'FULLTIME'),
    experience: job.job_required_experience?.required_experience_in_months ? `${Math.round(job.job_required_experience.required_experience_in_months / 12)}+ Years` : 'Mid-Senior',
    source: 'JSearch',
    publishedAt: job.job_posted_at_datetime_utc || new Date().toISOString(),
    companyLogo: job.employer_logo || '',
    applyLink: job.job_apply_link || job.job_google_link || ''
  }));
}

// 2. Remotive API
async function fetchRemotiveRaw(query) {
  const payload = await requestJson(`https://remotive.com/api/remote-jobs?search=${encodeURIComponent(query)}`);
  return (payload.jobs || []).map(job => ({
    id: `remotive-${job.id}`,
    title: job.title || 'Remote Developer',
    company: job.company_name || 'Tech Enterprise',
    location: job.candidate_required_location || 'Remote Worldwide',
    salary: job.salary || 'Salary not listed',
    description: stripHtml(job.description || ''),
    employmentType: job.job_type ? job.job_type.toUpperCase() : 'FULLTIME / REMOTE',
    experience: '3+ Years Preferred',
    source: 'Remotive',
    publishedAt: job.publication_date || new Date().toISOString(),
    companyLogo: job.company_logo_url || '',
    applyLink: job.url || ''
  }));
}

// 3. RemoteOK API
async function fetchRemoteOkRaw() {
  const payload = await requestJson('https://remoteok.com/api');
  const items = Array.isArray(payload) ? payload.slice(1) : [];
  return items.map(job => ({
    id: `remoteok-${job.id || job.slug}`,
    title: job.position || 'Engineering Role',
    company: job.company || 'Remote Innovators',
    location: job.location || 'Remote Worldwide',
    salary: job.salary_min ? `$${job.salary_min.toLocaleString()} - $${(job.salary_max || job.salary_min).toLocaleString()}` : 'Salary not listed',
    description: stripHtml(job.description || 'Remote opportunity listed on RemoteOK.'),
    employmentType: 'FULLTIME / REMOTE',
    experience: 'Senior Level',
    source: 'RemoteOK',
    publishedAt: job.date || new Date().toISOString(),
    companyLogo: job.company_logo || job.logo || '',
    applyLink: job.url || (job.slug ? `https://remoteok.com/remote-jobs/${job.slug}` : '')
  }));
}

// 4. Arbeitnow API
async function fetchArbeitnowRaw() {
  const payload = await requestJson('https://www.arbeitnow.com/api/job-board-api');
  return (payload.data || []).map(job => ({
    id: `arbeitnow-${job.slug}`,
    title: job.title || 'Tech Specialist',
    company: job.company_name || 'European Tech Firm',
    location: job.location || (job.remote ? 'Remote EU' : 'Europe'),
    salary: 'Salary not listed',
    description: stripHtml(job.description || ''),
    employmentType: job.remote ? 'REMOTE / HYBRID' : 'FULLTIME',
    experience: 'Mid Level',
    source: 'Arbeitnow',
    publishedAt: job.created_at ? new Date(job.created_at * 1000).toISOString() : new Date().toISOString(),
    companyLogo: '',
    applyLink: job.url || ''
  }));
}

// Cached API Wrappers
async function fetchJSearch(query, location) {
  const cacheKey = `jsearch:${query}:${location}`;
  return getCachedOrFetch(cacheKey, () => fetchJSearchRaw(query, location));
}

async function fetchRemotive(query) {
  const cacheKey = `remotive:${query}`;
  return getCachedOrFetch(cacheKey, () => fetchRemotiveRaw(query));
}

async function fetchRemoteOk() {
  const cacheKey = `remoteok:global`;
  return getCachedOrFetch(cacheKey, () => fetchRemoteOkRaw());
}

async function fetchArbeitnow() {
  const cacheKey = `arbeitnow:global`;
  return getCachedOrFetch(cacheKey, () => fetchArbeitnowRaw());
}

const sources = { jsearch: fetchJSearch, remotive: fetchRemotive, remoteok: fetchRemoteOk, arbeitnow: fetchArbeitnow };

function matches(job, query, location) {
  const words = query.toLowerCase().split(/\s+/).filter(w => w.length > 2 && w !== 'remote');
  const haystack = `${job.title} ${job.company} ${job.description} ${job.location}`.toLowerCase();
  const locationTerm = (location || '').trim().toLowerCase();
  
  const matchesQuery = !words.length || words.some(w => haystack.includes(w));
  
  let matchesLocation = true;
  if (locationTerm) {
    if (locationTerm === 'remote') {
      matchesLocation = job.location.toLowerCase().includes('remote') || 
                        job.source.toLowerCase() === 'remotive' || 
                        job.source.toLowerCase() === 'remoteok';
    } else {
      matchesLocation = job.location.toLowerCase().includes(locationTerm) ||
                        job.location.toLowerCase().includes('remote') ||
                        job.location.toLowerCase().includes('global') ||
                        job.location.toLowerCase().includes('worldwide');
    }
  }
  
  return matchesQuery && matchesLocation;
}

// Reverse Geocoding Endpoint
async function reverseGeocodeHandler(url, response) {
  const lat = url.searchParams.get('lat');
  const lon = url.searchParams.get('lon');
  
  if (lat && lon) {
    try {
      const geoRes = await requestJson(`https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${lat}&longitude=${lon}&localityLanguage=en`);
      if (geoRes && (geoRes.city || geoRes.locality)) {
        response.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
        return response.end(JSON.stringify({
          city: geoRes.city || geoRes.locality || 'Chennai',
          state: geoRes.principalSubdivision || 'Tamil Nadu',
          country: geoRes.countryName || 'India'
        }));
      }
    } catch (e) {
      console.warn('[Geocode API Fail]', e.message);
    }
  }

  // IP Fallback
  try {
    const ipRes = await requestJson('https://ipapi.co/json/');
    if (ipRes && ipRes.city) {
      response.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
      return response.end(JSON.stringify({
        city: ipRes.city,
        state: ipRes.region || '',
        country: ipRes.country_name || 'India'
      }));
    }
  } catch (e) {}

  response.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
  response.end(JSON.stringify({ city: 'Chennai', state: 'Tamil Nadu', country: 'India' }));
}

// Jobs Search Handler
async function jobsResponse(url, response) {
  const query = url.searchParams.get('q') || 'software engineer';
  const location = url.searchParams.get('location') || '';
  const customJSearchKey = url.searchParams.get('jsearch_key');
  
  if (customJSearchKey) {
    process.env.JSEARCH_API_KEY = customJSearchKey;
  }
  
  const requested = (url.searchParams.get('sources') || Object.keys(sources).join(',')).split(',').filter(s => sources[s]);
  const failedSources = [];
  
  const results = await Promise.allSettled(
    requested.map(async sourceName => {
      try {
        const res = await sources[sourceName](query, location);
        if (Array.isArray(res)) return res;
        return [];
      } catch (e) {
        failedSources.push(sourceName);
        console.warn(`[API Source Offline] ${sourceName}: ${e.message}`);
        return [];
      }
    })
  );
  
  let jobs = results
    .flatMap(result => result.status === 'fulfilled' ? result.value : [])
    .filter(job => matches(job, query, location));
    
  // Deduplicate by Title + Company
  const seen = new Set();
  const uniqueJobs = [];
  
  for (const job of jobs) {
    const key = `${job.title.toLowerCase().trim()}|${job.company.toLowerCase().trim()}`;
    if (!seen.has(key) && job.applyLink) {
      seen.add(key);
      uniqueJobs.push(job);
    }
  }
  
  // Sort by publishedAt newest first
  uniqueJobs.sort((a, b) => new Date(b.publishedAt || 0) - new Date(a.publishedAt || 0));
  
  response.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' });
  response.end(JSON.stringify({
    jobs: uniqueJobs.slice(0, 100),
    failedSources,
    fetchedAt: new Date().toISOString()
  }));
}

function serveStatic(requestPath, response) {
  const safePath = requestPath === '/' ? 'index.html' : requestPath.replace(/^\/+/, '');
  const filePath = path.resolve(root, safePath);
  if (!filePath.startsWith(root) || !fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
    return response.writeHead(404).end('Not found');
  }
  
  const contentTypes = { 
    '.html': 'text/html; charset=utf-8', 
    '.js': 'text/javascript; charset=utf-8', 
    '.css': 'text/css; charset=utf-8',
    '.svg': 'image/svg+xml',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.ico': 'image/x-icon',
    '.json': 'application/json; charset=utf-8'
  };
  
  response.writeHead(200, { 'Content-Type': contentTypes[path.extname(filePath)] || 'application/octet-stream' });
  fs.createReadStream(filePath).pipe(response);
}

http.createServer((request, response) => {
  const url = new URL(request.url, `http://${request.headers.host}`);
  if (url.pathname === '/api/reverse-geocode') return reverseGeocodeHandler(url, response);
  if (url.pathname === '/api/jobs') return jobsResponse(url, response).catch(err => {
    console.error('[Unhandled Express Route Failure]', err);
    response.writeHead(500).end(JSON.stringify({ jobs: [], failedSources: Object.keys(sources) }));
  });
  serveStatic(url.pathname, response);
}).listen(port, '127.0.0.1', () => console.log(`SignalHire Production Server running at http://127.0.0.1:${port}`));
