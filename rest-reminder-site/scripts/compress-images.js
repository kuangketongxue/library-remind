const sharp = require('sharp');
const path = require('path');
const fs = require('fs');

// Use absolute paths
const publicDir = 'C:\\Users\\binlo\\Desktop\\休息提醒\\rest-reminder-site\\public';
const rootDir = 'C:\\Users\\binlo\\Desktop\\休息提醒';

async function compress() {
  // 1. Logo: resize to 512px
  const logoOut = path.join(publicDir, 'rest-reminder-logo.png');
  const logoTmp = path.join(publicDir, 'rest-reminder-logo-tmp.png');
  await sharp(logoOut)
    .resize(512, 512, { fit: 'inside', withoutEnlargement: true })
    .png({ quality: 85, compressionLevel: 9 })
    .toFile(logoTmp);
  fs.renameSync(logoTmp, logoOut);

  // 2. Desktop icon: 256px
  const iconOut = path.join(rootDir, 'cute_icon.png');
  await sharp(logoOut)
    .resize(256, 256, { fit: 'inside', withoutEnlargement: true })
    .png({ quality: 85 })
    .toFile(iconOut);

  // 3. Hero: 1200px wide
  const heroOut = path.join(publicDir, 'hero-banner.png');
  const heroTmp = path.join(publicDir, 'hero-banner-tmp.png');
  await sharp(heroOut)
    .resize(1200, null, { fit: 'inside', withoutEnlargement: true })
    .png({ quality: 80, compressionLevel: 9 })
    .toFile(heroTmp);
  fs.renameSync(heroTmp, heroOut);

  // 4. Favicon: 128px
  const favOut = path.join(publicDir, 'favicon.png');
  const favTmp = path.join(publicDir, 'favicon-tmp.png');
  await sharp(favOut)
    .resize(128, 128, { fit: 'inside', withoutEnlargement: true })
    .png({ quality: 90 })
    .toFile(favTmp);
  fs.renameSync(favTmp, favOut);

  console.log('Done');
}

compress().catch(e => { console.error(e); process.exit(1); });
