#!/usr/bin/env python3
"""
Skill Security Scanner - Claude Code スキルの安全性を自動検査する

Usage:
    python3 skill_scanner.py <path>            # スキャンのみ
    python3 skill_scanner.py <path> --json      # JSON出力のみ
    python3 skill_scanner.py <path> --install   # スキャン → SAFEなら自動インストール

Exit codes:
    0 = SAFE (問題なし)
    1 = WARNING (要確認)
    2 = DANGER (インストール非推奨)
"""

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
import zipfile
from dataclasses import dataclass, field, asdict
from enum import IntEnum
from pathlib import Path
from typing import Optional


class Severity(IntEnum):
    INFO = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


SEVERITY_LABELS = {
    Severity.INFO: "INFO",
    Severity.LOW: "LOW",
    Severity.MEDIUM: "MEDIUM",
    Severity.HIGH: "HIGH",
    Severity.CRITICAL: "CRITICAL",
}

SEVERITY_ICONS = {
    Severity.INFO: "ℹ️",
    Severity.LOW: "🟡",
    Severity.MEDIUM: "🟠",
    Severity.HIGH: "🔴",
    Severity.CRITICAL: "🚨",
}


@dataclass
class Finding:
    category: str
    severity: int
    message: str
    file: str
    line: int
    matched_text: str
    in_code_block: bool = False

    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "severity": SEVERITY_LABELS[self.severity],
            "severity_level": self.severity,
            "message": self.message,
            "file": self.file,
            "line": self.line,
            "matched_text": self.matched_text,
            "in_code_block": self.in_code_block,
        }


@dataclass
class ScanResult:
    path: str
    file_count: int = 0
    total_lines: int = 0
    findings: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    verdict: str = "SAFE"

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "file_count": self.file_count,
            "total_lines": self.total_lines,
            "verdict": self.verdict,
            "summary": {
                "CRITICAL": sum(1 for f in self.findings if f.severity == Severity.CRITICAL),
                "HIGH": sum(1 for f in self.findings if f.severity == Severity.HIGH),
                "MEDIUM": sum(1 for f in self.findings if f.severity == Severity.MEDIUM),
                "LOW": sum(1 for f in self.findings if f.severity == Severity.LOW),
                "INFO": sum(1 for f in self.findings if f.severity == Severity.INFO),
            },
            "findings": [f.to_dict() for f in self.findings],
            "errors": self.errors,
        }


# ---------------------------------------------------------------------------
# 危険パターン定義（8カテゴリ）
# ---------------------------------------------------------------------------

PATTERNS: list[tuple[str, str, int, str]] = []


def _p(category: str, pattern: str, severity: int, message: str):
    PATTERNS.append((category, pattern, severity, message))


# 1. 認証情報の露出
_p("credential_exposure", r'(?:api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token)\s*[:=]\s*["\'][A-Za-z0-9_\-]{16,}["\']', Severity.CRITICAL, "APIキー/トークンがハードコードされています")
_p("credential_exposure", r'(?:password|passwd|pwd)\s*[:=]\s*["\'][^"\']{4,}["\']', Severity.HIGH, "パスワードがハードコードされています")
_p("credential_exposure", r'-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----', Severity.CRITICAL, "秘密鍵が含まれています")
_p("credential_exposure", r'(?:sk-|pk-|rk-)[A-Za-z0-9]{20,}', Severity.CRITICAL, "APIキー（sk-/pk-/rk-プレフィクス）が含まれています")
_p("credential_exposure", r'ghp_[A-Za-z0-9]{36}', Severity.CRITICAL, "GitHub Personal Access Tokenが含まれています")
_p("credential_exposure", r'xoxb-[0-9]{10,}-[A-Za-z0-9]{20,}', Severity.CRITICAL, "Slack Bot Tokenが含まれています")

