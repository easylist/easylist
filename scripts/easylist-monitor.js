// EasyList staleness monitor - notification only
const fs = require('fs');

const EASYLIST_URLS = {
  'easylist.txt': 'https://easylist.to/easylist/easylist.txt',
  'easyprivacy.txt': 'https://easylist.to/easylist/easyprivacy.txt'
};

// Helper to set GitHub Actions output
function setOutput(name, value) {
  const output = process.env.GITHUB_OUTPUT;
  if (output) {
    fs.appendFileSync(output, `${name}=${value}\n`);
  }
}

class EasyListMonitor {
  async fetchList(url) {
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return await response.text();
    } catch (error) {
      console.error(`Failed to fetch ${url}:`, error.message);
      throw error;
    }
  }

  extractVersion(content) {
    const versionMatch = content.match(/^! Version: (.+)$/m);
    const lastModifiedMatch = content.match(/^! Last modified: (.+)$/m);
    
    return {
      version: versionMatch ? versionMatch[1] : null,
      lastModified: lastModifiedMatch ? lastModifiedMatch[1] : null
    };
  }

  checkFileAge(versionInfo, filename) {
    if (!versionInfo.lastModified) {
      return { isStale: false, message: 'No timestamp found', ageHours: 0 };
    }

    try {
      const lastModified = new Date(versionInfo.lastModified);
      const now = new Date();
      const ageInHours = (now - lastModified) / (1000 * 60 * 60);
      
      // 24 hour threshold
      const staleThreshold = 24;
      const isStale = ageInHours > staleThreshold;

      return {
        isStale,
        ageHours: ageInHours.toFixed(1),
        message: isStale 
          ? `STALE: ${ageInHours.toFixed(1)} hours old (threshold: 24 hours)`
          : `Fresh: ${ageInHours.toFixed(1)} hours old`
      };
    } catch (error) {
      return { 
        isStale: false, 
        ageHours: 0,
        message: `Invalid timestamp: ${versionInfo.lastModified}` 
      };
    }
  }

  async checkForUpdates() {
    console.log(`Checking ${Object.keys(EASYLIST_URLS).length} EasyList files for staleness...`);
    
    const staleFiles = [];
    
    for (const [filename, url] of Object.entries(EASYLIST_URLS)) {
      try {
        console.log(`Checking ${filename}...`);
        
        const content = await this.fetchList(url);
        const versionInfo = this.extractVersion(content);
        const ageCheck = this.checkFileAge(versionInfo, filename);
        
        console.log(`${filename}: ${ageCheck.message}`);
        console.log(`  Version: ${versionInfo.version || 'N/A'}`);
        console.log(`  Last Modified: ${versionInfo.lastModified || 'N/A'}`);
        
        if (ageCheck.isStale) {
          staleFiles.push({
            filename,
            lastModified: versionInfo.lastModified,
            version: versionInfo.version,
            ageHours: ageCheck.ageHours,
            message: ageCheck.message
          });
          
          console.log(`WARNING: ${filename} is STALE!`);
        }
        
        // Small delay between requests
        await new Promise(resolve => setTimeout(resolve, 1000));
        
      } catch (error) {
        console.error(`Error checking ${filename}:`, error.message);
      }
    }
    
    const hasStaleFiles = staleFiles.length > 0;
    
    if (hasStaleFiles) {
      console.log(`\nFound ${staleFiles.length} stale file(s):`);
      staleFiles.forEach(file => {
        console.log(`- ${file.filename}: ${file.ageHours} hours old`);
      });
    } else {
      console.log('\nAll files are fresh (under 24 hours old)');
    }
    
    return {
      hasStaleFiles,
      staleFiles,
      staleCount: staleFiles.length
    };
  }
}

// Main execution
async function main() {
  const monitor = new EasyListMonitor();
  
  try {
    const result = await monitor.checkForUpdates();
    
    // Set GitHub Actions outputs
    if (process.env.GITHUB_ACTIONS) {
      setOutput('files_stale', result.hasStaleFiles ? 'true' : 'false');
      setOutput('stale_count', result.staleCount.toString());
      setOutput('stale_details', JSON.stringify(result.staleFiles));
    }
    
    if (result.hasStaleFiles) {
      console.log('\nStale files detected - notifications will be sent');
      process.exit(0);
    } else {
      console.log('\nAll files are up to date');
      process.exit(0);
    }
  } catch (error) {
    console.error('Check failed:', error);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { EasyListMonitor };
