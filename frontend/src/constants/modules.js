export const MODULE_OPTIONS = [
  { id: 'port_scan', label: 'Port Scan', description: 'nmap -sV -sC + NVD CVE lookup' },
  { id: 'subdomain', label: 'Subdomains', description: 'crt.sh + DNS resolution' },
  { id: 'header', label: 'HTTP Headers', description: 'Security headers via httpx' },
  { id: 'dir_enum', label: 'Directory Enum', description: 'Common path discovery' },
  { id: 'owasp', label: 'OWASP Checks', description: 'Header security analysis' },
  { id: 'osint', label: 'OSINT', description: 'WHOIS + IP geolocation' },
  { id: 'ai_summary', label: 'AI Summary', description: 'Claude executive report' },
]

export const SCAN_PROFILES = [
  {
    id: 'quick',
    label: 'Quick',
    description: 'Headers + OSINT',
    modules: ['header', 'osint'],
  },
  {
    id: 'standard',
    label: 'Standard',
    description: 'Ports, headers, OSINT',
    modules: ['port_scan', 'header', 'osint'],
  },
  {
    id: 'full',
    label: 'Full Recon',
    description: 'All modules including AI',
    modules: ['port_scan', 'subdomain', 'header', 'dir_enum', 'owasp', 'osint', 'ai_summary'],
  },
]

export const SSE_EVENT_TYPES = [
  'module_start',
  'module_progress',
  'module_complete',
  'module_error',
  'scan_complete',
]