# 2. 危険コマンド
_p("dangerous_command", r'\brm\s+-(?:[a-zA-Z]*r[a-zA-Z]*f|[a-zA-Z]*f[a-zA-Z]*r)[a-zA-Z]*\s', Severity.HIGH, "rm -rf コマンドが含まれています")
_p("dangerous_command", r'\bsudo\s+', Severity.MEDIUM, "sudo コマンドが含まれています")
_p("dangerous_command", r'\bcurl\b.*\|\s*(?:ba)?sh\b', Severity.CRITICAL, "リモートスクリプトのパイプ実行（curl|sh）")
_p("dangerous_command", r'\bwget\b.*\|\s*(?:ba)?sh\b', Severity.CRITICAL, "リモートスクリプトのパイプ実行（wget|sh）")
_p("dangerous_command", r'\beval\s*\(', Severity.HIGH, "eval() が使用されています")
_p("dangerous_command", r'\bexec\s*\(', Severity.MEDIUM, "exec() が使用されています")
_p("dangerous_command", r'\bDROP\s+(?:DATABASE|TABLE|SCHEMA)\b', Severity.CRITICAL, "DROP DATABASE/TABLE が含まれています")
_p("dangerous_command", r'\bos\.system\s*\(', Severity.HIGH, "os.system() が使用されています")
_p("dangerous_command", r'\bsubprocess\.(?:call|run|Popen)\s*\(.*shell\s*=\s*True', Severity.HIGH, "subprocess with shell=True が使用されています")
_p("dangerous_command", r'--no-verify', Severity.MEDIUM, "--no-verify フラグが使用されています")
_p("dangerous_command", r'\bgit\s+push\s+--force\b', Severity.HIGH, "git push --force が使用されています")
_p("dangerous_command", r'\bgit\s+reset\s+--hard\b', Severity.HIGH, "git reset --hard が使用されています")
_p("dangerous_command", r'\bchmod\s+777\b', Severity.HIGH, "chmod 777 が使用されています")
_p("dangerous_command", r'\bmkfs\b', Severity.CRITICAL, "mkfs（ファイルシステム作成）が含まれています")
_p("dangerous_command", r'\bdd\s+if=', Severity.HIGH, "dd コマンドが含まれています")

# 3. データ窃取
_p("data_exfiltration", r'(?:process\.env|os\.environ|ENV\[)', Severity.MEDIUM, "環境変数へのアクセス")
_p("data_exfiltration", r'(?:fetch|axios|requests?\.(?:get|post)|urllib|http\.request)\s*\(.*(?:env|token|key|secret|password|credential)', Severity.CRITICAL, "認証情報を含む外部リクエスト")
_p("data_exfiltration", r'(?:fetch|axios|requests?\.(?:get|post))\s*\([^)]*(?:ngrok|webhook\.site|requestbin|pipedream|burpcollaborator)', Severity.CRITICAL, "不審な外部エンドポイントへの送信")
_p("data_exfiltration", r'~/.ssh/', Severity.HIGH, "SSH鍵ディレクトリへのアクセス")
_p("data_exfiltration", r'~/.aws/', Severity.HIGH, "AWS認証ディレクトリへのアクセス")
_p("data_exfiltration", r'~/.claude/(?:settings|credentials|\.mcp)', Severity.CRITICAL, "Claude設定ファイルへのアクセス")
_p("data_exfiltration", r'(?:readFile|cat|type)\s+.*\.env\b', Severity.HIGH, ".env ファイルの読み取り")

# 4. パストラバーサル
_p("path_traversal", r'\.\.\/\.\.', Severity.HIGH, "パストラバーサル（../../）")
_p("path_traversal", r'/etc/(?:passwd|shadow|hosts)', Severity.CRITICAL, "システムファイルへのアクセス")
_p("path_traversal", r'~/.claude/(?:settings|CLAUDE)\.md', Severity.HIGH, "Claude設定ファイルの書き換え")
_p("path_traversal", r'~/.claude/\.mcp\.json', Severity.CRITICAL, "MCP設定ファイルへのアクセス")

# 5. 権限バイパス
_p("permission_bypass", r'dangerouslyDisableSandbox', Severity.CRITICAL, "サンドボックスの無効化")
_p("permission_bypass", r'bypassPermissions', Severity.CRITICAL, "権限バイパスの設定")
_p("permission_bypass", r'"mode"\s*:\s*"(?:bypassPermissions|dontAsk)"', Severity.HIGH, "権限チェックのバイパスモード")
_p("permission_bypass", r'allowedTools.*\*', Severity.MEDIUM, "全ツール許可のワイルドカード")

