// SpeechHelper.swift — Apple SpeechAnalyzer/SpeechTranscriber 래퍼
//
// 사용법:
//   SpeechHelper <audio-file> [--locale ko-KR] [--out result.json] [--verbose]
//   SpeechHelper --list-locales            # 설치/지원 로케일 진단
//
// stdout: JSON {"engine","locale","duration","segments":[{"start","end","text"}]}
//
// 빌드: ./build.sh   (swiftc -parse-as-library)

import Foundation
import Speech
import AVFoundation
import CoreMedia

struct Segment: Encodable {
    let start: Double
    let end: Double
    let text: String
}

struct Output: Encodable {
    let engine: String
    let locale: String
    let duration: Double
    let segments: [Segment]
}

struct Failure: Encodable {
    let engine: String
    let error: String
}

func emit(_ json: String) {
    FileHandle.standardOutput.write((json + "\n").data(using: .utf8)!)
}

func die(_ message: String, code: Int32 = 1) -> Never {
    let enc = JSONEncoder()
    enc.outputFormatting = [.withoutEscapingSlashes]
    if let data = try? enc.encode(Failure(engine: "apple-SpeechTranscriber", error: message)),
       let line = String(data: data, encoding: .utf8) {
        FileHandle.standardError.write((line + "\n").data(using: .utf8)!)
    } else {
        FileHandle.standardError.write((message + "\n").data(using: .utf8)!)
    }
    exit(code)
}

func listLocales() async {
    let supported = await SpeechTranscriber.supportedLocales
    let installed = await SpeechTranscriber.installedLocales
    let installedIds = Set(installed.map { $0.identifier(.bcp47) })
    print("supported(\(supported.count)): " + supported.map { $0.identifier(.bcp47) }.sorted().joined(separator: ", "))
    print("installed(\(installed.count)): " + installed.map { $0.identifier(.bcp47) }.sorted().joined(separator: ", "))
    let hasKo = supported.contains { $0.identifier(.bcp47).hasPrefix("ko") }
    print("ko supported: \(hasKo)")
    _ = installedIds
    exit(0)
}

@main
struct SpeechHelper {

    static func main() async {
        let args = Array(CommandLine.arguments.dropFirst())

        if args.contains("--list-locales") {
            await listLocales()
            return
        }

        var localeId = "ko-KR"
        var outPath: String? = nil
        var verbose = false
        var input: String? = nil

        var i = 0
        while i < args.count {
            let a = args[i]
            switch a {
            case "--locale":
                i += 1
                if i < args.count { localeId = args[i] }
            case "--out":
                i += 1
                if i < args.count { outPath = args[i] }
            case "--verbose":
                verbose = true
            default:
                if !a.hasPrefix("--") { input = a }
            }
            i += 1
        }

        guard let inputPath = input else {
            die("usage: SpeechHelper <audio-file> [--locale ko-KR] [--out path] [--verbose]", code: 2)
        }

        let url = URL(fileURLWithPath: inputPath)
        guard FileManager.default.fileExists(atPath: url.path) else {
            die("file not found: \(inputPath)")
        }

        func log(_ s: String) {
            if verbose { FileHandle.standardError.write((s + "\n").data(using: .utf8)!) }
        }

        // 1) 로케일 정규화
        let requested = Locale(identifier: localeId)
        guard let locale = await SpeechTranscriber.supportedLocale(equivalentTo: requested) else {
            die("locale not supported by SpeechTranscriber: \(localeId)")
        }
        let bcp47 = locale.identifier(.bcp47)
        log("locale=\(bcp47)")

        // 2) 언어 자산(모델) 준비
        let transcriber = SpeechTranscriber(
            locale: locale,
            preset: .timeIndexedTranscriptionWithAlternatives
        )

        let status = await AssetInventory.status(forModules: [transcriber])
        log("asset status=\(status)")
        if status != .installed {
            do {
                if let request = try await AssetInventory.assetInstallationRequest(supporting: [transcriber]) {
                    log("downloading language asset …")
                    try await request.downloadAndInstall()
                    log("asset installed")
                }
            } catch {
                die("asset install failed: \(error.localizedDescription)")
            }
        }

        // 3) 오디오 열기
        let audioFile: AVAudioFile
        do {
            audioFile = try AVAudioFile(forReading: url)
        } catch {
            die("cannot read audio: \(error.localizedDescription)")
        }
        let sampleRate = audioFile.processingFormat.sampleRate
        let frames = Double(audioFile.length)
        let duration = sampleRate > 0 ? frames / sampleRate : 0
        log("audio=\(audioFile.processingFormat) duration=\(duration)s")

        let analyzer = SpeechAnalyzer(
            modules: [transcriber],
            options: .init(priority: .userInitiated, modelRetention: .processLifetime)
        )

        // 4) 결과 수집 (analyzeSequence 호출 전에 시작해야 함)
        let collector = Task { () -> [Segment] in
            var segs: [Segment] = []
            var buf = ""
            var bufStart: Double = 0
            var bufEnd: Double = 0
            for try await result in transcriber.results {
                let text = String(result.text.characters)
                let start = CMTimeGetSeconds(result.range.start)
                let end = CMTimeGetSeconds(CMTimeRangeGetEnd(result.range))
                let trimmed = text.trimmingCharacters(in: .whitespacesAndNewlines)
                guard !trimmed.isEmpty else { continue }
                if buf.isEmpty {
                    buf = trimmed
                    bufStart = start
                    bufEnd = end
                } else if trimmed.hasPrefix(" ") || text.hasPrefix(" ") {
                    buf += trimmed
                    bufEnd = end
                } else {
                    buf += " " + trimmed
                    bufEnd = end
                }
                // 문장 종결 부호를 만나면 세그먼트로 확정
                if buf.hasSuffix(".") || buf.hasSuffix("?") || buf.hasSuffix("!") || buf.hasSuffix("다.") || buf.count > 120 {
                    segs.append(Segment(start: bufStart, end: bufEnd, text: buf))
                    buf = ""
                }
            }
            if !buf.isEmpty {
                segs.append(Segment(start: bufStart, end: bufEnd, text: buf))
            }
            return segs
        }

        // 5) 분석 실행
        do {
            if #available(macOS 26.0, *) {
                _ = try await analyzer.analyzeSequence(from: audioFile)
                try await analyzer.finalizeAndFinishThroughEndOfInput()
            } else {
                die("SpeechAnalyzer requires macOS 26+")
            }
        } catch {
            collector.cancel()
            die("analysis failed: \(error.localizedDescription)")
        }

        var segments: [Segment] = []
        do {
            segments = try await collector.value
        } catch {
            die("result collection failed: \(error.localizedDescription)")
        }

        // 6) 출력
        let out = Output(
            engine: "apple-SpeechTranscriber",
            locale: bcp47,
            duration: duration,
            segments: segments
        )
        let enc = JSONEncoder()
        enc.outputFormatting = [.withoutEscapingSlashes]
        guard let data = try? enc.encode(out), let json = String(data: data, encoding: .utf8) else {
            die("json encode failed")
        }

        if let outPath = outPath {
            do {
                try json.write(toFile: outPath, atomically: true, encoding: .utf8)
            } catch {
                die("cannot write \(outPath): \(error.localizedDescription)")
            }
        }
        emit(json)
    }
}
