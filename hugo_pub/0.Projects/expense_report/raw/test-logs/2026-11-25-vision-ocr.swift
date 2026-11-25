import Foundation
import Vision
import ImageIO

let url = URL(fileURLWithPath: CommandLine.arguments[1])
guard let src = CGImageSourceCreateWithURL(url as CFURL, nil),
      let img = CGImageSourceCreateImageAtIndex(src, 0, nil) else { fatalError("이미지 열기 실패") }
let props = CGImageSourceCopyPropertiesAtIndex(src, 0, nil) as? [CFString: Any]
let orientRaw = (props?[kCGImagePropertyOrientation] as? UInt32) ?? 1
let orient = CGImagePropertyOrientation(rawValue: orientRaw) ?? .up
let req = VNRecognizeTextRequest()
req.recognitionLevel = .accurate
req.recognitionLanguages = ["ko-KR", "en-US"]
req.usesLanguageCorrection = false
let t0 = Date()
try VNImageRequestHandler(cgImage: img, orientation: orient).perform([req])
let lines = (req.results ?? []).compactMap { $0.topCandidates(1).first?.string }
print(lines.joined(separator: "\n"))
FileHandle.standardError.write("[\(String(format: "%.1f", Date().timeIntervalSince(t0)))s]\n".data(using: .utf8)!)