# 6. プロンプトインジェクション
_p("prompt_injection", r'(?:ignore|disregard|forget)\s+(?:all\s+)?(?:previous|prior|above)\s+(?:instructions?|rules?|constraints?)', Severity.CRITICAL, "プロンプトインジェクション: 以前の指示を無視")
_p("prompt_injection", r'(?:act|behave|operate)\s+(?:as if|without)\s+(?:no\s+)?(?:restrictions?|constraints?|limitations?|rules?)', Severity.CRITICAL, "プロンプトインジェクション: 制約なしで動作")
_p("prompt_injection", r'you\s+are\s+now\s+(?:DAN|jailbroken|unrestricted|unfiltered)', Severity.CRITICAL, "プロンプトインジェクション: ジェイルブレイク試行")
_p("prompt_injection", r'<system>.*?</system>', Severity.HIGH, "偽のsystemタグ")
_p("prompt_injection", r'system[\s_-]?prompt\s*[:=]', Severity.HIGH, "system prompt の上書き試行")
_p("prompt_injection", r'IMPORTANT:\s*(?:ignore|override|disregard)', Severity.CRITICAL, "偽の重要指示（IMPORTANT:）")

# 7. 難読化
_p("obfuscation", r'(?:atob|btoa|base64\.(?:b64decode|b64encode|decode))\s*\(', Severity.MEDIUM, "Base64エンコード/デコードの使用")
_p("obfuscation", r'\\x[0-9a-fA-F]{2}(?:\\x[0-9a-fA-F]{2}){3,}', Severity.HIGH, "Hexバイト列の使用")
_p("obfuscation", r'String\.fromCharCode\s*\(', Severity.HIGH, "String.fromCharCode の使用")
_p("obfuscation", r'(?:chr|ord)\s*\(\s*\d+\s*\)(?:\s*\+\s*(?:chr|ord)\s*\(\s*\d+\s*\)){3,}', Severity.HIGH, "文字コード連結による難読化")
_p("obfuscation", r'\\u[0-9a-fA-F]{4}(?:\\u[0-9a-fA-F]{4}){5,}', Severity.MEDIUM, "Unicodeエスケープの連続使用")

# 8. サプライチェーン
_p("supply_chain", r'pip\s+install\s+(?!-r\b)(?!--upgrade\b)\S+', Severity.LOW, "pip install の実行")
_p("supply_chain", r'npm\s+install\s+(?!--save-dev\b)(?!-D\b)\S+', Severity.LOW, "npm install の実行")
_p("supply_chain", r'(?:curl|wget)\s+.*\.(?:sh|py|js|rb)\b', Severity.HIGH, "リモートスクリプトのダウンロード")
_p("supply_chain", r'git\s+clone\s+', Severity.LOW, "git clone の実行")
_p("supply_chain", r'npx\s+\S+', Severity.MEDIUM, "npx によるパッケージ直接実行")


# コンパイル済みパターン
COMPILED_PATTERNS = [
    (cat, re.compile(pat, re.IGNORECASE), sev, msg)
    for cat, pat, sev, msg in PATTERNS
]

# ---------------------------------------------------------------------------
# Markdownコードブロック検出
# ---------------------------------------------------------------------------

CODE_BLOCK_FENCE = re.compile(r'^(`{3,}|~{3,})')


def build_code_block_map(lines: list[str]) -> set[int]:
    """コードブロック内の行番号セットを返す"""
    in_block = False
    fence_char = None
    fence_len = 0
    block_lines = set()

    for i, line in enumerate(lines):
        stripped = line.strip()
        m = CODE_BLOCK_FENCE.match(stripped)
        if m:
            char = m.group(1)[0]
            length = len(m.group(1))
            if not in_block:
                in_block = True
                fence_char = char
                fence_len = length
                block_lines.add(i)
            elif char == fence_char and length >= fence_len:
                block_lines.add(i)
                in_block = False
                fence_char = None
                fence_len = 0
            else:
                block_lines.add(i)
        elif in_block:
            block_lines.add(i)

    return block_lines


# ---------------------------------------------------------------------------
# スキャナー本体
# ---------------------------------------------------------------------------

