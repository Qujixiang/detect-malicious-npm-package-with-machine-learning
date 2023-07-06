import { type PackageFeatureInfo } from './PackageFeatureInfo'
import { bytestring_pattern2 } from './Patterns'
import { type PositionRecorder } from './PositionRecorder'

export function matchUseRegExp (code: string, result: PackageFeatureInfo, positionRecorder: PositionRecorder, targetJSFilePath: string) {
  const matchResult = code.match(bytestring_pattern2)
  if (matchResult != null) {
    result.containBytestring = true
    positionRecorder.addRecord('containBytestring', {
      filePath: targetJSFilePath,
      content: matchResult[1]
    })
  }
}
