import { readFile } from 'fs/promises'
import fs from 'fs'
const filePath = '/Users/qjx/HUST/Projects/malicious-package-detection/detect-npm/datasets/preprocessed-datasets/malicious/npm-malicious-20230512/free-fortnite-accounts-cxe3-1.2.33/package/package.json'
const filePath2 = '/Users/qjx/HUST/Projects/malicious-package-detection/detect-npm/datasets/preprocessed-datasets/malicious/npm-malicious-20230512/free-fire-one-1.0.0/package/package.json'
// const fileContent = await readFile(filePath)
// const metaData = JSON.parse(fileContent)
// console.log(metaData)

function isUTF8WithBOM(filePath) {
  const buffer = fs.readFileSync(filePath);

  // 判断文件头部是否包含 UTF-8 with BOM 的标记字节
  if (buffer.length >= 3 && buffer[0] === 0xEF && buffer[1] === 0xBB && buffer[2] === 0xBF) {
    return true;
  } else {
    return false;
  }
}

// 示例用法
const isUTF8BOM = isUTF8WithBOM(filePath);
console.log(`Is UTF-8 with BOM: ${isUTF8BOM}`);

// 去除BOM头部标识
const fileContent = await readFile(filePath, { encoding: 'utf8' })
const utf8Content = fileContent.replace(/^\uFEFF/, '');
const metaData = JSON.parse(utf8Content)
console.log(metaData)