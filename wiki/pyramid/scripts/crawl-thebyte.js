const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');

// Configuration
const BASE_URL = 'https://www.thebyte.com.cn';
const OUTPUT_DIR = '/Users/sphinx.shi/workspace/wiki/pyramid/raw/bookmarks/ebooks/thebyte';
const IMAGES_DIR = path.join(OUTPUT_DIR, 'images');
const MAX_IMAGES_PER_PAGE = 8;

// Pages to crawl
const pages = [
  '/intro.html',
  '/noun.html',
  '/architecture/summary.md',
  '/architecture/history.html',
  '/architecture/background.html',
  '/architecture/define-cloud-native.html',
  '/architecture/target.html',
  '/architecture/container.html',
  '/architecture/MicroService.html',
  '/architecture/ServiceMesh.html',
  '/architecture/Immutable.html',
  '/architecture/declarative-api.html',
  '/architecture/devops.html',
  '/architecture/arc.html',
  '/architecture/architect.html',
];

// Ensure directories exist
fs.mkdirSync(OUTPUT_DIR, { recursive: true });
fs.mkdirSync(IMAGES_DIR, { recursive: true });
fs.mkdirSync(path.join(OUTPUT_DIR, 'architecture'), { recursive: true });

async function downloadImage(imageUrl, pageName, index) {
  if (!imageUrl || imageUrl.startsWith('data:') || imageUrl.startsWith('//')) {
    return null;
  }

  // Convert protocol-relative URLs to https
  if (imageUrl.startsWith('//')) {
    imageUrl = 'https:' + imageUrl;
  }

  // Skip external URLs
  if (!imageUrl.startsWith(BASE_URL) && !imageUrl.startsWith('http')) {
    return null;
  }

  try {
    const urlObj = new URL(imageUrl);
    const pathname = urlObj.pathname;
    const ext = path.extname(pathname) || '.jpg';
    const filename = `${pageName}_img${index}${ext}`;
    const filepath = path.join(IMAGES_DIR, filename);

    const file = fs.createWriteStream(filepath);
    await new Promise((resolve, reject) => {
      const protocol = urlObj.protocol === 'https:' ? https : http;
      protocol.get(imageUrl, (response) => {
        if (response.statusCode === 200) {
          response.pipe(file);
          file.on('finish', () => {
            file.close();
            resolve();
          });
        } else {
          file.close();
          reject(new Error(`HTTP ${response.statusCode}`));
        }
      }).on('error', reject);
    });

    return filename;
  } catch (err) {
    console.log(`  Failed to download ${imageUrl}: ${err.message}`);
    return null;
  }
}

