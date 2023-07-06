import { stringify } from 'csv-stringify/sync'
import { writeFile } from 'fs/promises'
import { join } from 'path'
import { getValidFileName } from '../util'
import { getPackageFeatureInfo, type PackageFeatureInfo } from './PackageFeatureInfo'

/**
 * Extract features from the npm package and save the features to the feature file
 * @param packagePath the directory of the npm package, where there should be a package.json file
 * @param featureDirPath directory of saving feature files
 * @returns the path of the feature file and feature information
 */
export async function extractFeatureFromPackage (packagePath: string, featureDirPath: string) {
  const result: PackageFeatureInfo = await getPackageFeatureInfo(packagePath)
  const fileName = getValidFileName(result.packageName)
  const csvPath = join(featureDirPath, fileName + '.csv')
  const featureArr: Array<[string, number | boolean]> = []
  featureArr.push(['hasInstallScript', result.hasInstallScripts])
  featureArr.push(['containIP', result.containIP])
  featureArr.push(['useBase64Conversion', result.useBase64Conversion])
  featureArr.push(['useBase64ConversionInInstallScript', result.useBase64ConversionInInstallScript])
  featureArr.push(['containBase64StringInJSFile', result.containBase64StringInJSFile])
  featureArr.push(['containBase64StringInInstallScript', result.containBase64StringInInstallScript])
  featureArr.push(['containBytestring', result.containBytestring])
  featureArr.push(['containDomainInJSFile', result.containDomainInJSFile])
  featureArr.push(['containDomainInInstallScript', result.containDomainInInstallScript])
  featureArr.push(['useBuffer', result.useBuffer])
  featureArr.push(['useEval', result.useEval])
  featureArr.push(['requireChildProcessInJSFile', result.requireChildProcessInJSFile])
  featureArr.push(['requireChildProcessInInstallScript', result.requireChildProcessInInstallScript])
  featureArr.push(['accessFSInJSFile', result.accessFSInJSFile])
  featureArr.push(['accessFSInInstallScript', result.accessFSInInstallScript])
  featureArr.push(['accessNetworkInJSFile', result.accessNetworkInJSFile])
  featureArr.push(['accessNetworkInInstallScript', result.accessNetworkInInstallScript])
  featureArr.push(['accessProcessEnvInJSFile', result.accessProcessEnvInJSFile])
  featureArr.push(['accessProcessEnvInInstallScript', result.accessProcessEnvInInstallScript])
  featureArr.push(['containSuspicousString', result.containSuspiciousString])
  featureArr.push(['accessCryptoAndZip', result.accessCryptoAndZip])
  featureArr.push(['accessSensitiveAPI', result.accessSensitiveAPI])
  await new Promise(resolve => {
    setTimeout(async () => {
      await writeFile(csvPath, stringify(featureArr, {
        cast: {
          boolean: function (value) {
            if (value) {
              return 'true'
            }
            return 'false'
          }
        }
      }))
      resolve(true)
    })
  })
  return {
    csvPath,
    featureInfo: result
  }
}