# スキャン対象の拡張子
SCAN_EXTENSIONS = {
    ".md", ".txt", ".py", ".js", ".ts", ".jsx", ".tsx",
    ".sh", ".bash", ".zsh", ".fish",
    ".json", ".yaml", ".yml", ".toml",
    ".html", ".css", ".scss",
    ".rb", ".go", ".rs", ".java", ".php",
    ".env", ".cfg", ".ini", ".conf",
    "", # 拡張子なし（Makefile, Dockerfile等）
}

# 除外パターン
SKIP_DIRS = {
    "__pycache__", "node_modules", ".git", ".venv", "venv",
    ".mypy_cache", ".pytest_cache", "dist", "build",
}

MAX_ZIP_SIZE = 100 * 1024 * 1024  # 100MB


def should_scan_file(path: Path) -> bool:
    """スキャン対象かどうか判定"""
    if path.suffix.lower() in SCAN_EXTENSIONS:
        return True
    # 拡張子なしファイルの場合、名前で判定
    if path.suffix == "" and path.name in {
        "Makefile", "Dockerfile", "Vagrantfile", "Gemfile",
        "Rakefile", "Procfile", ".env",
    }:
        return True
    return False


def scan_file(filepath: Path, base_dir: Path) -> tuple[list[Finding], int]:
    """単一ファイルをスキャン"""
    findings = []
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except (PermissionError, OSError) as e:
        return [], 0

    lines = content.splitlines()
    line_count = len(lines)

    # Markdownファイルの場合、コードブロックマップを構築
    is_markdown = filepath.suffix.lower() in {".md", ".txt"}
    code_block_lines = build_code_block_map(lines) if is_markdown else set()

    rel_path = str(filepath.relative_to(base_dir))

    for i, line in enumerate(lines):
        for category, pattern, severity, message in COMPILED_PATTERNS:
            match = pattern.search(line)
            if match:
                in_code_block = i in code_block_lines
                actual_severity = severity

                # コードブロック内の検出はseverityを1段階下げる
                if in_code_block and actual_severity > Severity.INFO:
                    actual_severity = actual_severity - 1

                matched_text = match.group(0)
                # 長すぎるマッチは切り詰め
                if len(matched_text) > 120:
                    matched_text = matched_text[:117] + "..."

                findings.append(Finding(
                    category=category,
                    severity=actual_severity,
                    message=message,
                    file=rel_path,
                    line=i + 1,
                    matched_text=matched_text,
                    in_code_block=in_code_block,
                ))

    return findings, line_count


def scan_directory(dir_path: Path) -> ScanResult:
    """ディレクトリ全体をスキャン"""
    result = ScanResult(path=str(dir_path))

    for root, dirs, files in os.walk(dir_path):
        # 除外ディレクトリをスキップ
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for fname in files:
            fpath = Path(root) / fname
            if not should_scan_file(fpath):
                continue

            result.file_count += 1
            findings, line_count = scan_file(fpath, dir_path)
            result.total_lines += line_count
            result.findings.extend(findings)

    # 判定
    result.verdict = determine_verdict(result.findings)
    return result


def scan_zip(zip_path: Path) -> ScanResult:
    """ZIP/.skill ファイルをスキャン"""
    result = ScanResult(path=str(zip_path))

    # ZIPボム検出
    try:
        file_size = zip_path.stat().st_size
        if file_size > MAX_ZIP_SIZE:
            result.errors.append(f"ファイルサイズが上限（100MB）を超えています: {file_size / 1024 / 1024:.1f}MB")
            result.verdict = "DANGER"
            return result
    except OSError as e:
        result.errors.append(f"ファイルアクセスエラー: {e}")
        result.verdict = "DANGER"
        return result

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            # 展開後サイズチェック
            total_uncompressed = sum(info.file_size for info in zf.infolist())
            if total_uncompressed > MAX_ZIP_SIZE:
                result.errors.append(
                    f"ZIPボムの可能性: 展開後サイズ {total_uncompressed / 1024 / 1024:.1f}MB "
                    f"（圧縮率 {total_uncompressed / max(file_size, 1):.0f}x）"
                )
                result.verdict = "DANGER"
                return result

            # 一時ディレクトリに展開してスキャン
            with tempfile.TemporaryDirectory(prefix="skill_scan_") as tmpdir:
                zf.extractall(tmpdir)
                tmp_path = Path(tmpdir)
                dir_result = scan_directory(tmp_path)
                result.file_count = dir_result.file_count
                result.total_lines = dir_result.total_lines
                result.findings = dir_result.findings
                result.errors = dir_result.errors

    except zipfile.BadZipFile:
        result.errors.append("無効なZIPファイルです")
        result.verdict = "DANGER"
        return result
    except Exception as e:
        result.errors.append(f"ZIP展開エラー: {e}")
        result.verdict = "DANGER"
        return result

    result.verdict = determine_verdict(result.findings)
    return result