async function crawlPage(pagePath) {
  console.log(`\n=== Crawling: ${pagePath} ===`);

  const browser = await puppeteer.launch({
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  try {
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });

    const url = BASE_URL + pagePath;
    console.log(`  Loading: ${url}`);

    await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });

    // Wait for VuePress content to render
    await page.waitForSelector('.theme-default-content', { timeout: 10000 }).catch(() => {
      console.log('  Warning: .theme-default-content not found');
    });

    // Wait a bit more for dynamic content
    await new Promise(r => setTimeout(r, 2000));

    // Extract title
    const title = await page.evaluate(() => {
      const h1 = document.querySelector('h1');
      if (h1) {
        // Get text content only, removing any anchor symbols
        return h1.textContent.replace(/^#\s*/, '').trim();
      }
      return document.title;
    });
    console.log(`  Title: ${title}`);

    // Extract main content
    const content = await page.evaluate(() => {
      const contentEl = document.querySelector('.theme-default-content');
      if (!contentEl) return null;

      // Clone to avoid modifying original
      const clone = contentEl.cloneNode(true);

      // Remove script and style elements
      clone.querySelectorAll('script, style, .sidebar, .navbar, .page-nav, .page-meta, .footer, .qrcode, .giscus-wrapper, .page-info').forEach(el => el.remove());

      return clone.innerHTML;
    });

    if (!content) {
      console.log('  Warning: No content extracted');
    }

    // Extract images (max 8)
    const maxImages = MAX_IMAGES_PER_PAGE;
    const images = await page.evaluate((max) => {
      const contentEl = document.querySelector('.theme-default-content');
      if (!contentEl) return [];

      const imgElements = contentEl.querySelectorAll('img');
      return Array.from(imgElements).slice(0, max).map(img => img.src);
    }, maxImages);

    console.log(`  Found ${images.length} images`);

    // Download images
    const pageName = pagePath.replace(/^\//, '').replace(/\//g, '_').replace(/\.html?$/, '').replace(/\.md$/, '');
    const downloadedImages = [];

    for (let i = 0; i < images.length; i++) {
      const img = await downloadImage(images[i], pageName, i);
      if (img) {
        downloadedImages.push(img);
        console.log(`  Downloaded: ${img}`);
      }
    }

    // Replace image URLs in content with local filenames
    let processedContent = content;
    for (let i = 0; i < downloadedImages.length; i++) {
      if (images[i]) {
        processedContent = processedContent.replace(new RegExp(images[i].replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'), `images/${downloadedImages[i]}`);
      }
    }

    // Convert HTML to Markdown
    const markdown = htmlToMarkdown(processedContent, title);

    // Determine output file path
    let outputPath;
    if (pagePath.startsWith('/architecture/')) {
      outputPath = path.join(OUTPUT_DIR, 'architecture', path.basename(pagePath));
    } else {
      outputPath = path.join(OUTPUT_DIR, path.basename(pagePath));
    }

    // Change extension to .md
    outputPath = outputPath.replace(/\.html$/, '.md');

    fs.writeFileSync(outputPath, markdown);
    console.log(`  Saved: ${outputPath}`);

    return { title, path: pagePath, outputPath };

  } finally {
    await browser.close();
  }
}

function htmlToMarkdown(html, title) {
  if (!html) return '';

  // First, remove header anchor links like <a class="header-anchor" ...>#</a>
  html = html.replace(/<a[^>]*class="header-anchor"[^>]*>[^<]*<\/a>/gi, '');

  // Simple HTML to Markdown conversion
  let md = html
    // Remove VuePress specific elements - custom containers
    .replace(/<div class="custom-container[^"]*">/g, '\n:::')
    .replace(/<\/div>/g, '\n:::\n')
    // Headers - simple approach, just strip all tags from content
    .replace(/<h1[^>]*>([\s\S]*?)<\/h1>/gi, (_, c) => '# ' + c.replace(/<[^>]+>/g, '').trim() + '\n\n')
    .replace(/<h2[^>]*>([\s\S]*?)<\/h2>/gi, (_, c) => '## ' + c.replace(/<[^>]+>/g, '').trim() + '\n\n')
    .replace(/<h3[^>]*>([\s\S]*?)<\/h3>/gi, (_, c) => '### ' + c.replace(/<[^>]+>/g, '').trim() + '\n\n')
    .replace(/<h4[^>]*>([\s\S]*?)<\/h4>/gi, (_, c) => '#### ' + c.replace(/<[^>]+>/g, '').trim() + '\n\n')
    .replace(/<h5[^>]*>([\s\S]*?)<\/h5>/gi, (_, c) => '##### ' + c.replace(/<[^>]+>/g, '').trim() + '\n\n')
    .replace(/<h6[^>]*>([\s\S]*?)<\/h6>/gi, (_, c) => '###### ' + c.replace(/<[^>]+>/g, '').trim() + '\n\n')
    // Links
    .replace(/<a[^>]*href="([^"]*)"[^>]*>([\s\S]*?)<\/a>/gi, '[$2]($1)')
    // Bold and italic
    .replace(/<strong[^>]*>([\s\S]*?)<\/strong>/gi, '**$1**')
    .replace(/<b[^>]*>([\s\S]*?)<\/b>/gi, '**$1**')
    .replace(/<em[^>]*>([\s\S]*?)<\/em>/gi, '*$1*')
    .replace(/<i[^>]*>([\s\S]*?)<\/i>/gi, '*$1*')
    // Code
    .replace(/<code[^>]*>([\s\S]*?)<\/code>/gi, '`$1`')
    .replace(/<pre[^>]*>([\s\S]*?)<\/pre>/gi, '\n```\n$1\n```\n')
    // Lists
    .replace(/<ul[^>]*>/gi, '\n')
    .replace(/<\/ul>/gi, '\n')
    .replace(/<ol[^>]*>/gi, '\n')
    .replace(/<\/ol>/gi, '\n')
    .replace(/<li[^>]*>([\s\S]*?)<\/li>/gi, '- $1\n')
    // Paragraphs and line breaks
    .replace(/<p[^>]*>([\s\S]*?)<\/p>/gi, '\n$1\n\n')
    .replace(/<br\s*\/?>/gi, '\n')
    // Images (will be replaced with local paths by caller)
    .replace(/<img[^>]*src="([^"]*)"[^>]*>/gi, '![]($1)')
    .replace(/<img[^>]*alt="([^"]*)"[^>]*>/gi, '![]($1)')
    // Divs and spans - remove
    .replace(/<div[^>]*>/gi, '\n')
    .replace(/<\/div>/gi, '\n')
    .replace(/<span[^>]*>([\s\S]*?)<\/span>/gi, '$1')
    // Clean up empty tags
    .replace(/<[^>]+>:/gi, ':')
    .replace(/<[^>]+>/gi, '')
    // Clean up extra whitespace
    .replace(/\n{3,}/g, '\n\n')
    .replace(/^\s+/gm, '')
    .trim();

  return md;
}

async function main() {
  console.log('Starting crawl of thebyte.com.cn...');
  console.log(`Output directory: ${OUTPUT_DIR}`);

  const results = [];

  for (const pagePath of pages) {
    try {
      const result = await crawlPage(pagePath);
      results.push(result);
    } catch (err) {
      console.error(`  Error crawling ${pagePath}: ${err.message}`);
    }
  }

  console.log('\n=== Crawl Complete ===');
  console.log(`Processed ${results.length} pages`);
}

main().catch(console.error);