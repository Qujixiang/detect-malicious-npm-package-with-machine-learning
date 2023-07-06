import chalk from 'chalk'
import { access, stat, readFile } from 'fs/promises'
import { dirname, join } from 'path'
import { isUTF8WithBOM, readFileFromUTF8WithBOM } from '../util/FileUtil'
import { Logger } from '../Logger'

export async function getPackageSize (tgzPath: string) {
  const fileInfo = await stat(tgzPath)
  return fileInfo.size
}

export interface PackageJSONInfo {
  dependencyNumber: number
  devDependencyNumber: number
  hasInstallScripts: boolean
  installCommand: string[]
  executeJSFiles: string[]
  packageName: string
  version: string
}

/**
 * Extract package information from package.json
 * @param packageJsonPath the path to package.json
 * @returns package information
 */
export async function getPackageJSONInfo (packageJsonPath: string): Promise<PackageJSONInfo> {
  const result: PackageJSONInfo = {
    dependencyNumber: 0,
    devDependencyNumber: 0,
    hasInstallScripts: false,
    installCommand: [],
    executeJSFiles: [],
    packageName: '',
    version: ''
  }
  let fileContent: string = ''
  if (await isUTF8WithBOM(packageJsonPath)) {
    fileContent = await readFileFromUTF8WithBOM(packageJsonPath)
  } else {
    fileContent = await readFile(packageJsonPath, { encoding: 'utf-8' })
  }
  const metaData = JSON.parse(fileContent)
  result.dependencyNumber = Object.keys(metaData?.dependencies || {}).length
  result.devDependencyNumber = Object.keys(metaData?.devDependencies || {}).length
  result.hasInstallScripts = Boolean(metaData?.scripts?.preinstall) || Boolean(metaData?.scripts?.install) || Boolean(metaData?.scripts?.postinstall)
  const executeJSFiles: string[] = []
  result.packageName = metaData?.name
  result.version = metaData?.version
  const preinstall = metaData?.scripts?.preinstall
  const install = metaData?.scripts?.install
  const postinstall = metaData?.scripts?.postinstall
  const parentDir = dirname(packageJsonPath)
  if (preinstall) {
    result.installCommand.push(preinstall)
    let jsFile = extractJSFilePath(preinstall)
    if (jsFile) {
      try {
        jsFile = join(parentDir, jsFile)
        await access(jsFile)
        executeJSFiles.push(jsFile)
      } catch (error) {
        Logger.warning(chalk.red(`The file in ${packageJsonPath} doesn't exist.`))
      }
    }
  }
  if (install) {
    result.installCommand.push(install)
    let jsFile = extractJSFilePath(install)
    if (jsFile) {
      try {
        jsFile = join(parentDir, jsFile)
        await access(jsFile)
        executeJSFiles.push(jsFile)
      } catch (error) {
        Logger.warning(chalk.red(`The file in ${packageJsonPath} doesn't exist.`))
      }
    }
  }
  if (postinstall) {
    result.installCommand.push(postinstall)
    let jsFile = extractJSFilePath(postinstall)
    if (jsFile) {
      jsFile = join(parentDir, jsFile)
      try {
        await access(jsFile)
        executeJSFiles.push(jsFile)
      } catch (error) {
        Logger.warning(chalk.red(`The file in ${packageJsonPath} doesn't exist.`))
      }
    }
  }
  result.executeJSFiles = executeJSFiles
  return result
}

/**
 * Extract the path to the JS file in the script content
 * @param scriptContent preinsta/install/postinstall script in package.json
 * @returns the path to the JS file in the script content
 */
export function extractJSFilePath (scriptContent: string): string | undefined {
  const jsFileReg = /node\s+?(.+?\.js)/
  const matchResult = scriptContent.match(jsFileReg)
  if (matchResult != null) {
    return matchResult[1]
  }
  return undefined
}
