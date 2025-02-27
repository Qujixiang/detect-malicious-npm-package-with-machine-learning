/* eslint-disable no-lone-blocks */
import { parse } from '@babel/core'
import traverse from '@babel/traverse'
import { type PackageFeatureInfo } from './PackageFeatureInfo'
import { isMemberExpression } from '@babel/types'
import {
  base64_Pattern,
  getDomainPattern,
  IP_Pattern,
  SensitiveStringPattern
} from './Patterns'
import { getFileLogger } from '../FileLogger'
import { type PositionRecorder, type Record } from './PositionRecorder'

const MAX_STRING_LENGTH = 66875

/**
 * Analyze the JavaScript code by AST and extract the feature information.
 * @param code JavaScript code
 * @param featureSet feature information
 * @param isInstallScript whether the JavaScript file name is present in install script
 * @param targetJSFilePath current analyzed file path
 * @param positionRecorder feature position recorder
 * @returns feature information
 */
export async function extractFeaturesFromJSFileByAST (
  code: string,
  featureSet: PackageFeatureInfo,
  isInstallScript: boolean,
  targetJSFilePath: string,
  positionRecorder: PositionRecorder
): Promise<PackageFeatureInfo> {
  function getRecord (path: any) {
    return {
      filePath: targetJSFilePath,
      content: path.node.loc
    } as Record
  }

  const logger = await getFileLogger()
  let ast: any
  try {
    ast = parse(code, {
      sourceType: 'unambiguous'
    })
  } catch (error) {
    await logger.log('Current analyzed file is ' + targetJSFilePath)
    const errorObj = error as Error
    await logger.log(`ERROR MESSAGE: ${errorObj.name}: ${errorObj.message}`)
    await logger.log('ERROR STACK:' + errorObj.stack)
  }
  try {
    traverse(ast, {
      CallExpression: function (path) {
        // @ts-expect-error uselesss lint error
        if (path.node.callee.name === 'require') {
          if (
            path.node.arguments.length > 0 &&
            // @ts-expect-error uselesss lint error
            path.node.arguments[0].value === 'base64-js'
          ) {
            featureSet.useBase64Conversion = true
            positionRecorder.addRecord('useBase64Conversion', getRecord(path))
            if (isInstallScript) {
              featureSet.useBase64ConversionInInstallScript = true
              positionRecorder.addRecord('useBase64ConversionInInstallScript', getRecord(path))
            }
          }
          if (
            path.node.arguments.length > 0 &&
            // @ts-expect-error uselesss lint error
            path.node.arguments[0].value === 'child_process'
          ) {
            featureSet.requireChildProcessInJSFile = true
            positionRecorder.addRecord('requireChildProcessInJSFile', getRecord(path))
            if (isInstallScript) {
              featureSet.requireChildProcessInInstallScript = true
              positionRecorder.addRecord('requireChildProcessInInstallScript', getRecord(path))
            }
          }
          if (path.node.arguments.length > 0) {
            // @ts-expect-error uselesss lint error
            const importModuleName = path.node.arguments[0].value
            if (
              importModuleName === 'fs' ||
              importModuleName === 'fs/promises' ||
              importModuleName === 'path' ||
              importModuleName === 'promise-fs'
            ) {
              featureSet.accessFSInJSFile = true
              positionRecorder.addRecord('accessFSInJSFile', getRecord(path))
              if (isInstallScript) {
                featureSet.accessFSInInstallScript = true
                positionRecorder.addRecord('accessFSInInstallScript', getRecord(path))
              }
            }
          }
          if (path.node.arguments.length > 0) {
            // @ts-expect-error uselesss lint error
            const moduleName = path.node.arguments[0].value as string
            if (
              moduleName === 'http' ||
              moduleName === 'https' ||
              moduleName === 'nodemailer' ||
              moduleName === 'axios' ||
              moduleName === 'request' ||
              moduleName === 'node-fetch' ||
              moduleName === 'got'
            ) {
              featureSet.accessNetworkInJSFile = true
              positionRecorder.addRecord('accessNetworkInJSFile', getRecord(path))
              if (isInstallScript) {
                featureSet.accessNetworkInInstallScript = true
                positionRecorder.addRecord('accessNetworkInInstallScript', getRecord(path))
              }
            }
          }
          if (path.node.arguments.length > 0) {
            // @ts-expect-error uselesss lint error
            const moduleName = path.node.arguments[0].value as string
            if (moduleName === 'dns') {
              featureSet.containDomainInJSFile = true
              if (isInstallScript) {
                featureSet.containDomainInInstallScript = true
              }
            }
          }
          if (path.node.arguments.length > 0) {
            // @ts-expect-error uselesss lint error
            const moduleName = path.node.arguments[0].value as string
            if (moduleName === 'crypto' || moduleName === 'zlib') {
              featureSet.accessCryptoAndZip = true
              positionRecorder.addRecord('accessCryptoAndZip', getRecord(path))
            }
          }
        }
        if (
          isMemberExpression(path.node.callee) &&
          // @ts-expect-error uselesss lint error
          path.node.callee.object.name === 'os'
        ) {
          featureSet.accessSensitiveAPI = true
          positionRecorder.addRecord('accessSensitiveAPI', getRecord(path))
        }
      },
      StringLiteral: function (path) {
        const content = path.node.value
        if (content === 'base64') {
          featureSet.useBase64Conversion = true
          positionRecorder.addRecord('useBase64Conversion', getRecord(path))
          if (isInstallScript) {
            featureSet.useBase64ConversionInInstallScript = true
            positionRecorder.addRecord('useBase64ConversionInInstallScript', getRecord(path))
          }
        }
        if (content.length >= MAX_STRING_LENGTH) {
          return
        }
        {
          const matchResult = content.match(IP_Pattern)
          if (matchResult != null) {
            featureSet.containIP = true
            positionRecorder.addRecord('containIP', getRecord(path))
          }
        }
        {
          const matchResult = content.match(base64_Pattern)
          if (matchResult != null) {
            featureSet.containBase64StringInJSFile = true
            if (isInstallScript) {
              featureSet.containBase64StringInInstallScript = true
            }
          }
        }
        {
          const matchResult = content.match(getDomainPattern())
          if (matchResult != null) {
            featureSet.containDomainInJSFile = true
            positionRecorder.addRecord('containDomainInJSFile', getRecord(path))
            if (isInstallScript) {
              featureSet.containDomainInInstallScript = true
              positionRecorder.addRecord('containDomainInInstallScript', getRecord(path))
            }
          }
        }
        {
          const matchResult = content.match(SensitiveStringPattern)
          if (matchResult != null) {
            featureSet.containSuspiciousString = true
            positionRecorder.addRecord('containSuspiciousString', getRecord(path))
          }
        }
      },
      MemberExpression: function (path) {
        if (
          path.get('object').isIdentifier({ name: 'process' }) &&
          path.get('property').isIdentifier({ name: 'env' })
        ) {
          featureSet.accessProcessEnvInJSFile = true
          positionRecorder.addRecord('accessProcessEnvInJSFile', getRecord(path))
          if (isInstallScript) {
            featureSet.accessProcessEnvInInstallScript = true
            positionRecorder.addRecord('accessProcessEnvInInstallScript', getRecord(path))
          }
        }
        if (
          path.get('object').isIdentifier({ name: 'Buffer' }) &&
          path.get('property').isIdentifier({ name: 'from' })
        ) {
          featureSet.useBuffer = true
          positionRecorder.addRecord('useBuffer', getRecord(path))
        }
      },
      NewExpression: function (path) {
        // @ts-expect-error uselesss lint error
        if (path.node.callee.name === 'Buffer') {
          featureSet.useBuffer = true
          positionRecorder.addRecord('useBuffer', getRecord(path))
        }
      },
      ImportDeclaration: function (path) {
        const moduleName = path.node.source.value
        if (path.node.source.value === 'base64-js') {
          featureSet.useBase64Conversion = true
          positionRecorder.addRecord('useBase64Conversion', getRecord(path))
          if (isInstallScript) {
            featureSet.useBase64ConversionInInstallScript = true
            positionRecorder.addRecord('useBase64ConversionInInstallScript', getRecord(path))
          }
        }
        if (path.node.source.value === 'child_process') {
          featureSet.requireChildProcessInJSFile = true
          positionRecorder.addRecord('requireChildProcessInJSFile', getRecord(path))
          if (isInstallScript) {
            featureSet.requireChildProcessInInstallScript = true
            positionRecorder.addRecord('requireChildProcessInInstallScript', getRecord(path))
          }
        }
        {
          if (
            moduleName === 'fs' ||
            moduleName === 'fs/promises' ||
            moduleName === 'path' ||
            moduleName === 'promise-fs'
          ) {
            featureSet.accessFSInJSFile = true
            positionRecorder.addRecord('accessFSInJSFile', getRecord(path))
            if (isInstallScript) {
              featureSet.accessFSInInstallScript = true
              positionRecorder.addRecord('accessFSInInstallScript', getRecord(path))
            }
          }
        }
        {
          if (
            moduleName === 'http' ||
            moduleName === 'https' ||
            moduleName === 'nodemailer' ||
            moduleName === 'aixos' ||
            moduleName === 'request' ||
            moduleName === 'node-fetch'
          ) {
            featureSet.accessNetworkInJSFile = true
            positionRecorder.addRecord('accessNetworkInJSFile', getRecord(path))
            if (isInstallScript) {
              featureSet.accessNetworkInInstallScript = true
              positionRecorder.addRecord('accessNetworkInInstallScript', getRecord(path))
            }
          }
        }
        {
          if (moduleName === 'dns') {
            featureSet.containDomainInJSFile = true
            if (isInstallScript) {
              featureSet.containDomainInInstallScript = true
            }
          }
        }
        {
          if (moduleName === 'crypto' || moduleName === 'zlib') {
            featureSet.accessCryptoAndZip = true
            positionRecorder.addRecord('accessCryptoAndZip', getRecord(path))
          }
        }
      },
      Identifier: function (path) {
        if (path.node.name === 'eval') {
          featureSet.useEval = true
          positionRecorder.addRecord('useEval', getRecord(path))
        }
      }
    })
  } catch (error) {
    await logger.log('Current analyzed file is ' + targetJSFilePath)
    const errorObj = error as Error
    await logger.log(`ERROR MESSAGE: ${errorObj.name}: ${errorObj.message}`)
    await logger.log('ERROR STACK:' + errorObj.stack)
  }

  return featureSet
}
