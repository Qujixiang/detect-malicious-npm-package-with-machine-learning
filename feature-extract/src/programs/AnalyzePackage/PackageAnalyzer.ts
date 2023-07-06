import { extractFeatureFromPackage } from '../../feature-extract'
import { getErrorInfo, getPackagesFromDir } from '../../util'
import { getConfig } from '../../config'
import { join } from 'path'
import { writeFile, mkdir } from 'fs/promises'
import { Logger } from '../../Logger'
import { error } from 'console'

function getAnalyzeResult (fileName: string, featurePosPath: string) {
  return `Finished extracting features of ${fileName}.  recorded at ${featurePosPath}`
}

/**
 * Extract the features of a single npm package
 * @param packagePath the absolute path to npm package
 * @param featureDirPath the absolute directory path to save feature files
 * @param featurePosDirPath the absolute directory path to save feature position files
 */
async function analyzeSinglePackage (packagePath: string, featureDirPath: string, featurePosDirPath: string) {
  const result = await extractFeatureFromPackage(packagePath, featureDirPath)
  const packageName = `${result.featureInfo.packageName}@${result.featureInfo.version}`.replace('/', '#')
  try {
    const featurePosPath = join(featurePosDirPath, `${packageName}.json`)
    Logger.warning(getAnalyzeResult(packageName, featurePosPath))
    await writeFile(featurePosPath, getConfig().positionRecorder!.serializeRecord())
    return result
  } catch (error) {
    Logger.error(getErrorInfo(error))
    return null
  }
}

/**
 * Extract the features of all npm packages in the directory
 * @param packageDirPath the absolute directory path to npm package
 * @param featureDirPath the absolute directory path to save feature files
 * @param featurePosDirPath the absolute directory path to save feature position files
 */
export async function analyzePackages (packageDirPath: string, featureDirPath: string, featurePosDirPath: string) {
  try { await mkdir(featureDirPath) } catch (e) {}
  try { await mkdir(featurePosDirPath) } catch (e) {}
  const packagesPath = await getPackagesFromDir(packageDirPath)
  for (const packagePath of packagesPath) {
    await analyzeSinglePackage(packagePath, featureDirPath, featurePosDirPath)
  }
}