def determine_verdict(findings: list[Finding]) -> str:
    """検出結果から最終判定を返す"""
    if not findings:
        return "SAFE"

    max_severity = max(f.severity for f in findings)

    if max_severity >= Severity.HIGH:
        return "DANGER"
    elif max_severity >= Severity.MEDIUM:
        return "WARNING"
    elif max_severity >= Severity.LOW:
        # LOW が3件以上ある場合は WARNING
        low_count = sum(1 for f in findings if f.severity >= Severity.LOW)
        if low_count >= 3:
            return "WARNING"
        return "SAFE"
    else:
        return "SAFE"


# ---------------------------------------------------------------------------
# レポート出力
# ---------------------------------------------------------------------------

VERDICT_ICONS = {
    "SAFE": "✅",
    "WARNING": "⚠️",
    "DANGER": "🚨",
}


def format_report(result: ScanResult) -> str:
    """human-readable レポートを生成"""
    lines = []
    icon = VERDICT_ICONS.get(result.verdict, "❓")

    lines.append(f"{'=' * 60}")
    lines.append(f"  Skill Security Scanner - スキャン結果")
    lines.append(f"{'=' * 60}")
    lines.append(f"")
    lines.append(f"  対象: {result.path}")
    lines.append(f"  ファイル数: {result.file_count}")
    lines.append(f"  総行数: {result.total_lines}")
    lines.append(f"")
    lines.append(f"  判定: {icon} {result.verdict}")
    lines.append(f"")

    if result.errors:
        lines.append(f"  エラー:")
        for err in result.errors:
            lines.append(f"    ❌ {err}")
        lines.append(f"")

    d = result.to_dict()
    summary = d["summary"]
    lines.append(f"  検出サマリー:")
    lines.append(f"    🚨 CRITICAL: {summary['CRITICAL']}")
    lines.append(f"    🔴 HIGH:     {summary['HIGH']}")
    lines.append(f"    🟠 MEDIUM:   {summary['MEDIUM']}")
    lines.append(f"    🟡 LOW:      {summary['LOW']}")
    lines.append(f"    ℹ️  INFO:     {summary['INFO']}")
    lines.append(f"")

    if result.findings:
        lines.append(f"{'─' * 60}")
        lines.append(f"  検出詳細")
        lines.append(f"{'─' * 60}")
        lines.append(f"")

        # カテゴリでグループ化
        by_category: dict[str, list[Finding]] = {}
        for f in sorted(result.findings, key=lambda x: (-x.severity, x.category)):
            by_category.setdefault(f.category, []).append(f)

        category_labels = {
            "credential_exposure": "認証情報の露出",
            "dangerous_command": "危険コマンド",
            "data_exfiltration": "データ窃取",
            "path_traversal": "パストラバーサル",
            "permission_bypass": "権限バイパス",
            "prompt_injection": "プロンプトインジェクション",
            "obfuscation": "難読化",
            "supply_chain": "サプライチェーン",
        }

        for cat, cat_findings in by_category.items():
            label = category_labels.get(cat, cat)
            lines.append(f"  [{label}]")
            for f in cat_findings:
                sev_icon = SEVERITY_ICONS.get(f.severity, "❓")
                code_note = " (コードブロック内)" if f.in_code_block else ""
                lines.append(f"    {sev_icon} {SEVERITY_LABELS[f.severity]} | {f.file}:{f.line}")
                lines.append(f"       {f.message}{code_note}")
                lines.append(f"       → {f.matched_text}")
                lines.append(f"")
    else:
        lines.append(f"  検出なし - 既知の危険パターンは見つかりませんでした。")
        lines.append(f"")

    lines.append(f"{'=' * 60}")

    if result.verdict == "SAFE":
        lines.append(f"  自動スキャンでは問題は検出されませんでした。")
        lines.append(f"  ※ セマンティック分析（Claude）での追加確認を推奨します。")
    elif result.verdict == "WARNING":
        lines.append(f"  注意が必要な項目があります。")
        lines.append(f"  インストール前に検出項目を確認してください。")
    else:
        lines.append(f"  危険な項目が検出されました。")
        lines.append(f"  このスキルのインストールは推奨しません。")

    lines.append(f"{'=' * 60}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# インストール機能
# ---------------------------------------------------------------------------

SKILLS_DIR = Path.home() / ".claude" / "skills"


def resolve_skill_source(target: Path) -> tuple[Path, Optional[tempfile.TemporaryDirectory]]:
    """インストール元のディレクトリパスを返す。ZIPの場合は一時展開する。"""
    if target.is_file() and target.suffix in {".skill", ".zip"}:
        tmpdir = tempfile.TemporaryDirectory(prefix="skill_install_")
        with zipfile.ZipFile(target, "r") as zf:
            zf.extractall(tmpdir.name)
        return Path(tmpdir.name), tmpdir
    return target, None


def detect_skill_name(source_dir: Path) -> Optional[str]:
    """SKILL.md の YAML フロントマターから name を取得する。"""
    skill_md = source_dir / "SKILL.md"
    if not skill_md.exists():
        return None
    try:
        content = skill_md.read_text(encoding="utf-8", errors="replace")
        lines = content.splitlines()
        if lines and lines[0].strip() == "---":
            for line in lines[1:]:
                if line.strip() == "---":
                    break
                m = re.match(r'^name:\s*(.+)', line)
                if m:
                    return m.group(1).strip().strip('"').strip("'")
    except OSError:
        pass
    # フォールバック: ディレクトリ名を使用
    return source_dir.name if source_dir.name else None


def install_skill(source_dir: Path, skill_name: str) -> Path:
    """スキルを ~/.claude/skills/ にコピーする。"""
    dest = SKILLS_DIR / skill_name
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(
        source_dir,
        dest,
        ignore=shutil.ignore_patterns(".DS_Store", "__pycache__", "*.pyc"),
    )
    return dest


# ---------------------------------------------------------------------------
# メイン
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Claude Code スキルの安全性を検査する",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("path", help="スキャン対象のパス（ディレクトリまたは .skill/.zip）")
    parser.add_argument("--json", action="store_true", help="JSON出力のみ")
    parser.add_argument(
        "--install",
        action="store_true",
        help="スキャン後、SAFEの場合のみ ~/.claude/skills/ にインストール",
    )
    args = parser.parse_args()

    target = Path(args.path).expanduser().resolve()

    if not target.exists():
        print(f"エラー: パスが見つかりません: {target}", file=sys.stderr)
        sys.exit(2)

    if target.is_file() and target.suffix in {".skill", ".zip"}:
        result = scan_zip(target)
    elif target.is_dir():
        result = scan_directory(target)
    else:
        print(f"エラー: サポートされていない形式です: {target}", file=sys.stderr)
        sys.exit(2)

    if args.json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(format_report(result))
        # JSON も stderr に出力（Claude解析用）
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2), file=sys.stderr)

    # --install モード
    if args.install:
        if result.verdict == "SAFE":
            source_dir, tmpdir_obj = resolve_skill_source(target)
            try:
                skill_name = detect_skill_name(source_dir)
                if not skill_name:
                    print("エラー: SKILL.md が見つからない、またはスキル名を特定できません", file=sys.stderr)
                    sys.exit(2)
                dest = install_skill(source_dir, skill_name)
                print(f"\n✅ インストール完了: {dest}")
            finally:
                if tmpdir_obj:
                    tmpdir_obj.cleanup()
        elif result.verdict == "WARNING":
            print(f"\n⚠️  WARNING検出のためインストールを中断しました。")
            print(f"   検出内容を確認し、問題なければ手動でコピーしてください。")
        else:
            print(f"\n🚨 DANGER検出のためインストールを拒否しました。")
            print(f"   このスキルのインストールは推奨しません。")

    # 終了コード
    if result.verdict == "SAFE":
        sys.exit(0)
    elif result.verdict == "WARNING":
        sys.exit(1)
    elif result.verdict == "DANGER":
        sys.exit(2)


if __name__ == "__main__":
    main()
